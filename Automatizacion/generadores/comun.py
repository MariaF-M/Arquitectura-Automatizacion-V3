"""Artefactos que no dependen del lenguaje: despliegue, esquemas de BD, contratos y trazabilidad."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .base import GeneradorBase


def rutas_contexto(ctx) -> list[dict]:
    rutas = [{"metodo": "GET", "ruta": "/salud", "que": "estado del servicio"},
             {"metodo": "GET", "ruta": "/eventos", "que": "eventos de dominio publicados"},
             {"metodo": "GET", "ruta": "/arquitectura", "que": "componentes, funciones y caché"}]
    for a in ctx.agregados:
        rutas.append({"metodo": "GET", "ruta": f"/{a.recurso}", "que": f"lista de {a.nombre}"})
        rutas.append({"metodo": "GET", "ruta": f"/{a.recurso}/{{id}}", "que": f"un {a.nombre}"})
        for c in a.comandos:
            r = f"/{a.recurso}/{c.ruta}" if c.crea else f"/{a.recurso}/{{id}}/{c.ruta}"
            ev = f" → evento «{c.evento.nombre}»" if c.evento else ""
            rutas.append({"metodo": "POST", "ruta": r, "que": f"comando «{c.nombre}»{ev}", "cuerpo": a.clase})
        rutas.append({"metodo": "POST", "ruta": f"/{a.recurso}/{{id}}/deshacer", "que": "deshace el último comando (memento)"})
    for f in ctx.funciones:
        rutas.append({"metodo": "POST", "ruta": f"/funciones/{f.ruta}", "que": f"función «{f.nombre}» (pendiente, 501)"})
    return rutas


def rutas_acl(acl) -> list[dict]:
    rutas = [{"metodo": "GET", "ruta": "/salud", "que": "estado del servicio"},
             {"metodo": "GET", "ruta": "/integraciones", "que": "catálogo de integraciones INT-xx"}]
    for i in acl.integraciones:
        sentido = "entrantes" if i.direccion == "entrada" else "salientes"
        destino = f"comando «{i.comando}» en {i.contexto}" if i.direccion == "entrada" else f"{i.externo}"
        rutas.append({"metodo": "POST", "ruta": f"/{sentido}/{i.ruta}",
                      "que": f"{i.codigo} {i.nombre}: traduce «{i.objeto}» → {destino}", "cuerpo": i.dto})
    return rutas


class GeneradorComun(GeneradorBase):
    lenguaje = "comun"

    def __init__(self, sistema, salida: Path, spec: dict, ruta_modelo: Path, frontend=None):
        super().__init__(sistema, salida)
        self.frontend = frontend
        self.spec = spec
        self.ruta_modelo = ruta_modelo
        self.resumen_traza = {}

    def generar_contexto(self, ctx):  # no aplica
        raise NotImplementedError

    def generar(self):
        s = self.sistema
        for ctx in s.contextos:
            rutas = rutas_contexto(ctx)
            sql = ctx.base_datos.get("tipo", "SQL").upper() == "SQL"
            if ctx.agregados:
                self.escribir(f"{ctx.carpeta}/db/{'esquema.sql' if sql else 'colecciones.json'}",
                              "esquema.sql.j2" if sql else "colecciones.json.j2", [a.origen for a in ctx.agregados], ctx=ctx)
            self.escribir(f"contratos/{ctx.carpeta}.openapi.json", "openapi.json.j2",
                          [c.origen for c in ctx.componentes], ctx=ctx, rutas=rutas, titulo=ctx.nombre, puerto=ctx.puerto)
            self.escribir(f"{ctx.carpeta}/README.md", "README_servicio.md.j2", [ctx.origen, ctx.grupo_v6], ctx=ctx, rutas=rutas)
        kernels = {(r.detalle, r.origen) for c in s.contextos for r in c.proveedores if r.patron == "shared-kernel"}
        for detalle, origen in kernels:
            ent = next(e for c in s.contextos for e in c.entidades if e.compartida and e.nombre == detalle)
            ids = [origen] + [e.origen for c in s.contextos for e in c.entidades if e.compartida and e.nombre == detalle]
            self.escribir(f"contratos/shared-kernel/{ent.snake}.schema.json", "shared_kernel.schema.json.j2", ids, ent=ent)
        if s.acl:
            self.escribir("contratos/acl-01-anticorrupcion.openapi.json", "openapi.json.j2", [s.acl.origen],
                          ctx=None, rutas=rutas_acl(s.acl), titulo=s.acl.nombre, puerto=s.acl.puerto)
            self.escribir(f"{s.acl.carpeta}/README.md", "README_acl.md.j2", [s.acl.origen], acl=s.acl, rutas=rutas_acl(s.acl))
        self.escribir("docker-compose.yml", "docker-compose.yml.j2", [], spec=self.spec, frontend=self.frontend)
        self.escribir("gateway/nginx.conf", "gateway.conf.j2", [c.origen for c in s.contextos] + ([s.acl.origen] if s.acl else []))
        if any(c.base_datos.get("tipo", "").upper() == "SQL" for c in s.contextos):
            self.escribir("bd/postgres/01-crear-bases.sql", "crear_bases.sql.j2", [])
        self.escribir("README.md", "README_raiz.md.j2", [], modelo=self.ruta_modelo.name)
        self._trazabilidad()

    def _trazabilidad(self):
        filas = sorted(self.sistema.traza.values(), key=lambda f: (f["vista"], f["tipo"], f["nombre"]))
        # Elementos sin archivos que son el mismo elemento ya generado bajo otra vista no existen (traza por id),
        # así que cada fila es un elemento único del diagrama.
        generados = [f for f in filas if f["archivos"]]
        total = len(filas)
        self.resumen_traza = {"total": total, "generados": len(generados),
                              "porcentaje": 100 * len(generados) / total if total else 100}
        self.escribir("TRAZABILIDAD.md", "TRAZABILIDAD.md.j2", [], filas=filas, resumen=self.resumen_traza,
                      fecha=datetime.now().strftime("%Y-%m-%d %H:%M"), modelo=self.ruta_modelo.name)
        (self.salida / "trazabilidad.json").write_text(json.dumps(filas, ensure_ascii=False, indent=2), encoding="utf-8")
