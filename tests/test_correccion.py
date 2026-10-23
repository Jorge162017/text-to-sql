"""Política de corrección sin GPU: límites, feedback y fallback."""
import os
import unittest
from unittest.mock import Mock
os.environ['SOLUCION_CARGA_DIFERIDA'] = '1'
import solucion
from evaluacion.correccion import generar_sql


class Correccion(unittest.TestCase):
    def setUp(self):
        self.s = Mock(wraps=solucion)
        self.s.CONSULTA_NEUTRA = solucion.CONSULTA_NEUTRA
        self.s.generar_sql.return_value = 'SELECT inexistente FROM tabla'

    def test_sin_callback_equivale_a_directa(self):
        reparar = Mock()
        self.assertEqual(generar_sql(self.s, 'esquema', 'pregunta', reparar=reparar), self.s.generar_sql.return_value)
        reparar.assert_not_called()

    def test_exito_no_repara_ni_usa_filas_para_cambiar_sql(self):
        cb = Mock(return_value={'ok': True, 'filas': []})
        reparar = Mock()
        generar_sql(self.s, 'esquema', 'pregunta', cb, reparar=reparar)
        self.assertEqual(cb.call_count, 1)
        reparar.assert_not_called()

    def test_error_se_envia_al_modelo_y_para_en_exito(self):
        cb = Mock(side_effect=[{'ok': False, 'error': 'Unknown column inexistente'}, {'ok': True}])
        reparar = Mock(return_value='SELECT 2')
        self.assertEqual(generar_sql(self.s, 'esquema', 'pregunta', cb, reparar=reparar), 'SELECT 2')
        self.assertIn('Unknown column inexistente', reparar.call_args.args[0][-1]['content'])
        self.assertEqual(cb.call_count, 2)

    def test_maximo_tres_llamadas_y_dos_reparaciones(self):
        cb = Mock(return_value={'ok': False, 'error': 'error'})
        reparar = Mock(side_effect=['SELECT 2', 'SELECT 3'])
        self.assertEqual(generar_sql(self.s, 'esquema', 'pregunta', cb, reparar=reparar), 'SELECT 3')
        self.assertEqual(cb.call_count, 3)
        self.assertEqual(reparar.call_count, 2)

    def test_rechaza_escritura_y_detiene_ciclo(self):
        for respuesta in ['DELETE FROM tabla', 'SELECT inexistente FROM tabla']:
            cb = Mock(return_value={'ok': False, 'error': 'error'})
            generar_sql(self.s, 'esquema', 'pregunta', cb, reparar=Mock(return_value=respuesta))
            self.assertEqual(cb.call_count, 1)

    def test_no_callback_si_no_quedan_diez_segundos_y_medio(self):
        cb = Mock()
        generar_sql(self.s, 'esquema', 'pregunta', cb, reloj=Mock(side_effect=[0, 20]))
        cb.assert_not_called()

    def test_error_callback_conserva_consulta(self):
        cb = Mock(side_effect=RuntimeError('fallo'))
        self.assertEqual(generar_sql(self.s, 'esquema', 'pregunta', cb), self.s.generar_sql.return_value)
