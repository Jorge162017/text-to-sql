"""Preparación del entrenamiento LoRA: sin fuga, división reproducible y pérdida solo en el SQL."""
import json
import tempfile
import unittest
from pathlib import Path

from entrenamiento.entrenar import cargar_pares, dividir, leer_config_entrenamiento, tokenizar
from scripts.comun import ROOT

CONFIG_A = ROOT / 'entrenamiento' / 'lora_a.json'


class ConfiguracionLoRA(unittest.TestCase):
    def test_config_a_con_hipotesis(self):
        config = leer_config_entrenamiento(CONFIG_A)
        self.assertEqual(config['lora']['r'], 8)
        self.assertIn('0.5658', config['hipotesis'])
        self.assertEqual(config['salida_adapter'], 'adapter/')

    def test_otras_configuraciones_cambian_un_solo_factor(self):
        """Cualquier lora_*.json adicional (p. ej. B) solo puede diferir de A en lora.r, nombre, hipótesis y salida."""
        base = json.loads(CONFIG_A.read_text())
        libres = {'nombre', 'hipotesis', 'salida_adapter'}
        for ruta in sorted((ROOT / 'entrenamiento').glob('lora_*.json')):
            if ruta == CONFIG_A:
                continue
            with self.subTest(config=ruta.name):
                otra = json.loads(ruta.read_text())
                self.assertEqual({k: v for k, v in otra.items() if k not in libres | {'lora'}},
                                 {k: v for k, v in base.items() if k not in libres | {'lora'}})
                self.assertEqual({k: v for k, v in otra['lora'].items() if k != 'r'},
                                 {k: v for k, v in base['lora'].items() if k != 'r'})
                self.assertNotEqual(otra['lora']['r'], base['lora']['r'])

    def test_sin_hipotesis_rechazada(self):
        config = json.loads(CONFIG_A.read_text())
        config['hipotesis'] = ''
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / 'sin_hipotesis.json'
            ruta.write_text(json.dumps(config))
            with self.assertRaises(ValueError):
                leer_config_entrenamiento(ruta)


class Datos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = leer_config_entrenamiento(CONFIG_A)
        cls.pares = cargar_pares(cls.config)

    def test_sin_esquemas_de_validacion(self):
        self.assertFalse({p['esquema_id'] for p in self.pares} & {'val_biblioteca', 'val_hospital'})

    def test_division_reproducible_estratificada_y_disjunta(self):
        train, dev = dividir(self.pares, 0.05, 2026)
        train2, dev2 = dividir(self.pares, 0.05, 2026)
        self.assertEqual([p['id'] for p in dev], [p['id'] for p in dev2])
        self.assertEqual(len(train) + len(dev), len(self.pares))
        self.assertFalse({p['id'] for p in train} & {p['id'] for p in dev})
        self.assertEqual(len({p['esquema_id'] for p in dev}), 15)


class Tokenizacion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from transformers import AutoTokenizer
            cls.tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-Coder-1.5B-Instruct', local_files_only=True)
        except Exception as exc:
            raise unittest.SkipTest(f'Tokenizer no disponible localmente: {exc}')
        cls.par = cargar_pares(leer_config_entrenamiento(CONFIG_A))[0]

    def test_perdida_solo_en_sql_y_prompt_de_inferencia(self):
        import solucion
        d = tokenizar(self.tokenizer, self.par, 1024)
        respuesta = [t for t, l in zip(d['input_ids'], d['labels']) if l != -100]
        self.assertEqual(self.tokenizer.decode(respuesta), self.par['sql'].strip() + '<|im_end|>')
        n_prompt = d['labels'].index(next(l for l in d['labels'] if l != -100))
        prompt = self.tokenizer.apply_chat_template(solucion.construir_mensajes(self.par['esquema'], self.par['pregunta']),
                                                    tokenize=False, add_generation_prompt=True)
        self.assertEqual(self.tokenizer.decode(d['input_ids'][:n_prompt]), prompt)

    def test_no_trunca(self):
        with self.assertRaises(ValueError):
            tokenizar(self.tokenizer, self.par, 100)


if __name__ == '__main__':
    unittest.main()
