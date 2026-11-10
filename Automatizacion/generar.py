"""Generador de proyectos a partir del modelo ArchiMate (Opción V3).

Uso (desde cualquier carpeta):
    python Automatizacion/generar.py                       # usa Automatizacion/spec.yaml
    python Automatizacion/generar.py --spec otro.yaml --salida ./salida
    python Automatizacion/generar.py --validar             # solo valida modelo + spec, no genera

Pasos:
  1. Lee el .archimate (archimate/lector.py)
  2. Lo interpreta con reglas DDD y lo cruza con spec.yaml (archimate/extractor.py)
  3. Guarda el modelo intermedio en modelo_intermedio.json
  4. Genera cada contexto con el generador de su lenguaje (generadores/)
  5. Genera despliegue, contratos y el reporte de trazabilidad
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import yaml

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from archimate.extractor import ErrorModelo, Extractor  # noqa: E402
from archimate.lector import ModeloArchimate  # noqa: E402
from generadores import GENERADORES  # noqa: E402
from generadores.comun import GeneradorComun  # noqa: E402
from generadores.frontend_gen import GeneradorFrontend  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Genera el código de las aplicaciones desde el modelo ArchiMate")
    p.add_argument("--spec", default=str(AQUI / "spec.yaml"))
    p.add_argument("--salida", default=str(AQUI.parent / "Codigo_generado"))
    p.add_argument("--validar", action="store_true", help="solo valida, no escribe archivos")
    args = p.parse_args(argv)

    ruta_spec = Path(args.spec).resolve()
    spec = yaml.safe_load(ruta_spec.read_text(encoding="utf-8"))
    ruta_modelo = (ruta_spec.parent / spec["modelo"]["archivo"]).resolve()
    print(f"Modelo : {ruta_modelo.name}")
    print(f"Spec   : {ruta_spec.name}")

    try:
        modelo = ModeloArchimate(ruta_modelo)
        sistema = Extractor(modelo, spec).extraer()
    except (ErrorModelo, KeyError) as error:
        print(f"\n[ERROR] {error}")
        return 1

    for a in sistema.advertencias:
        print(f"[AVISO] {a}")
    if args.validar:
        print("\nModelo y spec válidos.")
        return 0

    salida = Path(args.salida).resolve()
    if salida.exists():
        if not (salida / "TRAZABILIDAD.md").exists() and any(salida.iterdir()):
            print(f"[ERROR] {salida} existe y no parece generada por esta herramienta; no se borra.")
            return 1
        shutil.rmtree(salida)
    salida.mkdir(parents=True)

    print()
    for ctx in sistema.contextos:
        GENERADORES[ctx.lenguaje](sistema, salida).generar_contexto(ctx)
        print(f" [OK] {ctx.nombre:<26} {ctx.dominio} {ctx.clasificacion:<10} -> {ctx.lenguaje:<6} {ctx.arquitectura:<14} :{ctx.puerto}")
    if sistema.acl:
        GENERADORES[sistema.acl.lenguaje](sistema, salida).generar_acl(sistema.acl)
        print(f" [OK] {'ACL-01 Anticorrupción':<26} {len(sistema.acl.integraciones)} integraciones -> {sistema.acl.lenguaje:<6} {sistema.acl.arquitectura:<14} :{sistema.acl.puerto}")

    frontend = None
    if spec.get("frontend", {}).get("generar", True):
        frontend = GeneradorFrontend(sistema, salida).generar()
        print(f" [OK] {'Frontend':<26} shell + {len(frontend.remotos)} microfrontends -> React + TypeScript + Module Federation :{frontend.shell.puerto}")

    comun = GeneradorComun(sistema, salida, spec, ruta_modelo, frontend)
    comun.generar()
    (salida / "modelo_intermedio.json").write_text(
        json.dumps(sistema.a_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    t = comun.resumen_traza
    print(f"\nTrazabilidad: {t['generados']}/{t['total']} elementos de la capa de aplicación generaron código "
          f"({t['porcentaje']:.0f} %). Ver {salida.name}/TRAZABILIDAD.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
