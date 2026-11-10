"""Generador de contextos en Python (solo biblioteca estándar: http.server, urllib, dataclasses)."""
from __future__ import annotations

from .base import GeneradorBase

# rol -> paquete Python, según la arquitectura del contexto
LAYOUT_HEXAGONAL = {
    # Hexagonal (Cockburn): organizada POR LADO — dominio, puertos de entrada/salida, adaptadores de entrada/salida
    "modelo": "dominio.modelo", "eventos": "dominio.eventos", "bus": "dominio.eventos",
    "servicios": "dominio.servicios", "memento": "dominio.memento",
    "comandos": "puertos.entrada", "puertos": "puertos.salida",
    "api": "adaptadores.entrada",
    "persistencia": "adaptadores.salida.persistencia", "clientes": "adaptadores.salida.clientes",
    "transversal": "adaptadores.salida.transversal",
    "kernel": "shared_kernel", "contratos": "contratos",
}
LAYOUT_MICROSERVICIO = {
    # Microservicio con Clean Architecture: organizado POR CAPA — api, aplicacion, dominio, infraestructura, contratos
    "modelo": "dominio.modelo", "eventos": "dominio.eventos", "puertos": "dominio.puertos",
    "comandos": "aplicacion.comandos", "servicios": "aplicacion.servicios", "memento": "aplicacion.memento",
    "bus": "aplicacion.eventos",
    "api": "api",
    "persistencia": "infraestructura.persistencia", "clientes": "infraestructura.clientes",
    "transversal": "infraestructura.transversal",
    "kernel": "shared_kernel", "contratos": "contratos",
}


def tipo_py(t: str) -> str:
    return {"texto": "str", "entero": "int", "decimal": "float", "fecha": "date", "booleano": "bool"}[t]


class GeneradorPython(GeneradorBase):
    lenguaje = "python"
    LAYOUTS = {"hexagonal": LAYOUT_HEXAGONAL, "microservicios": LAYOUT_MICROSERVICIO}

    def _archivo(self, ctx, rol: str, modulo: str) -> str:
        return f"{ctx.carpeta}/{self.layout(ctx)[rol].replace('.', '/')}/{modulo}.py"

    def generar_contexto(self, ctx):
        L = self.layout(ctx)
        v = dict(ctx=ctx, L=L, tipo_py=tipo_py)
        f = lambda rol, mod: self._archivo(ctx, rol, mod)  # noqa: E731

        self.escribir(f("modelo", "errores"), "errores.py.j2", **v)
        for a in ctx.agregados:
            self.escribir(f("modelo", a.snake), "agregado.py.j2", [a.origen] + [c.origen for c in a.comandos], a=a, **v)
        self.escribir(f("modelo", "entidades"), "entidades.py.j2",
                      [e.origen for e in ctx.entidades if not e.compartida], **v)
        if any(e.compartida for e in ctx.entidades):
            self.escribir(f"{ctx.carpeta}/shared_kernel/__init__.py", "shared_kernel.py.j2",
                          [e.origen for e in ctx.entidades if e.compartida] +
                          [r.origen for r in ctx.proveedores + ctx.consumidores if r.patron == "shared-kernel"], **v)
        self.escribir(f("contratos", "eventos_v1"), "contratos_v1.py.j2",
                      [ev.origen for a in ctx.agregados for ev in a.eventos], **v)
        self.escribir(f("eventos", "eventos"), "eventos.py.j2",
                      [ev.origen for a in ctx.agregados for ev in a.eventos], **v)
        self.escribir(f("puertos", "repositorios"), "puertos_repositorios.py.j2", [a.origen for a in ctx.agregados], **v)
        self.escribir(f("puertos", "clientes"), "puertos_clientes.py.j2",
                      [r.origen for r in ctx.proveedores] + [i.origen for i in ctx.integraciones], **v)
        self.escribir(f("comandos", "comandos"), "comandos.py.j2",
                      [c.origen for a in ctx.agregados for c in a.comandos], **v)
        self.escribir(f("servicios", "servicios"), "servicios.py.j2",
                      [c.origen for c in ctx.componentes] + [x.origen for x in ctx.funciones], **v)
        self.escribir(f("memento", "memento"), "memento.py.j2", [a.origen for a in ctx.agregados], **v)
        self.escribir(f("persistencia", "memoria"), "repo_memoria.py.j2", [a.origen for a in ctx.agregados], **v)
        self.escribir(f("persistencia", "base_datos"), "repo_bd.py.j2", [a.origen for a in ctx.agregados], **v)
        self.escribir(f("persistencia", "cache"), "cache.py.j2", **v)
        self.escribir(f("clientes", "http"), "clientes_http.py.j2",
                      [r.origen for r in ctx.proveedores] + [i.origen for i in ctx.integraciones], **v)
        self.escribir(f("transversal", "cifrado"), "cifrado.py.j2", **v)
        self.escribir(f("bus", "bus_eventos"), "bus_eventos.py.j2", **v)
        self.escribir(f("api", "http"), "api_http.py.j2",
                      [c.origen for a in ctx.agregados for c in a.comandos] + [x.origen for x in ctx.funciones], **v)
        self.escribir(f"{ctx.carpeta}/main.py", "main.py.j2", self.origenes_contexto(ctx), **v)
        self.escribir(f"{ctx.carpeta}/requirements.txt", "requirements.txt.j2", **v)
        self.escribir(f"{ctx.carpeta}/Dockerfile", "Dockerfile.j2", [ctx.origen], **v)
        # __init__.py en cada paquete
        paquetes = set()
        for p in set(L.values()):
            partes = p.split(".")
            for i in range(1, len(partes) + 1):
                paquetes.add("/".join(partes[:i]))
        for p in sorted(paquetes):
            if p == "shared_kernel" and not any(e.compartida for e in ctx.entidades):
                continue
            destino = self.salida / ctx.carpeta / p / "__init__.py"
            if not destino.exists():
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text("", encoding="utf-8")
