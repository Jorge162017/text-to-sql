"""Regresión: no declarar comparación congelada solo por conservar el prompt."""
from copy import deepcopy
import os
import unittest

os.environ['SOLUCION_CARGA_DIFERIDA'] = '1'
import solucion
from evaluacion.congelar import configuracion, coincide_configuracion


class ConfiguracionExperimental(unittest.TestCase):
    def test_configuracion_vigente(self):
        self.assertTrue(coincide_configuracion(configuracion(solucion), solucion))

    def test_mismo_prompt_no_oculta_cambio_de_codigo_o_revision(self):
        actual = configuracion(solucion)
        for campo in ['sha256', 'revision_modelo', 'limpieza_version']:
            alterada = deepcopy(actual)
            if campo == 'sha256':
                alterada[campo]['solucion.py'] = '0' * 64
            else:
                alterada[campo] = 'otra-version'
            with self.subTest(campo=campo):
                self.assertEqual(alterada['prompt'], actual['prompt'])
                self.assertFalse(coincide_configuracion(alterada, solucion))


if __name__ == '__main__':
    unittest.main()
