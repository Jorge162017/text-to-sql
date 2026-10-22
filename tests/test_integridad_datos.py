"""Pruebas del contrato de datos y prevención de fuga/autoria falsa."""
import unittest

from scripts.generar_datos import DOMINIOS, candidatos
from scripts.dominios_diversos import DOMINIOS_DIVERSOS, candidatos_diversos
from scripts.comun import DATOS, leer_jsonl
from scripts.validar_datos import comprobar_registro, comprobar_autoria, cargar_particiones


class IntegridadDatos(unittest.TestCase):
    def test_particion_disjunta(self):
        p = cargar_particiones()
        self.assertFalse(set(p['entrenamiento']) & set(p['validacion']))

    def test_cobertura_y_duplicados(self):
        registros = [r for d in DOMINIOS for r in candidatos(d)] + [r for d in DOMINIOS_DIVERSOS for r in candidatos_diversos(d)]
        self.assertGreaterEqual(len(registros), 2000)
        self.assertEqual(len({r['id'] for r in registros}), len(registros))
        self.assertEqual(len({(r['esquema_id'], r['pregunta'], r['sql']) for r in registros}), len(registros))
        self.assertEqual(len({r['esquema_id'] for r in registros}), 15)
        self.assertEqual({r['nivel'] for r in registros}, {'facil', 'media', 'dificil'})

    def test_fuga_rechazada(self):
        r = next(candidatos(DOMINIOS[0]))
        with self.assertRaises(ValueError):
            comprobar_registro(r, ['val_biblioteca'])

    def test_no_escritura_ni_multisentencia(self):
        r = next(candidatos(DOMINIOS[0]))
        for sql in ['DELETE FROM clientes', 'SELECT 1; DROP TABLE clientes', "SELECT 1 INTO OUTFILE '/tmp/x'", 'SELECT SLEEP(10)']:
            with self.subTest(sql=sql), self.assertRaises(ValueError):
                comprobar_registro({**r, 'sql': sql}, ['train_tienda'])

    def test_borradores_no_son_autoria_humana(self):
        registros = leer_jsonl(DATOS / 'validacion' / 'preguntas_propias.jsonl')
        self.assertEqual(len(registros), 40)
        self.assertEqual(len({r['esquema_id'] for r in registros}), 2)
        comprobar_autoria(registros)
        registros = [{**r, 'autor': None, 'estado': 'borrador_no_entregable'} for r in registros]
        with self.assertRaises(ValueError):
            comprobar_autoria(registros)

    def test_peso_incorrecto_rechazado(self):
        r = next(candidatos(DOMINIOS[0]))
        with self.assertRaises(ValueError):
            comprobar_registro({**r, 'peso': 3}, ['train_tienda'])


if __name__ == '__main__':
    unittest.main()
