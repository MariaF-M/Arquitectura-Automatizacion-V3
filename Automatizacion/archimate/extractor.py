"""Interpreta el modelo ArchiMate con reglas DDD y lo combina con spec.yaml.

Reglas de lectura (qué vista aporta qué):
  V5 Dominios ........ grupos «D-0X: Título (CLASIFICACIÓN)» con sus Application Component y Function
  V6 Agregados ....... Grouping «D-0X. ...» -> Data Object (raíz), Application Process (comando)
                       --Triggering--> Application Event (evento)
  V8 Mapa contextos .. Application Component internos/externos, Data Objects anidados (entidades)
                       y relaciones con el patrón DDD escrito como nombre de la relación
  V9 Interoperabilidad INT-xx --Flow--> ACL-01, con el objeto de negocio intercambiado (Access)
"""
from __future__ import annotations

import re

from .lector import ModeloArchimate, Vista
from .modelo import (Agregado, Anticorrupcion, Atributo, Comando, Componente, Contexto, Entidad,
                     Evento, Funcion, Integracion, RelacionContexto, Sistema, TIPOS_VALIDOS)
from . import nombres as n


class ErrorModelo(Exception):
    """El modelo o el spec tienen una inconsistencia que impide generar."""


_RE_DOMINIO = re.compile(r"(D-\d+)\s*[:.]\s*(.+?)\s*\((CORE|SUPPORTING|GENERIC)\w*\)", re.I)
_RE_INT = re.compile(r"^(INT-\d+)\.?\s*(.*)$")


def patron_de(etiqueta: str) -> str | None:
    e = n.sin_tildes(etiqueta).lower()
    if "customer" in e or "supplier" in e or "cliente" in e:
        return "customer-supplier"
    if "shared kernel" in e or "nucleo compartido" in e:
        return "shared-kernel"
    if "open host" in e:
        return "open-host-service"
    if "acl" in e or "anticorrup" in e:
        return "acl"
    if "conform" in e:
        return "conformista"
    if "published" in e or "lenguaje publicado" in e:
        return "published-language"
    return None


class Extractor:
    def __init__(self, modelo: ModeloArchimate, spec: dict):
        self.m = modelo
        self.spec = spec
        self.adv: list[str] = []
        self.traza: dict[str, dict] = {}
        vistas = spec["modelo"]["vistas"]
        self.v5 = modelo.vista(vistas["dominios"])
        self.v6 = modelo.vista(vistas["agregados"])
        self.v8 = modelo.vista(vistas["mapa_contextos"])
        self.v9 = modelo.vista(vistas["interoperabilidad"])

    # ------------------------------------------------------------------ util
    def _trazar(self, vista: Vista, elemento):
        self.traza.setdefault(elemento.id, {"vista": vista.nombre, "tipo": elemento.tipo,
                                            "nombre": elemento.nombre, "archivos": []})

    def _inventariar(self):
        """Registra todo elemento de la capa de aplicación de las vistas usadas, para que el
        reporte muestre también lo que NO se generó."""
        for vista in (self.v5, self.v6, self.v8, self.v9):
            for e in vista.elementos():
                if e.tipo.startswith("Application") or e.tipo in ("DataObject", "Grouping"):
                    self._trazar(vista, e)

    @staticmethod
    def _formatos(attrs, formatos: dict, no_negativos: list, donde: str) -> None:
        """Aplica las reglas de formato del spec a los atributos (y los valores por defecto)."""
        por_nombre = {a.nombre: a for a in attrs}
        for campo, regla in formatos.items():
            if campo not in por_nombre:
                raise ErrorModelo(f"{donde}: 'formatos' usa el atributo inexistente '{campo}'")
            at = por_nombre[campo]
            if "patron" in regla:
                try:
                    re.compile(regla["patron"])
                except re.error as e:
                    raise ErrorModelo(f"{donde}: el patrón de '{campo}' no es una expresión regular válida: {e}")
                if at.tipo != "texto":
                    raise ErrorModelo(f"{donde}: 'patron' solo aplica a atributos de texto ('{campo}' es {at.tipo})")
            at.patron = regla.get("patron")
            at.mensaje = regla.get("mensaje") or (f"no tiene el formato esperado ({at.patron})" if at.patron else None)
            at.minimo = regla.get("minimo")
            at.maximo = regla.get("maximo")
            at.max_largo = regla.get("max_largo")
        for at in attrs:
            if at.tipo == "texto" and at.max_largo is None:
                at.max_largo = 255                      # igual al VARCHAR(255) de la base de datos
            if at.nombre in no_negativos and at.minimo is None:
                at.minimo = 0

    @staticmethod
    def _texto(valor) -> str:
        """Una invariante escrita sin comillas con ':' llega de YAML como dict; se vuelve a texto."""
        if isinstance(valor, dict):
            return "; ".join(f"{k}: {v}" for k, v in valor.items())
        return str(valor)

    @staticmethod
    def _atributos(definicion: dict | None, donde: str) -> list[Atributo]:
        atributos = []
        for nombre, tipo in (definicion or {}).items():
            if tipo not in TIPOS_VALIDOS:
                raise ErrorModelo(f"{donde}: el atributo '{nombre}' tiene tipo '{tipo}'. Use uno de {sorted(TIPOS_VALIDOS)}")
            atributos.append(Atributo(nombre, tipo))
        return atributos

    # ------------------------------------------------------------------ V5
    def _dominios(self) -> dict:
        dominios = {}
        for nodo in self.v5.raiz:
            if nodo.elemento is not None:
                continue
            m = _RE_DOMINIO.search(nodo.etiqueta)
            if not m:
                continue
            codigo, titulo, clasif = m.group(1).upper(), m.group(2).strip(), m.group(3).upper()
            comps, funcs = [], []
            for h in nodo.recorrer():
                e = h.elemento
                if e and e.tipo == "ApplicationComponent":
                    comps.append(Componente(e.nombre, e.id))
                elif e and e.tipo == "ApplicationFunction":
                    funcs.append(Funcion(e.nombre, e.id))
            dominios[codigo] = {"titulo": titulo, "clasificacion": clasif, "componentes": comps, "funciones": funcs}
        if not dominios:
            raise ErrorModelo(f"La vista {self.v5.nombre} no tiene grupos con el formato 'D-0X: Título (CORE|SUPPORTING|GENERIC)'")
        return dominios

    # ------------------------------------------------------------------ V6
    def _agregados_por_dominio(self) -> dict:
        resultado = {}
        rels = self.v6.relaciones()
        for nodo in self.v6.nodos():
            g = nodo.elemento
            if not g or g.tipo != "Grouping":
                continue
            m = re.match(r"(D-\d+)", g.nombre)
            if not m:
                continue
            miembros = [h.elemento for h in nodo.recorrer() if h.elemento and h.elemento is not g]
            raices = [e for e in miembros if e.tipo == "DataObject"]
            procesos = [e for e in miembros if e.tipo == "ApplicationProcess"]
            eventos = {e.id: e for e in miembros if e.tipo == "ApplicationEvent"}
            agregados = []
            for raiz in raices:
                cmds, evs = [], []
                for p in procesos:
                    if not any(r.tipo == "Access" and r.origen == p.id and r.destino == raiz.id for r in rels):
                        continue
                    ev_ids = [r.destino for r in rels if r.tipo == "Triggering" and r.origen == p.id and r.destino in eventos]
                    ev = Evento(eventos[ev_ids[0]].nombre, ev_ids[0]) if ev_ids else None
                    if not ev:
                        self.adv.append(f"V6: el comando '{p.nombre}' no dispara ningún evento (falta relación Triggering).")
                    else:
                        evs.append(ev)
                    cmds.append(Comando(p.nombre, p.id, ev))
                if not cmds:
                    self.adv.append(f"V6: el agregado '{raiz.nombre}' no tiene comandos (falta Access desde un Application Process).")
                agregados.append({"elemento": raiz, "comandos": cmds, "eventos": evs})
            resultado[m.group(1).upper()] = {"grupo": g, "agregados": agregados}
        return resultado

    # ------------------------------------------------------------------ V8
    def _mapa_contextos(self, internos: set[str]):
        componentes, entidades, relaciones, acl_externos = {}, {}, [], {}
        for nodo in self.v8.raiz:
            e = nodo.elemento
            if not e or e.tipo != "ApplicationComponent":
                continue
            componentes[e.nombre] = e
            entidades[e.nombre] = [h.elemento for h in nodo.recorrer() if h.elemento and h.elemento.tipo == "DataObject"]
        faltantes = internos - set(componentes)
        if faltantes:
            raise ErrorModelo(f"spec.yaml declara contextos que no están en {self.v8.nombre}: {sorted(faltantes)}")
        for r in self.v8.relaciones():
            o, d = self.m.elementos[r.origen], self.m.elementos[r.destino]
            if o.tipo != "ApplicationComponent" or d.tipo != "ApplicationComponent":
                continue
            patron = patron_de(r.nombre)
            if patron is None:
                self.adv.append(f"V8: la relación {o.nombre} -> {d.nombre} no tiene patrón DDD en su nombre; se ignora.")
                continue
            if patron == "acl":
                if d.nombre not in internos:
                    raise ErrorModelo(f"V8: relación ACL hacia '{d.nombre}', que no es un contexto interno del spec")
                acl_externos[o.nombre] = (d.nombre, r, o.id)
                continue
            if o.nombre not in internos or d.nombre not in internos:
                self.adv.append(f"V8: relación {patron} entre '{o.nombre}' y '{d.nombre}' con un extremo externo; se ignora.")
                continue
            detalle = r.nombre.split(":")[-1].strip(" )") if patron == "shared-kernel" else ""
            relaciones.append(RelacionContexto(patron, r.nombre, o.nombre, d.nombre, r.id, detalle))
        return componentes, entidades, relaciones, acl_externos

    # ------------------------------------------------------------------ V9
    def _integraciones(self, acl_externos: dict, contextos: dict[str, Contexto], dominio_de_componente: dict):
        acl_spec = self.spec.get("anticorrupcion")
        if not acl_spec:
            return None
        acl = next((e for e in self.v9.elementos("ApplicationComponent") if e.nombre == acl_spec["componente"]), None)
        if not acl:
            raise ErrorModelo(f"No se encontró el componente '{acl_spec['componente']}' en {self.v9.nombre}")
        rels = self.v9.relaciones()
        interfaz = next((self.m.elementos[r.destino].nombre for r in rels
                         if r.origen == acl.id and self.m.elementos[r.destino].tipo == "ApplicationInterface"), "")
        # componentes internos a los que la ACL entrega información (Flow ACL -> componente)
        destinos_v9 = {self.m.elementos[r.destino].id for r in rels if r.origen == acl.id and r.tipo == "Flow"}
        spec_int = acl_spec.get("integraciones", {})
        integraciones = []
        for r in rels:
            if r.tipo != "Flow" or r.destino != acl.id:
                continue
            fuente = self.m.elementos[r.origen]
            m = _RE_INT.match(fuente.nombre)
            if not m:
                continue
            codigo, nombre = m.group(1), m.group(2).strip()
            obj = next((self.m.elementos[x.destino] for x in rels if x.origen == fuente.id and x.tipo == "Access"), None)
            # empareja el INT-xx de V9 con el sistema externo de V8 por similitud de nombre
            mejor, puntaje = None, 0
            for externo in acl_externos:
                p = len(n.raices(nombre) & n.raices(externo))
                if p > puntaje:
                    mejor, puntaje = externo, p
            if not mejor:
                raise ErrorModelo(f"V9: '{fuente.nombre}' no corresponde a ningún sistema externo con relación ACL en V8")
            contexto = acl_externos[mejor][0]
            # verificación cruzada V9 <-> V8: algún componente destino del Flow debe pertenecer a ese contexto
            dom = contextos[contexto].dominio
            if not any(dominio_de_componente.get(c) == dom for c in destinos_v9):
                self.adv.append(f"V9/V8: {codigo} llega a '{contexto}' según V8, pero en V9 la ACL no fluye a ningún componente de {dom}.")
            cfg = spec_int.get(codigo)
            if cfg is None:
                self.adv.append(f"spec: {codigo} ({nombre}) no tiene configuración; se genera solo el DTO y el traductor vacío.")
                cfg = {"direccion": "entrada", "mapeo": {}}
            ctx = contextos[contexto]
            comandos = {c.nombre: c for a in ctx.agregados for c in a.comandos}
            eventos = {c.evento.nombre for a in ctx.agregados for c in a.comandos if c.evento}
            if cfg.get("comando") and cfg["comando"] not in comandos:
                raise ErrorModelo(f"spec: {codigo} usa el comando '{cfg['comando']}', que no existe en el contexto '{contexto}' (V6). Comandos: {sorted(comandos)}")
            if cfg.get("evento") and cfg["evento"] not in eventos:
                raise ErrorModelo(f"spec: {codigo} usa el evento '{cfg['evento']}', que no existe en el contexto '{contexto}' (V6). Eventos: {sorted(eventos)}")
            integ = Integracion(codigo, nombre, fuente.id, obj.nombre if obj else nombre, obj.id if obj else "",
                                mejor, contexto, cfg.get("direccion", "entrada"), cfg.get("comando"),
                                cfg.get("evento"), cfg.get("mapeo", {}), acl_externos[mejor][2], acl_externos[mejor][1].id)
            integraciones.append(integ)
            ctx.integraciones.append(integ)
            self._trazar(self.v9, fuente)
            if obj:
                self._trazar(self.v9, obj)
        faltan = set(spec_int) - {i.codigo for i in integraciones}
        if faltan:
            raise ErrorModelo(f"spec: integraciones que no existen en {self.v9.nombre}: {sorted(faltan)}")
        integraciones.sort(key=lambda i: i.codigo)
        return Anticorrupcion(acl.nombre, acl.id, interfaz, acl_spec["lenguaje"], acl_spec["arquitectura"],
                              acl_spec["puerto"], integraciones)

    # ------------------------------------------------------------------ principal
    def extraer(self) -> Sistema:
        self._inventariar()
        spec_ctx = self.spec["contextos"]
        dominios = self._dominios()
        agregados_v6 = self._agregados_por_dominio()
        comp_v8, entidades_v8, relaciones, acl_externos = self._mapa_contextos(set(spec_ctx))

        dominio_de_componente = {c.origen: cod for cod, d in dominios.items() for c in d["componentes"]}
        contextos: dict[str, Contexto] = {}
        for nombre, cfg in spec_ctx.items():
            cod = cfg["dominio"].upper()
            if cod not in dominios:
                raise ErrorModelo(f"spec: el contexto '{nombre}' apunta al dominio {cod}, que no existe en {self.v5.nombre}. Hay: {sorted(dominios)}")
            if cfg["lenguaje"] not in ("python", "java", "csharp"):
                raise ErrorModelo(f"spec: lenguaje '{cfg['lenguaje']}' no soportado en '{nombre}' (python | java | csharp)")
            if cfg["arquitectura"] not in ("hexagonal", "microservicios"):
                raise ErrorModelo(f"spec: arquitectura '{cfg['arquitectura']}' no soportada en '{nombre}' (hexagonal | microservicios)")
            d = dominios[cod]
            ctx = Contexto(nombre, comp_v8[nombre].id, cod, d["titulo"], d["clasificacion"], cfg["lenguaje"],
                           cfg["arquitectura"], cfg["puerto"], cfg.get("base_datos", {}), cfg.get("cache", {}),
                           (cfg.get("cifrado") or {}).get("campos", []), d["componentes"], d["funciones"])

            # entidades (V8)
            spec_ent = cfg.get("entidades", {}) or {}
            vistos = set()
            for e in entidades_v8[nombre]:
                if e.nombre in vistos:
                    continue
                vistos.add(e.nombre)
                attrs = self._atributos(spec_ent.get(e.nombre), f"{nombre}/{e.nombre}") or [Atributo("descripcion", "texto")]
                ctx.entidades.append(Entidad(e.nombre, e.id, attrs))
            for sobrante in set(spec_ent) - vistos:
                raise ErrorModelo(f"spec: la entidad '{sobrante}' de '{nombre}' no está anidada en el componente en {self.v8.nombre}")

            # agregados (V6)
            spec_ag = cfg.get("agregados", {}) or {}
            info6 = agregados_v6.get(cod)
            if not info6:
                if spec_ag:
                    raise ErrorModelo(f"spec: '{nombre}' define agregados pero {cod} no tiene Grouping en {self.v6.nombre}")
                self.adv.append(f"V6: el dominio {cod} ({nombre}) no tiene agregados modelados; se generan solo entidades y servicios.")
            else:
                ctx.grupo_v6 = info6["grupo"].id
                for a in info6["agregados"]:
                    raiz = a["elemento"]
                    s = spec_ag.get(raiz.nombre)
                    if s is None:
                        self.adv.append(f"spec: el agregado '{raiz.nombre}' no tiene atributos definidos; se genera solo con id.")
                        s = {}
                    attrs = self._atributos(s.get("atributos"), f"{nombre}/{raiz.nombre}")
                    nombres_attr = {x.nombre for x in attrs}
                    self._formatos(attrs, s.get("formatos", {}) or {}, s.get("no_negativos", []), f"{nombre}/{raiz.nombre}")
                    for clave in ("obligatorios", "no_negativos", "unicos"):
                        malos = set(s.get(clave, [])) - nombres_attr
                        if malos:
                            raise ErrorModelo(f"spec: {raiz.nombre}.{clave} usa atributos inexistentes: {sorted(malos)}")
                    spec_cmd = s.get("comandos", {}) or {}
                    for c in a["comandos"]:
                        cc = spec_cmd.get(c.nombre, {})
                        c.crea = bool(cc.get("crea"))
                        c.restar = cc.get("restar")
                        c.nuevo_estado = cc.get("estado")
                        c.requiere = cc.get("requiere", [])
                        c.desde_estados = cc.get("desde_estados", [])
                        c.fecha_futura = cc.get("fecha_futura", [])
                        for campo in c.fecha_futura:
                            at = next((x for x in attrs if x.nombre == campo), None)
                            if not at or at.tipo != "fecha":
                                raise ErrorModelo(f"spec: '{c.nombre}' exige fecha futura en '{campo}', que no es un atributo de tipo fecha de {raiz.nombre}")
                        for campo in [c.restar] + c.requiere:
                            if campo and campo not in nombres_attr:
                                raise ErrorModelo(f"spec: el comando '{c.nombre}' usa el atributo '{campo}', que no existe en {raiz.nombre}")
                    sobran = set(spec_cmd) - {c.nombre for c in a["comandos"]}
                    if sobran:
                        raise ErrorModelo(f"spec: comandos de {raiz.nombre} que no existen en {self.v6.nombre}: {sorted(sobran)}")
                    if not any(c.crea for c in a["comandos"]) and a["comandos"]:
                        self.adv.append(f"spec: ningún comando crea '{raiz.nombre}'; se usará el primero ('{a['comandos'][0].nombre}').")
                        a["comandos"][0].crea = True
                    ctx.agregados.append(Agregado(raiz.nombre, raiz.id, attrs, a["comandos"], a["eventos"],
                                                  s.get("valores_iniciales", {}), s.get("obligatorios", []),
                                                  s.get("no_negativos", []), s.get("valores_permitidos", {}),
                                                  [self._texto(i) for i in s.get("invariantes", [])],
                                                  s.get("unicos", [])))
                for sobrante in set(spec_ag) - {a["elemento"].nombre for a in info6["agregados"]}:
                    raise ErrorModelo(f"spec: el agregado '{sobrante}' no existe en el grupo {cod} de {self.v6.nombre}")
            contextos[nombre] = ctx

        for r in relaciones:
            contextos[r.cliente].proveedores.append(r)
            contextos[r.proveedor].consumidores.append(r)
            if r.patron == "shared-kernel":
                for lado in (r.proveedor, r.cliente):
                    ent = next((e for e in contextos[lado].entidades if e.nombre == r.detalle), None)
                    if ent:
                        ent.compartida = True
                    else:
                        self.adv.append(f"V8: Shared Kernel '{r.detalle}' no aparece como Data Object dentro de '{lado}'.")

        acl = self._integraciones(acl_externos, contextos, dominio_de_componente)
        externos_sin_int = set(acl_externos) - {i.externo for i in (acl.integraciones if acl else [])}
        for e in externos_sin_int:
            self.adv.append(f"V8/V9: el sistema externo '{e}' tiene relación ACL en V8 pero ninguna integración INT-xx en V9.")

        return Sistema(self.spec["proyecto"]["nombre"], self.spec["proyecto"]["paquete_base"],
                       list(contextos.values()), acl, self.adv, self.traza)
