"""Regresiones: evidencia faltante, fuga por SQL y comparación de resultados."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.auditar_datos import verificar_hashes, topologias
from scripts.validar_datos import cargar_particiones
from scripts.validar_datos import comprobar_registro, hash_archivo
from scripts.generar_datos import DOMINIOS, candidatos
from scripts.revisar_muestra import comparar


class Auditoria(unittest.TestCase):
    def test_diversidad_estructural_real(self):
        grupos = topologias(cargar_particiones()['entrenamiento'])
        self.assertEqual(len(grupos), 6)
        self.assertEqual(sum(map(len, grupos)), 15)

    def test_hash_obligatorio_no_puede_omitirse(self):
        with self.assertRaises(ValueError):
            verificar_hashes({'sha256': {}}, ['datos.jsonl'])

    def test_editar_o_borrar_evidencia_se_detecta(self):
        with tempfile.TemporaryDirectory() as carpeta:
            raiz = Path(carpeta)
            archivo = raiz / 'datos.jsonl'
            archivo.write_text('original')
            reporte = {'sha256': {'datos.jsonl': hash_archivo(archivo)}}
            with patch('scripts.auditar_datos.ROOT', raiz):
                verificar_hashes(reporte, ['datos.jsonl'])
                archivo.write_text('modificado')
                with self.assertRaises(ValueError):
                    verificar_hashes(reporte, ['datos.jsonl'])
                archivo.unlink()
                with self.assertRaises(ValueError):
                    verificar_hashes(reporte, ['datos.jsonl'])

    def test_sql_no_puede_usar_validacion_desde_train(self):
        r = next(candidatos(DOMINIOS[0]))
        with self.assertRaises(ValueError):
            comprobar_registro({**r, 'sql': 'SELECT * FROM val_biblioteca.titulos'}, ['train_tienda'])

    def test_resultados_conservan_duplicados_y_orden(self):
        actual = {'filas': [['Ana', '2.00'], ['Ana', '2.00'], ['Luis', '3']], 'tipos_mysql': [253, 246]}
        self.assertTrue(comparar(actual, [['Luis', 3], ['Ana', 2], ['Ana', 2]], False))
        self.assertFalse(comparar(actual, [['Luis', 3], ['Ana', 2]], False))
        self.assertFalse(comparar(actual, [['Luis', 3], ['Ana', 2], ['Ana', 2]], True))


if __name__ == '__main__':
    unittest.main()
