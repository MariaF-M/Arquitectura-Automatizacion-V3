"""Generador de contextos en C# / .NET 8 (ASP.NET Core Minimal API, sin paquetes NuGet externos)."""
from __future__ import annotations

from archimate import nombres as n
from .base import GeneradorBase

LAYOUT_HEXAGONAL = {
    # Hexagonal: por lado
    "modelo": "Dominio/Modelo", "eventos": "Dominio/Eventos", "bus": "Dominio/Eventos",
    "servicios": "Dominio/Servicios", "memento": "Dominio/Memento",
    "comandos": "Puertos/Entrada", "puertos": "Puertos/Salida",
    "api": "Adaptadores/Entrada",
    "persistencia": "Adaptadores/Salida/Persistencia", "clientes": "Adaptadores/Salida/Clientes",
    "transversal": "Adaptadores/Salida/Transversal",
    "kernel": "SharedKernel", "contratos": "Contratos",
}
LAYOUT_MICROSERVICIO = {
    # Clean Architecture: por capa
    "modelo": "Dominio/Modelo", "eventos": "Dominio/Eventos", "puertos": "Dominio/Puertos",
    "comandos": "Aplicacion/Comandos", "servicios": "Aplicacion/Servicios", "memento": "Aplicacion/Memento",
    "bus": "Aplicacion/Eventos",
    "api": "Api",
    "persistencia": "Infraestructura/Persistencia", "clientes": "Infraestructura/Clientes",
    "transversal": "Infraestructura/Transversal",
    "kernel": "SharedKernel", "contratos": "Contratos",
}


def tipo_cs(t: str) -> str:
    return {"texto": "string", "entero": "int", "decimal": "double", "fecha": "DateOnly", "booleano": "bool"}[t]


class GeneradorCSharp(GeneradorBase):
    lenguaje = "csharp"
    LAYOUTS = {"hexagonal": LAYOUT_HEXAGONAL, "microservicios": LAYOUT_MICROSERVICIO}

    def generar_contexto(self, ctx):
        raiz = ".".join(n.pascal(p) for p in self.sistema.paquete_base.split(".")) + "." + ctx.clase
        L = self.layout(ctx)
        N = {rol: raiz + "." + carpeta.replace("/", ".") for rol, carpeta in L.items()} | {"base": raiz}
        v = dict(ctx=ctx, N=N, tipo_cs=tipo_cs)
        f = lambda rol, archivo: f"{ctx.carpeta}/{L[rol]}/{archivo}.cs"  # noqa: E731
        ags = [a.origen for a in ctx.agregados]
        cmds = [c.origen for a in ctx.agregados for c in a.comandos]

        self.escribir(f("modelo", "Errores"), "Errores.cs.j2", **v)
        for a in ctx.agregados:
            self.escribir(f("modelo", a.clase), "Agregado.cs.j2", [a.origen] + [c.origen for c in a.comandos], a=a, **v)
        self.escribir(f("modelo", "Entidades"), "Entidades.cs.j2", [e.origen for e in ctx.entidades if not e.compartida], **v)
        if any(e.compartida for e in ctx.entidades):
            self.escribir(f("kernel", "SharedKernel"), "SharedKernel.cs.j2",
                          [e.origen for e in ctx.entidades if e.compartida] +
                          [r.origen for r in ctx.proveedores + ctx.consumidores if r.patron == "shared-kernel"], **v)
        self.escribir(f("contratos", "EventosV1"), "ContratosV1.cs.j2", [e.origen for a in ctx.agregados for e in a.eventos], **v)
        self.escribir(f("eventos", "Eventos"), "Eventos.cs.j2", [e.origen for a in ctx.agregados for e in a.eventos], **v)
        self.escribir(f("puertos", "Repositorios"), "PuertosRepositorios.cs.j2", ags, **v)
        self.escribir(f("puertos", "Clientes"), "PuertosClientes.cs.j2",
                      [r.origen for r in ctx.proveedores] + [i.origen for i in ctx.integraciones], **v)
        self.escribir(f("comandos", "Comandos"), "Comandos.cs.j2", cmds, **v)
        self.escribir(f("servicios", "Servicios"), "Servicios.cs.j2",
                      [c.origen for c in ctx.componentes] + [x.origen for x in ctx.funciones], **v)
        self.escribir(f("memento", "Caretaker"), "Caretaker.cs.j2", ags, **v)
        self.escribir(f("persistencia", "RepositoriosMemoria"), "RepoMemoria.cs.j2", ags, **v)
        self.escribir(f("persistencia", "RepositoriosBaseDatos"), "RepoBd.cs.j2", ags, **v)
        self.escribir(f("persistencia", "Cache"), "Cache.cs.j2", ags, **v)
        self.escribir(f("clientes", "ClientesHttp"), "ClientesHttp.cs.j2",
                      [r.origen for r in ctx.proveedores] + [i.origen for i in ctx.integraciones], **v)
        self.escribir(f("transversal", "Cifrador"), "Cifrador.cs.j2", **v)
        self.escribir(f("bus", "BusEventos"), "BusEventos.cs.j2", **v)
        self.escribir(f("transversal", "Valores"), "Valores.cs.j2", **v)
        self.escribir(f("modelo", "Conversion"), "Conversion.cs.j2", **v)
        self.escribir(f("api", "Rutas"), "Rutas.cs.j2", cmds + [x.origen for x in ctx.funciones], **v)
        self.escribir(f"{ctx.carpeta}/Program.cs", "Program.cs.j2", self.origenes_contexto(ctx), **v)
        self.escribir(f"{ctx.carpeta}/{ctx.clase}.csproj", "csproj.j2", [ctx.origen], **v)
        self.escribir(f"{ctx.carpeta}/Dockerfile", "Dockerfile.j2", [ctx.origen], **v)
