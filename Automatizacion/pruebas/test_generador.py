"""Pruebas del generador.  Ejecutar desde la raíz del repo:

    python -m unittest discover -s Automatizacion/pruebas -v
"""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

AUTOMATIZACION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AUTOMATIZACION))

from archimate.extractor import ErrorModelo, Extractor  # noqa: E402
from archimate.lector import ModeloArchimate  # noqa: E402
import generar  # noqa: E402

SPEC = yaml.safe_load((AUTOMATIZACION / "spec.yaml").read_text(encoding="utf-8"))
MODELO = ModeloArchimate((AUTOMATIZACION / SPEC["modelo"]["archivo"]).resolve())


def extraer(spec=None):
    return Extractor(MODELO, spec or copy.deepcopy(SPEC)).extraer()


class LecturaDelModelo(unittest.TestCase):
    def test_contextos_y_clasificacion_salen_de_v5_y_v8(self):
        s = extraer()
        clasif = {c.nombre: (c.dominio, c.clasificacion) for c in s.contextos}
        self.assertEqual(clasif["Inventario"], ("D-01", "CORE"))
        self.assertEqual(clasif["Vencimientos"], ("D-02", "CORE"))
        self.assertEqual(clasif["Abastecimiento"], ("D-04", "SUPPORTING"))
        self.assertEqual(clasif["Seguridad y Auditoría"], ("D-05", "GENERIC"))

    def test_agregados_comandos_y_eventos_salen_de_v6(self):
        inv = extraer().contexto("Inventario")
        a = inv.agregados[0]
        self.assertEqual(a.nombre, "LoteMedicamento")
        self.assertEqual({c.nombre: c.evento.nombre for c in a.comandos},
                         {"Registrar Ingreso": "Lote Ingresado", "Descontar Existencias": "Existencias Descontadas"})

    def test_patrones_de_v8(self):
        s = extraer()
        patrones = {(r.proveedor, r.cliente, r.patron) for c in s.contextos for r in c.proveedores}
        self.assertIn(("Inventario", "Abastecimiento", "customer-supplier"), patrones)
        self.assertIn(("Inventario", "Vencimientos", "shared-kernel"), patrones)
        self.assertIn(("Seguridad y Auditoría", "Inventario", "open-host-service"), patrones)

    def test_integraciones_de_v9_se_emparejan_con_v8(self):
        destinos = {i.codigo: (i.externo, i.contexto) for i in extraer().acl.integraciones}
        self.assertEqual(destinos["INT-04"], ("Sistema ERP (Compras)", "Abastecimiento"))
        self.assertEqual(destinos["INT-06"], ("INVIMA (Vigilancia)", "Vencimientos"))
        self.assertEqual(len(destinos), 6)


class ValidacionDelSpec(unittest.TestCase):
    def _falla(self, cambio, texto):
        spec = copy.deepcopy(SPEC)
        cambio(spec)
        with self.assertRaises(ErrorModelo) as e:
            extraer(spec)
        self.assertIn(texto, str(e.exception))

    def test_comando_que_no_esta_en_el_diagrama(self):
        self._falla(lambda s: s["contextos"]["Inventario"]["agregados"]["LoteMedicamento"]["comandos"]
                    .update({"Inventar Comando": {}}), "Inventar Comando")

    def test_contexto_que_no_esta_en_v8(self):
        self._falla(lambda s: s["contextos"].update({"Facturación": SPEC["contextos"]["Inventario"]}), "Facturación")

    def test_integracion_con_comando_de_otro_contexto(self):
        self._falla(lambda s: s["anticorrupcion"]["integraciones"]["INT-06"].update(comando="Registrar Ingreso"), "INT-06")


class Generacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.salida = Path(cls.tmp.name) / "Codigo_generado"
        assert generar.main(["--salida", str(cls.salida)]) == 0

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_trazabilidad_completa(self):
        filas = json.loads((self.salida / "trazabilidad.json").read_text(encoding="utf-8"))
        sin_codigo = [f["nombre"] for f in filas if not f["archivos"]]
        self.assertEqual(sin_codigo, [])

    def test_un_servicio_por_contexto_mas_la_acl(self):
        carpetas = {p.name for p in self.salida.iterdir() if p.is_dir()}
        self.assertTrue({"inventario", "vencimientos", "planificacion-de-demanda", "abastecimiento",
                         "seguridad-y-auditoria", "acl-01-anticorrupcion", "contratos"} <= carpetas)

    def test_invariantes_memento_y_cifrado_en_el_codigo_generado(self):
        script = (
            "import main\n"
            "from puertos.entrada.comandos import RegistrarIngreso, DescontarExistencias\n"
            "from dominio.modelo.errores import ReglaNegocioError\n"
            "app = main.construir_app(); m = app.manejadores['lote-medicamento']\n"
            "r = m.manejar_registrar_ingreso(RegistrarIngreso({'codigo':'1001','descripcion':'Amoxicilina','proveedor':'Genfar',"
            "'fecha_vencimiento':'2030-01-01','registro_sanitario':'INVIMA 2024M-01','cantidad':10}))\n"
            "m.manejar_descontar_existencias(DescontarExistencias({'cantidad':4}, r['id']))\n"
            "try:\n    m.manejar_descontar_existencias(DescontarExistencias({'cantidad':99}, r['id'])); raise SystemExit('no validó')\n"
            "except ReglaNegocioError: pass\n"
            "assert m.obtener(r['id'])['cantidad'] == 6\n"
            "for malo in [{'codigo':'ABC'}, {'cantidad':'diez'}, {'cantidad':2.5}, {'fecha_vencimiento':'31/12/2027'}, {'codigo':'   '}]:\n"
            "    datos = {'codigo':'123','descripcion':'Amoxicilina','proveedor':'Genfar','fecha_vencimiento':'2030-01-01',"
            "'registro_sanitario':'INVIMA 2024M-01','cantidad':1} | malo\n"
            "    try:\n        m.manejar_registrar_ingreso(RegistrarIngreso(datos)); raise SystemExit(f'aceptó {malo}')\n"
            "    except ReglaNegocioError: pass\n"
            "try:\n    m.manejar_descontar_existencias(DescontarExistencias({'cantidad':-5}, r['id'])); raise SystemExit('restó negativo')\n"
            "except ReglaNegocioError: pass\n"
            "try:\n    m.manejar_registrar_ingreso(RegistrarIngreso({'codigo':'1001','descripcion':'Otra','proveedor':'Genfar',"
            "'fecha_vencimiento':'2030-01-01','registro_sanitario':'INVIMA 2024M-01','cantidad':1})); raise SystemExit('aceptó código repetido')\n"
            "except ReglaNegocioError: pass\n"
            "try:\n    m.manejar_registrar_ingreso(RegistrarIngreso({'codigo':'1002','descripcion':'Amoxicilina','proveedor':'Genfar',"
            "'fecha_vencimiento':'2020-01-01','registro_sanitario':'INVIMA 2024M-01','cantidad':1})); raise SystemExit('aceptó lote vencido')\n"
            "except ReglaNegocioError: pass\n"
            "assert m.deshacer(r['id'])['cantidad'] == 10\n"
            "assert app.caches['lote-medicamento']._repo._datos[r['id']]['proveedor'].startswith('enc:')\n"
            "assert app.bus.historial[0]['agregado_id'] and app.bus.historial[0]['contrato'] == 'LoteIngresadoV1'\n"
            "print('ok')\n")
        res = subprocess.run([sys.executable, "-c", script], cwd=self.salida / "inventario",
                             capture_output=True, text=True)
        self.assertEqual(res.stdout.strip(), "ok", res.stderr)

    def test_estructura_segun_la_arquitectura(self):
        """Hexagonal: por lado (puertos/adaptadores de entrada y salida). Microservicio: Clean por capa + contratos."""
        for carpeta in ("dominio", "puertos/entrada", "puertos/salida", "adaptadores/entrada", "adaptadores/salida", "contratos"):
            self.assertTrue((self.salida / "inventario" / carpeta).is_dir(), carpeta)
        for carpeta in ("api", "aplicacion", "dominio", "infraestructura", "contratos"):
            self.assertTrue((self.salida / "planificacion-de-demanda" / carpeta).is_dir(), carpeta)
        self.assertIn("class LoteIngresadoV1", (self.salida / "inventario/contratos/eventos_v1.py").read_text(encoding="utf-8"))

    def test_regla_de_dependencias(self):
        """Las dependencias apuntan hacia adentro: el dominio y los puertos nunca importan adaptadores ni infraestructura."""
        violaciones = []
        revisar = [("inventario", ("dominio", "puertos"), "adaptadores", "py"),
                   ("abastecimiento", ("Dominio", "Puertos"), "Adaptadores", "cs"),
                   ("planificacion-de-demanda", ("dominio", "aplicacion"), "infraestructura", "py"),
                   ("vencimientos/src", ("main/java/co/edu/farmacia/vencimientos/dominio",), "infraestructura", "java")]
        for ctx, capas, prohibido, ext in revisar:
            for capa in capas:
                for f in (self.salida / ctx / capa).rglob(f"*.{ext}"):
                    if f"{prohibido}." in f.read_text(encoding="utf-8") or f"{prohibido}/" in f.read_text(encoding="utf-8"):
                        violaciones.append(str(f.relative_to(self.salida)))
        self.assertEqual(violaciones, [])

    def test_adaptadores_de_bd_segun_spec(self):
        inv = (self.salida / "inventario/adaptadores/salida/persistencia/base_datos.py").read_text(encoding="utf-8")
        plan = (self.salida / "planificacion-de-demanda/infraestructura/persistencia/base_datos.py").read_text(encoding="utf-8")
        self.assertIn("import psycopg", inv)                     # Inventario: SQL
        self.assertIn("CREATE TABLE IF NOT EXISTS lote_medicamento", inv)
        self.assertIn("CHECK (cantidad >= 0)", inv)              # invariante también en la BD
        self.assertIn("from pymongo import MongoClient", plan)   # Planificación: NoSQL
        self.assertIn("mongodb-driver-legacy", (self.salida / "vencimientos/pom.xml").read_text(encoding="utf-8"))
        self.assertIn('Include="Npgsql"', (self.salida / "abastecimiento/Abastecimiento.csproj").read_text(encoding="utf-8"))

    def test_despliegue_con_gateway_y_bases(self):
        compose = yaml.safe_load((self.salida / "docker-compose.yml").read_text(encoding="utf-8"))
        servicios = compose["services"]
        self.assertTrue({"gateway", "postgres", "mongo", "shell", "mf-inventario", "mf-integraciones"} <= set(servicios))
        self.assertEqual(servicios["inventario"]["environment"]["PERSISTENCIA"], "bd")
        self.assertIn("location /api/abastecimiento/", (self.salida / "gateway/nginx.conf").read_text(encoding="utf-8"))

    def test_microfrontends_generados_desde_el_modelo(self):
        desc = json.loads((self.salida / "frontend/mf-inventario/src/contexto.json").read_text(encoding="utf-8"))
        self.assertEqual(desc["clasificacion"], "CORE")
        lote = desc["agregados"][0]
        self.assertEqual(lote["nombre"], "LoteMedicamento")
        self.assertEqual([c["nombre"] for c in lote["comandos"]], ["Registrar Ingreso", "Descontar Existencias"])
        integ = json.loads((self.salida / "frontend/mf-integraciones/src/contexto.json").read_text(encoding="utf-8"))
        self.assertEqual(len(integ["integraciones"]), 6)
        remotos = (self.salida / "frontend/shell/src/remotos.ts").read_text(encoding="utf-8")
        self.assertEqual(remotos.count("lazy(() => import("), 6)


@unittest.skipUnless(os.getenv("PRUEBAS_POSTGRES_URL"), "defina PRUEBAS_POSTGRES_URL=postgresql://usuario:clave@host:5432/base")
class PersistenciaPostgres(unittest.TestCase):
    """Integración real: el adaptador SQL generado guarda, cifra y relee en PostgreSQL."""

    def test_guardar_y_leer(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "Codigo_generado"
            generar.main(["--salida", str(salida)])
            script = (
                "import os, psycopg\n"
                "from adaptadores.salida.persistencia.base_datos import RepositorioLoteMedicamentoBaseDatos\n"
                "from adaptadores.salida.transversal.cifrado import Cifrador\n"
                "from dominio.modelo.lote_medicamento import LoteMedicamento\n"
                "url = os.environ['PRUEBAS_POSTGRES_URL']\n"
                "repo = RepositorioLoteMedicamentoBaseDatos(Cifrador(), url)\n"
                "a = LoteMedicamento.registrar_ingreso({'codigo':'5001','descripcion':'Amoxicilina','proveedor':'Secreto',"
                "'fecha_vencimiento':'2030-01-01','registro_sanitario':'INVIMA 2024M-01','cantidad':3})\n"
                "repo.guardar(a)\n"
                "assert repo.obtener(a.id).proveedor == 'Secreto'\n"
                "crudo = psycopg.connect(url).execute('select proveedor from lote_medicamento where id=%s',(a.id,)).fetchone()[0]\n"
                "assert crudo.startswith('enc:'), crudo\n"
                "print('ok')\n")
            res = subprocess.run([sys.executable, "-c", script], cwd=salida / "inventario", capture_output=True, text=True)
            self.assertEqual(res.stdout.strip(), "ok", res.stderr)


if __name__ == "__main__":
    unittest.main()
