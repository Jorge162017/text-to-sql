"""La consolidación cubre todos los fallos con la regla de clasificación y reproduce los pesos de cada resumen."""
import json
import unittest

from evaluacion.consolidar import CATEGORIAS, CONFIGURACIONES, POR_CODIGO, filas_configuracion
from scripts.comun import ROOT


class Consolidacion(unittest.TestCase):
    def setUp(self):
        self.manual = json.loads((ROOT / 'resultados' / 'clasificacion_errores.json').read_text())['fallos']

    def test_todas_las_configuraciones_clasificadas(self):
        for nombre in CONFIGURACIONES:
            filas, resumen = filas_configuracion(nombre, self.manual)
            self.assertEqual(len(filas), 40)
            self.assertEqual(sum(f['peso'] for f in filas), resumen['peso_total'])
            for f in filas:
                self.assertEqual(bool(f['categoria_error']), not f['acierto'])
                if not f['acierto']:
                    self.assertIn(f['categoria_error'], CATEGORIAS)
                    if f['codigo_mysql']:
                        self.assertEqual(POR_CODIGO[f['codigo_mysql']], f['categoria_error'])

    def test_clasificacion_manual_sin_entradas_sobrantes(self):
        fallos = {(n, f['id']) for n in CONFIGURACIONES for f in filas_configuracion(n, self.manual)[0] if not f['acierto']}
        manuales = {(n, i) for i, por_config in self.manual.items() for n in por_config}
        self.assertEqual(fallos, manuales)

    def test_entrega_es_a_directa(self):
        self.assertEqual([n for n, c in CONFIGURACIONES.items() if c[3]], ['a'])


if __name__ == '__main__':
    unittest.main()
