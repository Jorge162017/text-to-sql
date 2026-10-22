"""Reglas del evaluador por ejecución: orden, duplicados, redondeo y columnas adicionales."""
from collections import Counter
from datetime import date
from decimal import Decimal
import unittest

from evaluacion.comparar import categoria_error_mysql, comparar_resultados, normalizar_celda, rehidratar, resumir


def comparar(ref, pred, orden=False, cols_ref=None, cols_pred=None):
    cols_ref = cols_ref or [f'r{i}' for i in range(len(ref[0]) if ref else 1)]
    cols_pred = cols_pred or [f'p{i}' for i in range(len(pred[0]) if pred else len(cols_ref))]
    return comparar_resultados(cols_ref, ref, cols_pred, pred, orden)[0]


class Comparacion(unittest.TestCase):
    def test_identicos(self):
        self.assertTrue(comparar([[1, 'a'], [2, 'b']], [[1, 'a'], [2, 'b']]))

    def test_orden_ignorado_si_no_se_exige(self):
        self.assertTrue(comparar([[1, 'a'], [2, 'b']], [[2, 'b'], [1, 'a']]))

    def test_orden_exigido(self):
        self.assertFalse(comparar([[1, 'a'], [2, 'b']], [[2, 'b'], [1, 'a']], orden=True))
        self.assertTrue(comparar([[1, 'a'], [2, 'b']], [[1, 'a'], [2, 'b']], orden=True))

    def test_duplicados_conservados(self):
        self.assertFalse(comparar([['x'], ['x'], ['y']], [['x'], ['y'], ['y']]))
        self.assertFalse(comparar([['x'], ['x']], [['x']]))  # DISTINCT indebido
        self.assertFalse(comparar([['x']], [['x'], ['x']]))  # JOIN que multiplica filas
        self.assertTrue(comparar([['x'], ['x'], ['y']], [['y'], ['x'], ['x']]))

    def test_redondeo_dos_decimales(self):
        self.assertTrue(comparar([[Decimal('3.3333')]], [[3.333333333]]))
        self.assertTrue(comparar([[5]], [[Decimal('5.000')]]))
        self.assertTrue(comparar([[2.675]], [[Decimal('2.68')]]))  # half-up sobre la representación decimal
        self.assertFalse(comparar([[Decimal('3.33')]], [[Decimal('3.34')]]))

    def test_columna_adicional_no_penaliza(self):
        self.assertTrue(comparar([['Ana', 3]], [[7, 'Ana', 3]], cols_ref=['nombre', 'n'], cols_pred=['id', 'nombre', 'n']))

    def test_columnas_permutadas_y_alias_distintos(self):
        self.assertTrue(comparar([['Ana', 3], ['Luis', 1]], [[1, 'Luis'], [3, 'Ana']],
                                 cols_ref=['usuario', 'cantidad'], cols_pred=['total', 'nombre']))

    def test_falta_columna(self):
        self.assertFalse(comparar([['Ana', 3]], [['Ana']]))

    def test_valores_cruzados_entre_filas_fallan(self):
        # Cada columna coincide como multiconjunto, pero las filas están mal emparejadas.
        self.assertFalse(comparar([['Ana', 1], ['Luis', 2]], [['Ana', 2], ['Luis', 1]]))

    def test_columnas_con_mismos_valores_eligen_la_correcta(self):
        # Dos columnas predichas iguales por columna; solo una asignación reproduce las filas.
        ref = [[1, 1], [2, 3]]
        pred = [[1, 1, 1], [3, 2, 3]]
        self.assertTrue(comparar(ref, pred))

    def test_vacio(self):
        self.assertTrue(comparar_resultados(['a'], [], ['a', 'b'], [], False)[0])
        self.assertFalse(comparar_resultados(['a', 'b'], [], ['a'], [], False)[0])

    def test_null_y_fechas(self):
        self.assertTrue(comparar([[None, date(2025, 1, 2)]], [[None, date(2025, 1, 2)]]))
        self.assertFalse(comparar([[None]], [['']]))
        self.assertEqual(normalizar_celda(date(2025, 1, 2)), '2025-01-02')

    def test_motivo_orden(self):
        ok, _, motivo = comparar_resultados(['a'], [[1], [2]], ['a'], [[2], [1]], True)
        self.assertFalse(ok)
        self.assertEqual(motivo, 'orden distinto')

    def test_rehidratar_evidencia_json(self):
        filas = rehidratar([['Ana', '12.50', None]], [253, 246, 246])
        self.assertEqual(filas, [['Ana', Decimal('12.50'), None]])


class Puntuacion(unittest.TestCase):
    def test_ex_ponderado(self):
        registros = [
            {'nivel': 'facil', 'peso': 1, 'esquema_id': 'a', 'acierto': True, 'categoria': 'correcto'},
            {'nivel': 'media', 'peso': 2, 'esquema_id': 'a', 'acierto': False, 'categoria': 'sintaxis'},
            {'nivel': 'dificil', 'peso': 3, 'esquema_id': 'b', 'acierto': True, 'categoria': 'correcto'},
        ]
        r = resumir(registros)
        self.assertEqual((r['peso_aciertos'], r['peso_total']), (4, 6))
        self.assertAlmostEqual(r['ex'], 0.6667)
        self.assertEqual(r['por_nivel']['media']['ex'], 0.0)
        self.assertEqual(r['por_esquema']['b']['ex'], 1.0)
        self.assertEqual(Counter(r['categorias']), Counter({'correcto': 2, 'sintaxis': 1}))

    def test_categorias_mysql(self):
        self.assertEqual(categoria_error_mysql(1064), 'sintaxis')
        self.assertEqual(categoria_error_mysql(1054), 'columna_tabla_inexistente')
        self.assertEqual(categoria_error_mysql(1146), 'columna_tabla_inexistente')
        self.assertEqual(categoria_error_mysql(1055), 'agregacion')


if __name__ == '__main__':
    unittest.main()
