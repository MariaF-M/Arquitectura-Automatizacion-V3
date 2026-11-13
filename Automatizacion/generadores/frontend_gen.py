"""Generador del frontend: una aplicación contenedora (shell) + un microfrontend por contexto delimitado
+ un microfrontend de integraciones (V9). React 19 + TypeScript + Vite + Module Federation 2.0.

Cada microfrontend lleva un `src/contexto.json` derivado del modelo (agregados, comandos, atributos,
invariantes, funciones...). El código React es genérico y se arma con ese descriptor, así la interfaz
cambia sola cuando cambia el diagrama.
"""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from archimate import nombres as n
from .base import GeneradorBase, PLANTILLAS

ESTATICO = PLANTILLAS / "frontend" / "estatico"
PUERTO_SHELL = 5100


@dataclass
class AppFrontend:
    nombre: str        # nombre visible
    carpeta: str       # mf-inventario
    federado: str      # mf_inventario (nombre Module Federation)
    puerto: int
    origen: str = ""   # id del elemento del diagrama
    clasificacion: str = ""
    dominio: str = ""


@dataclass
class Frontend:
    shell: AppFrontend
    remotos: list[AppFrontend]


class GeneradorFrontend(GeneradorBase):
    lenguaje = "frontend"

    def __init__(self, sistema, salida: Path):
        super().__init__(sistema, salida)
        remotos, puerto = [], PUERTO_SHELL + 1
        for ctx in sistema.contextos:
            remotos.append(AppFrontend(ctx.nombre, f"mf-{ctx.carpeta}", f"mf_{ctx.snake}", puerto,
                                       ctx.origen, ctx.clasificacion, ctx.dominio))
            puerto += 1
        if sistema.acl:
            remotos.append(AppFrontend("Integraciones", "mf-integraciones", "mf_integraciones", puerto,
                                       sistema.acl.origen, "ACL", "V9"))
        self.frontend = Frontend(AppFrontend("Shell", "shell", "shell", PUERTO_SHELL), remotos)

    def generar_contexto(self, ctx):  # no aplica: se genera todo junto
        raise NotImplementedError

    # --------------------------------------------------------------- descriptores (modelo -> JSON)
    @staticmethod
    def _descriptor_contexto(ctx) -> dict:
        def atributos(a):
            cifrados = {n.snake(c) for c in ctx.cifrado}
            return [{"nombre": at.snake, "etiqueta": at.nombre.replace("_", " ").capitalize(), "tipo": at.tipo,
                     "obligatorio": at.nombre in a.obligatorios, "noNegativo": at.nombre in a.no_negativos,
                     "opciones": a.valores_permitidos.get(at.nombre), "cifrado": at.snake in cifrados,
                     "inicial": a.valores_iniciales.get(at.nombre),
                     "patron": at.patron, "mensaje": at.mensaje, "minimo": at.minimo, "maximo": at.maximo,
                     "maxLargo": at.max_largo} for at in a.atributos]

        return {
            "tipo": "contexto", "nombre": ctx.nombre, "carpeta": ctx.carpeta, "puerto": ctx.puerto,
            "dominio": ctx.dominio, "tituloDominio": ctx.titulo_dominio, "clasificacion": ctx.clasificacion,
            "lenguaje": {"python": "Python", "java": "Java", "csharp": "C#"}[ctx.lenguaje],
            "arquitectura": ctx.arquitectura,
            "baseDatos": f"{ctx.base_datos.get('tipo', '')} · {ctx.base_datos.get('motor', '')}",
            "agregados": [{
                "nombre": a.nombre, "recurso": a.recurso, "atributos": atributos(a), "invariantes": a.invariantes,
                "comandos": [{"nombre": c.nombre, "ruta": c.ruta, "crea": c.crea,
                              "evento": c.evento.nombre if c.evento else None,
                              "restar": n.snake(c.restar) if c.restar else None,
                              "estado": c.nuevo_estado, "requiere": [n.snake(r) for r in c.requiere],
                              "desdeEstados": c.desde_estados,
                              "fechaFutura": [n.snake(f) for f in c.fecha_futura],
                              "minimos": {n.snake(k): v for k, v in c.minimos.items()}} for c in a.comandos],
            } for a in ctx.agregados],
            "funciones": [{"nombre": f.nombre, "ruta": f.ruta} for f in ctx.funciones],
            "componentes": [c.nombre for c in ctx.componentes],
            "entidades": [e.nombre for e in ctx.entidades],
            "relaciones": [{"con": r.proveedor, "patron": r.etiqueta, "sentido": "consume"} for r in ctx.proveedores]
                          + [{"con": r.cliente, "patron": r.etiqueta, "sentido": "provee"} for r in ctx.consumidores],
        }

    def _descriptor_integraciones(self) -> dict:
        acl = self.sistema.acl
        integraciones = []
        for i in acl.integraciones:
            ctx = self.sistema.contexto(i.contexto)
            recurso = next((a.recurso for a in ctx.agregados for c in a.comandos
                            if c.nombre in (i.comando, ) or (c.evento and c.evento.nombre == i.evento)), None)
            campos = list(i.mapeo.keys())
            integraciones.append({
                "codigo": i.codigo, "ruta": i.ruta, "nombre": i.nombre, "externo": i.externo, "objeto": i.objeto,
                "direccion": i.direccion, "contexto": i.contexto, "carpetaContexto": ctx.carpeta,
                "puertoContexto": ctx.puerto, "recursoContexto": recurso,
                "comando": i.comando, "evento": i.evento, "campos": campos,
                "campoId": next((k for k, v in i.mapeo.items() if v == "id"), None),
                "mapeo": i.mapeo})
        return {"tipo": "integraciones", "nombre": "Integraciones (ACL-01)", "carpeta": acl.carpeta,
                "puerto": acl.puerto, "interfaz": acl.interfaz, "integraciones": integraciones}

    # --------------------------------------------------------------- escritura
    def _copiar(self, origen: Path, destino: Path, origenes: list[str]):
        for archivo in origen.rglob("*"):
            if archivo.is_file():
                rel = archivo.relative_to(origen)
                d = destino / rel
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(archivo, d)
                ruta = d.relative_to(self.salida.parent).as_posix()
                for o in origenes:
                    self.sistema.registrar(o, ruta)

    def _json(self, relativo: str, datos: dict, origenes: list[str]):
        d = self.salida / relativo
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for o in origenes:
            self.sistema.registrar(o, d.relative_to(self.salida.parent).as_posix())

    def generar(self) -> Frontend:
        fe = self.frontend
        base = "frontend"
        for mf in fe.remotos:
            if mf.carpeta == "mf-integraciones":
                desc = self._descriptor_integraciones()
                origenes = [self.sistema.acl.origen] + [i.origen for i in self.sistema.acl.integraciones]
                api = {"carpeta": self.sistema.acl.carpeta, "puerto": self.sistema.acl.puerto}
            else:
                ctx = self.sistema.contexto(mf.nombre)
                desc = self._descriptor_contexto(ctx)
                origenes = ([ctx.origen] + [a.origen for a in ctx.agregados] +
                            [c.origen for a in ctx.agregados for c in a.comandos] +
                            [f.origen for f in ctx.funciones])
                api = {"carpeta": ctx.carpeta, "puerto": ctx.puerto}
            d = f"{base}/{mf.carpeta}"
            self._copiar(ESTATICO / "remoto", self.salida / d, [])
            self._json(f"{d}/src/contexto.json", desc, origenes)
            v = dict(mf=mf, fe=fe, api=api)
            self.escribir(f"{d}/package.json", "remoto/package.json.j2", **v)
            self.escribir(f"{d}/vite.config.ts", "remoto/vite.config.ts.j2", [mf.origen], **v)
            self.escribir(f"{d}/index.html", "remoto/index.html.j2", **v)
            self.escribir(f"{d}/Dockerfile", "Dockerfile.j2", **v)
            self.escribir(f"{d}/nginx.conf", "nginx-estatico.conf.j2", **v)

        d = f"{base}/shell"
        self._copiar(ESTATICO / "shell", self.salida / d, [])
        v = dict(fe=fe)
        self.escribir(f"{d}/package.json", "shell/package.json.j2", **v)
        self.escribir(f"{d}/vite.config.ts", "shell/vite.config.ts.j2", [m.origen for m in fe.remotos], **v)
        self.escribir(f"{d}/src/remotos.ts", "shell/remotos.ts.j2", [m.origen for m in fe.remotos], **v)
        self.escribir(f"{d}/src/tipos-remotos.d.ts", "shell/remotos.d.ts.j2", **v)
        self.escribir(f"{d}/index.html", "shell/index.html.j2", **v)
        self.escribir(f"{d}/Dockerfile", "Dockerfile.j2", mf=fe.shell, fe=fe, api=None)
        self.escribir(f"{d}/nginx.conf", "nginx-estatico.conf.j2", **v)
        self.escribir(f"{base}/package.json", "package.json.j2", **v)
        self.escribir(f"{base}/README.md", "README.md.j2", **v)
        return fe
