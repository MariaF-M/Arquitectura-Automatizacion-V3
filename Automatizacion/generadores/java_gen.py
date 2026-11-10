"""Generador de contextos y de la ACL en Java 17 (solo JDK: com.sun.net.httpserver, java.net.http)."""
from __future__ import annotations

from archimate import nombres as n
from .base import GeneradorBase

LAYOUT_HEXAGONAL = {
    # Hexagonal (Cockburn): organizada POR LADO — dominio, puertos de entrada/salida, adaptadores de entrada/salida
    "modelo": "dominio.modelo", "eventos": "dominio.eventos", "bus": "dominio.eventos",
    "servicios": "dominio.servicios", "memento": "dominio.memento",
    "comandos": "puertos.entrada", "puertos": "puertos.salida",
    "api": "adaptadores.entrada",
    "persistencia": "adaptadores.salida.persistencia", "clientes": "adaptadores.salida.clientes",
    "transversal": "adaptadores.salida.transversal",
    "kernel": "sharedkernel", "contratos": "contratos",
}
LAYOUT_MICROSERVICIO = {
    # Microservicio con Clean Architecture: organizado POR CAPA — api, aplicacion, dominio, infraestructura, contratos
    "modelo": "dominio.modelo", "eventos": "dominio.eventos", "puertos": "dominio.puertos",
    "comandos": "aplicacion.comandos", "servicios": "aplicacion.servicios", "memento": "aplicacion.memento",
    "bus": "aplicacion.eventos",
    "api": "api",
    "persistencia": "infraestructura.persistencia", "clientes": "infraestructura.clientes",
    "transversal": "infraestructura.transversal",
    "kernel": "sharedkernel", "contratos": "contratos",
}
# La ACL tiene su propio layout hexagonal: el "dominio" de la ACL son los traductores
LAYOUT_ACL = {
    "dto": "dominio.dto", "traductores": "dominio.traductores", "puertos": "dominio.puertos",
    "servicios": "aplicacion", "api": "infraestructura.api", "adaptadores": "infraestructura.adaptadores",
    "transversal": "infraestructura.transversal",
}


def tipo_java(t: str) -> str:
    return {"texto": "String", "entero": "Integer", "decimal": "Double", "fecha": "LocalDate", "booleano": "Boolean"}[t]


class GeneradorJava(GeneradorBase):
    lenguaje = "java"
    LAYOUTS = {"hexagonal": LAYOUT_HEXAGONAL, "microservicios": LAYOUT_MICROSERVICIO}

    def _paquetes(self, base: str, layout: dict) -> dict:
        return {rol: f"{base}.{p}" for rol, p in layout.items()} | {"base": base}

    def _ruta(self, carpeta: str, paquete: str, clase: str) -> str:
        return f"{carpeta}/src/main/java/{paquete.replace('.', '/')}/{clase}.java"

    def generar_contexto(self, ctx):
        base = f"{self.sistema.paquete_base}.{ctx.paquete}"
        P = self._paquetes(base, self.layout(ctx))
        v = dict(ctx=ctx, P=P, tipo_java=tipo_java)
        w = lambda rol, clase, plantilla, origenes=(), **extra: self.escribir(  # noqa: E731
            self._ruta(ctx.carpeta, P[rol], clase), plantilla, list(origenes), clase=clase, **v, **extra)

        w("transversal", "Json", "Json.java.j2", paquete=P["transversal"])
        w("transversal", "Cifrador", "Cifrador.java.j2")
        w("bus", "BusEventos", "BusEventos.java.j2")
        w("modelo", "ReglaNegocioException", "Excepcion.java.j2", paquete=P["modelo"], doc="Se viola una invariante del agregado.")
        w("modelo", "NoEncontradoException", "Excepcion.java.j2", paquete=P["modelo"], doc="El agregado solicitado no existe.")
        w("eventos", "EventoDominio", "EventoDominio.java.j2")
        w("servicios", "CasoDeUsoPendienteException", "Excepcion.java.j2", paquete=P["servicios"],
          doc="La función existe en el diagrama pero su lógica aún no se implementa.")
        w("memento", "Caretaker", "Caretaker.java.j2", [a.origen for a in ctx.agregados])
        w("clientes", "ClienteHttp", "ClienteHttp.java.j2")

        for a in ctx.agregados:
            w("modelo", a.clase, "Agregado.java.j2", [a.origen] + [c.origen for c in a.comandos], a=a)
            w("modelo", a.clase + "Memento", "Memento.java.j2", [a.origen], a=a)
            for ev in a.eventos:
                w("eventos", ev.clase, "Evento.java.j2", [ev.origen], ev=ev, a=a)
                w("contratos", ev.clase + "V1", "ContratoV1.java.j2", [ev.origen], ev=ev, a=a)
            for c in a.comandos:
                w("comandos", c.clase, "Comando.java.j2", [c.origen], c=c, a=a)
            w("comandos", "Manejador" + a.clase, "Manejador.java.j2", [c.origen for c in a.comandos], a=a)
            w("puertos", "Repositorio" + a.clase, "PuertoRepositorio.java.j2", [a.origen], a=a)
            w("persistencia", f"Repositorio{a.clase}Memoria", "RepoMemoria.java.j2", [a.origen], a=a)
            w("persistencia", f"Repositorio{a.clase}BaseDatos", "RepoBd.java.j2", [a.origen], a=a)
            w("persistencia", f"Repositorio{a.clase}Cache", "RepoCache.java.j2", [a.origen], a=a)

        for e in ctx.entidades:
            rol = "kernel" if e.compartida else "modelo"
            orig = [e.origen] + ([r.origen for r in ctx.proveedores + ctx.consumidores if r.patron == "shared-kernel"] if e.compartida else [])
            w(rol, e.clase, "Entidad.java.j2", orig, e=e, paquete=P[rol])

        for r in ctx.proveedores:
            w("puertos", "Puerto" + n.pascal(r.proveedor), "PuertoCliente.java.j2", [r.origen], r=r)
            w("clientes", f"Cliente{n.pascal(r.proveedor)}Http", "ClienteContexto.java.j2", [r.origen], r=r)
        if ctx.integraciones:
            w("puertos", "PuertoAnticorrupcion", "PuertoAnticorrupcion.java.j2", [i.origen for i in ctx.integraciones])
            w("clientes", "ClienteAnticorrupcionHttp", "ClienteAnticorrupcion.java.j2", [i.origen for i in ctx.integraciones])

        for f in ctx.funciones:
            w("servicios", f.clase, "Funcion.java.j2", [f.origen], f=f)
        for c in ctx.componentes:
            w("servicios", c.clase + "Servicio", "Componente.java.j2", [c.origen], c=c)

        w("api", "ServidorHttp", "ServidorHttp.java.j2",
          [c.origen for a in ctx.agregados for c in a.comandos] + [f.origen for f in ctx.funciones])
        self.escribir(self._ruta(ctx.carpeta, base, "Main"), "Main.java.j2", self.origenes_contexto(ctx), **v)
        self.escribir(f"{ctx.carpeta}/pom.xml", "pom.xml.j2", [ctx.origen], artefacto=ctx.carpeta, principal=f"{base}.Main", **v)
        self.escribir(f"{ctx.carpeta}/Dockerfile", "Dockerfile.j2", [ctx.origen], artefacto=ctx.carpeta,
                      principal=f"{base}.Main", puerto=ctx.puerto)

    # ------------------------------------------------------------------ ACL (V9)
    def _destino(self, i) -> dict:
        """A dónde entrega la ACL una integración de entrada: URL del contexto y ruta del comando."""
        ctx = self.sistema.contexto(i.contexto)
        d = {"variable": ctx.variable_url, "url": f"http://localhost:{ctx.puerto}", "ruta": "", "crea": False}
        for a in ctx.agregados:
            for c in a.comandos:
                if c.nombre == i.comando:
                    d.update(ruta=f"/{a.recurso}/{c.ruta}" if c.crea else f"/{a.recurso}/{{id}}/{c.ruta}", crea=c.crea)
        return d

    def generar_acl(self, acl):
        base = f"{self.sistema.paquete_base}.{acl.paquete}"
        P = {rol: f"{base}.{p}" for rol, p in LAYOUT_ACL.items()} | {"base": base}
        v = dict(acl=acl, P=P)
        w = lambda rol, clase, plantilla, origenes=(), **extra: self.escribir(  # noqa: E731
            self._ruta(acl.carpeta, P[rol], clase), plantilla, list(origenes), clase=clase, **v, **extra)

        w("transversal", "Json", "Json.java.j2", paquete=P["transversal"])
        w("adaptadores", "ClienteHttp", "acl/ClienteHttp.java.j2")
        w("traductores", "Traductor", "acl/Traductor.java.j2")
        for i in acl.integraciones:
            orig = [i.origen, i.objeto_origen, i.externo_origen, i.relacion_v8]
            w("dto", i.dto, "acl/Dto.java.j2", orig, i=i)
            w("traductores", "Traductor" + i.clase, "acl/TraductorIntegracion.java.j2", orig, i=i, d=self._destino(i))
        w("puertos", "PuertoContextoInterno", "acl/PuertoContextoInterno.java.j2")
        w("puertos", "PuertoSistemaExterno", "acl/PuertoSistemaExterno.java.j2")
        w("adaptadores", "AdaptadorContextoHttp", "acl/AdaptadorContextoHttp.java.j2",
          [i.origen for i in acl.integraciones])
        w("adaptadores", "AdaptadorSistemaExternoHttp", "acl/AdaptadorSistemaExternoHttp.java.j2",
          [i.externo_origen for i in acl.integraciones])
        w("servicios", "ServicioIntegracion", "acl/ServicioIntegracion.java.j2", [acl.origen])
        interfaz = [k for k, t in self.sistema.traza.items() if t["nombre"] == acl.interfaz]
        w("api", "ServidorHttp", "acl/ServidorHttp.java.j2", [acl.origen] + interfaz + [i.origen for i in acl.integraciones])
        self.escribir(self._ruta(acl.carpeta, base, "Main"), "acl/Main.java.j2", [acl.origen], **v)
        self.escribir(f"{acl.carpeta}/pom.xml", "pom.xml.j2", [acl.origen], artefacto=acl.carpeta, principal=f"{base}.Main", P=P)
        self.escribir(f"{acl.carpeta}/Dockerfile", "Dockerfile.j2", [acl.origen], artefacto=acl.carpeta,
                      principal=f"{base}.Main", puerto=acl.puerto)
