"""Contrato de solucion.py sin cargar el modelo: config, prompt, extracción y solo lectura."""
import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ['SOLUCION_CARGA_DIFERIDA'] = '1'
import solucion  # noqa: E402

from scripts.comun import DATOS, leer_jsonl  # noqa: E402


class Config(unittest.TestCase):
    def test_config_entregada(self):
        config = solucion.leer_config()
        self.assertEqual(set(config), {'modelo_base', 'adapter', 'usar_adapter', 'semilla'})
        self.assertEqual(config['modelo_base'], 'Qwen/Qwen2.5-Coder-1.5B-Instruct')
        self.assertEqual(config['semilla'], 2026)

    def test_modelo_no_permitido(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / 'config.json'
            ruta.write_text(json.dumps({'modelo_base': 'otro/modelo', 'adapter': 'adapter/',
                                        'usar_adapter': False, 'semilla': 1}))
            with self.assertRaises(ValueError):
                solucion.leer_config(ruta)


class Prompt(unittest.TestCase):
    def setUp(self):
        self.par = leer_jsonl(DATOS / 'entrenamiento' / 'pares.jsonl')[0]

    def test_compactar_conserva_semantica(self):
        compacto = solucion.compactar_esquema(self.par['esquema'])
        for fragmento in ['CREATE TABLE `clientes`', 'COMMENT=\'Contactos de tienda\'', 'FOREIGN KEY',
                          'PRIMARY KEY', "COMMENT 'Precio historico de esta linea'"]:
            self.assertIn(fragmento, compacto)
        for ruido in ['ENGINE=', 'CHARSET=', 'COLLATE=', '\n  KEY ']:
            self.assertNotIn(ruido, compacto)
        self.assertEqual(compacto.count('CREATE TABLE'), self.par['esquema'].count('CREATE TABLE'))
        self.assertNotIn(',\n)', compacto)

    def test_compactar_tolera_formato_desconocido(self):
        self.assertIn('tabla rara', solucion.compactar_esquema('tabla rara'))

    def test_mensajes_iguales_para_base_y_adapter(self):
        a = solucion.construir_mensajes(self.par['esquema'], self.par['pregunta'])
        b = solucion.construir_mensajes(self.par['esquema'], self.par['pregunta'])
        self.assertEqual(a, b)
        self.assertEqual([m['role'] for m in a], ['system', 'user'])
        self.assertIn(self.par['pregunta'], a[1]['content'])


class Limpieza(unittest.TestCase):
    def test_bloque_markdown(self):
        texto = 'Aquí está:\n```sql\nSELECT nombre\nFROM clientes;\n```\nEsta consulta...'
        self.assertEqual(solucion.limpiar_sql(texto), 'SELECT nombre\nFROM clientes')

    def test_texto_sin_bloque(self):
        self.assertEqual(solucion.limpiar_sql('SELECT 1 AS x;\nExplicación'), 'SELECT 1 AS x')
        self.assertEqual(solucion.limpiar_sql('La consulta es: SELECT a FROM t\n\nEsto devuelve a.'), 'SELECT a FROM t')

    def test_solo_primera_sentencia(self):
        self.assertEqual(solucion.limpiar_sql('SELECT a FROM t; DROP TABLE t;'), 'SELECT a FROM t')

    def test_punto_y_coma_dentro_de_literal(self):
        sql = "SELECT a FROM t WHERE b = 'x;y'"
        self.assertEqual(solucion.limpiar_sql(sql + ';'), sql)

    def test_with(self):
        sql = 'WITH c AS (SELECT a FROM t) SELECT a FROM c'
        self.assertEqual(solucion.limpiar_sql(sql), sql)

    def test_escrituras_rechazadas(self):
        for sql in ['DELETE FROM t', 'UPDATE t SET a = 1', 'WITH c AS (SELECT 1) DELETE FROM t',
                    "SELECT a INTO OUTFILE '/tmp/x' FROM t", 'SELECT SLEEP(5)', 'SELECT a FROM t FOR UPDATE',
                    'DROP TABLE t', 'texto sin consulta']:
            with self.subTest(sql=sql):
                self.assertFalse(solucion.es_consulta_lectura(sql))
                self.assertEqual(solucion.limpiar_sql(sql), solucion.CONSULTA_NEUTRA)

    def test_funciones_de_texto_permitidas(self):
        for sql in ["SELECT REPLACE(nombre, 'a', 'b') FROM t", "SELECT INSERT(nombre, 1, 2, 'x') FROM t",
                    "SELECT a FROM t WHERE nota = 'delete'", 'SELECT `update` FROM t']:
            with self.subTest(sql=sql):
                self.assertTrue(solucion.es_consulta_lectura(sql))

    def test_comentarios(self):
        self.assertTrue(solucion.es_consulta_lectura('SELECT a FROM t -- nota; DROP TABLE t'))
        self.assertTrue(solucion.es_consulta_lectura('SELECT a - -1 FROM t'))

    def test_referencias_propias_son_lectura(self):
        for par in leer_jsonl(DATOS / 'validacion' / 'pares.jsonl'):
            with self.subTest(id=par['id']):
                self.assertTrue(solucion.es_consulta_lectura(par['sql']))
                self.assertEqual(solucion.limpiar_sql(par['sql']), par['sql'].strip().rstrip(';'))


if __name__ == '__main__':
    unittest.main()
