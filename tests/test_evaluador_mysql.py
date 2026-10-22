"""Controles negativos del evaluador contra MySQL real. Se omite si las bases no están disponibles."""
import unittest

from evaluacion.comparar import categoria_error_mysql, comparar_resultados
from evaluacion.evaluar import ejecutar_sql
from scripts.comun import DATOS, conectar, leer_jsonl


class EvaluadorMySQL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.conexion = conectar()
            with cls.conexion.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME LIKE 'val\\_%'")
                if cursor.fetchone()[0] < 2:
                    raise unittest.SkipTest('Bases de validación no importadas')
        except unittest.SkipTest:
            raise
        except Exception as exc:  # sin servidor local
            raise unittest.SkipTest(f'MySQL no disponible: {exc}')
        cls.pares = {p['id']: p for p in leer_jsonl(DATOS / 'validacion' / 'pares.jsonl')}

    @classmethod
    def tearDownClass(cls):
        cls.conexion.close()

    def evaluar(self, id_, sql):
        par = self.pares[id_]
        ref = ejecutar_sql(self.conexion, par['esquema_id'], par['sql'])
        pred = ejecutar_sql(self.conexion, par['esquema_id'], sql)
        if not pred['ok']:
            return False, categoria_error_mysql(pred['codigo'])
        ok, _, motivo = comparar_resultados(par['columnas_esperadas'], ref['filas'], pred['columnas'],
                                            pred['filas'], par['requiere_orden'])
        return ok, motivo

    def test_columna_adicional_y_alias(self):
        sql = f"SELECT 99 AS extra, q.* FROM ({self.pares['propia_27']['sql']}) q"
        self.assertEqual(self.evaluar('propia_27', sql), (True, 'ok'))

    def test_distinct_pierde_duplicados(self):
        sql = f"SELECT DISTINCT q.* FROM ({self.pares['propia_21']['sql']}) q"
        self.assertFalse(self.evaluar('propia_21', sql)[0])

    def test_orden_exigido(self):
        # Las cinco filas empatan en cantidad; se invierte por título para alterar solo el orden.
        sql = f"SELECT * FROM ({self.pares['propia_08']['sql']}) q ORDER BY q.titulo DESC"
        self.assertEqual(self.evaluar('propia_08', sql), (False, 'orden distinto'))

    def test_orden_no_exigido(self):
        sql = f"SELECT * FROM ({self.pares['propia_27']['sql']}) q ORDER BY 3 DESC, 1 DESC"
        self.assertTrue(self.evaluar('propia_27', sql)[0])

    def test_errores_categorizados(self):
        self.assertEqual(self.evaluar('propia_21', 'SELECT nombre_completo FROM pacientes'),
                         (False, 'columna_tabla_inexistente'))
        self.assertEqual(self.evaluar('propia_21', 'SELEC nombre FROM pacientes'), (False, 'sintaxis'))


if __name__ == '__main__':
    unittest.main()
