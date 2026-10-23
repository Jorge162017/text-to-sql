"""Entrena un adapter LoRA con el prompt congelado de solucion.py.

La pérdida se calcula solo sobre el SQL de respuesta (el prompt se enmascara con -100).
Se separa un 5 % por esquema como conjunto dev para la curva de pérdida; la
validación propia (val_*) nunca se usa.

    python -m entrenamiento.entrenar --config entrenamiento/lora_a.json
    python -m entrenamiento.entrenar --config entrenamiento/lora_a.json --prueba   # 2 pasos, sin escribir en el repo
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import random
import sys
import tempfile
import time
from pathlib import Path

from scripts.comun import DATOS, ROOT, guardar_json, leer_jsonl
from scripts.validar_datos import cargar_particiones, hash_archivo

os.environ['SOLUCION_CARGA_DIFERIDA'] = '1'
sys.path.insert(0, str(ROOT))
import solucion  # noqa: E402


def leer_config_entrenamiento(ruta):
    config = json.loads(Path(ruta).read_text(encoding='utf-8'))
    for campo in ['nombre', 'hipotesis', 'modelo_base', 'datos', 'fraccion_dev', 'semilla', 'max_longitud',
                  'lora', 'entrenamiento', 'salida_adapter']:
        if campo not in config:
            raise ValueError(f'Falta {campo} en {ruta}')
    if len(config['hipotesis'].strip()) < 50:
        raise ValueError('La hipótesis debe quedar escrita antes de entrenar')
    if config['modelo_base'] != solucion.leer_config()['modelo_base']:
        raise ValueError('El modelo base debe coincidir con config.json')
    return config


def cargar_pares(config):
    particiones = cargar_particiones()
    pares = leer_jsonl(ROOT / config['datos'])
    prohibidos = set(particiones['validacion'])
    preguntas_val = {p['pregunta'].strip().lower() for p in leer_jsonl(DATOS / 'validacion' / 'pares.jsonl')}
    for p in pares:
        if p['esquema_id'] in prohibidos or p['esquema_id'] not in particiones['entrenamiento']:
            raise ValueError(f'{p["id"]}: esquema fuera de la partición de entrenamiento')
        if p['pregunta'].strip().lower() in preguntas_val:
            raise ValueError(f'{p["id"]}: pregunta idéntica a una de validación')
    return pares


def dividir(pares, fraccion, semilla):
    """Separación dev estratificada por esquema y reproducible."""
    por_esquema = defaultdict(list)
    for p in pares:
        por_esquema[p['esquema_id']].append(p)
    train, dev = [], []
    for esquema in sorted(por_esquema):
        grupo = sorted(por_esquema[esquema], key=lambda p: p['id'])
        random.Random(f'{semilla}-{esquema}').shuffle(grupo)
        n = max(1, round(len(grupo) * fraccion))
        dev += grupo[:n]
        train += grupo[n:]
    return train, dev


def tokenizar(tokenizer, par, max_longitud):
    """input_ids = prompt de inferencia + SQL + <|im_end|>; labels solo en la respuesta."""
    prompt = tokenizer.apply_chat_template(solucion.construir_mensajes(par['esquema'], par['pregunta']),
                                           tokenize=False, add_generation_prompt=True)
    ids_prompt = tokenizer(prompt, add_special_tokens=False)['input_ids']
    ids_respuesta = tokenizer(par['sql'].strip() + tokenizer.eos_token, add_special_tokens=False)['input_ids']
    ids = ids_prompt + ids_respuesta
    if len(ids) > max_longitud:
        raise ValueError(f'{par["id"]}: {len(ids)} tokens supera max_longitud={max_longitud}; no se trunca')
    return {'input_ids': ids, 'attention_mask': [1] * len(ids),
            'labels': [-100] * len(ids_prompt) + ids_respuesta}


def curvas(historial, ruta):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return False
    train = [(h['step'], h['loss']) for h in historial if 'loss' in h]
    dev = [(h['step'], h['eval_loss']) for h in historial if 'eval_loss' in h]
    fig, ax = plt.subplots(figsize=(7, 4))
    if train:
        ax.plot(*zip(*train), label='entrenamiento', color='#1f77b4')
    if dev:
        ax.plot(*zip(*dev), label='dev (5 % por esquema)', color='#d62728', marker='o')
    ax.set_xlabel('paso de optimización')
    ax.set_ylabel('pérdida (solo SQL de respuesta)')
    ax.set_title(ruta.parent.name)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--config', required=True)
    parser.add_argument('--prueba', action='store_true', help='2 pasos con pocos ejemplos; escribe en un directorio temporal')
    parser.add_argument('--reemplazar', action='store_true', help='Permite sobrescribir un adapter existente')
    args = parser.parse_args()

    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import (DataCollatorForSeq2Seq, Trainer,
                              TrainingArguments, set_seed)

    config = leer_config_entrenamiento(args.config)
    e = config['entrenamiento']
    set_seed(config['semilla'])
    cuda = torch.cuda.is_available()
    if e['fp16'] and not cuda and not args.prueba:
        raise SystemExit('La configuración exige fp16 en CUDA (Colab T4).')
    temporal = Path(tempfile.mkdtemp(prefix='lora_prueba_')) if args.prueba else None
    salida_adapter = temporal / 'adapter' if args.prueba else ROOT / config['salida_adapter']
    salida_resultados = temporal / 'resultados' if args.prueba else ROOT / 'resultados' / 'entrenamientos' / config['nombre']
    checkpoints = temporal / 'ckpt' if args.prueba else ROOT / '.cache' / 'entrenamiento' / config['nombre']
    if (salida_adapter / 'adapter_config.json').exists() and not args.reemplazar:
        raise SystemExit(f'Ya existe un adapter en {salida_adapter}; usa --reemplazar.')

    pares = cargar_pares(config)
    train, dev = dividir(pares, config['fraccion_dev'], config['semilla'])
    if args.prueba:
        train, dev = train[:16], dev[:4]
    tokenizer = solucion.cargar_tokenizer(config['modelo_base'])
    datos_train = [tokenizar(tokenizer, p, config['max_longitud']) for p in train]
    datos_dev = [tokenizar(tokenizer, p, config['max_longitud']) for p in dev]
    tokens_respuesta = sum(sum(l != -100 for l in d['labels']) for d in datos_train)
    print(f'train={len(datos_train)} dev={len(datos_dev)} tokens={sum(len(d["input_ids"]) for d in datos_train)} '
          f'tokens_respuesta={tokens_respuesta}', flush=True)

    tipo = torch.float16 if cuda else torch.float32
    modelo = solucion.cargar_modelo_base(config['modelo_base'], dtype=tipo)
    modelo.config.use_cache = False
    l = config['lora']
    modelo = get_peft_model(modelo, LoraConfig(r=l['r'], lora_alpha=l['lora_alpha'], lora_dropout=l['lora_dropout'],
                                               bias=l['bias'], target_modules=l['target_modules'], task_type='CAUSAL_LM'))
    entrenables = sum(p.numel() for p in modelo.parameters() if p.requires_grad)
    totales = sum(p.numel() for p in modelo.parameters())
    print(f'Parámetros entrenables: {entrenables:,} de {totales:,} ({100 * entrenables / totales:.3f} %)', flush=True)

    argumentos = TrainingArguments(
        output_dir=str(checkpoints), num_train_epochs=e['epocas'], max_steps=2 if args.prueba else -1,
        per_device_train_batch_size=e['batch_por_dispositivo'], per_device_eval_batch_size=e['batch_por_dispositivo'],
        gradient_accumulation_steps=1 if args.prueba else e['acumulacion_gradiente'],
        learning_rate=e['tasa_aprendizaje'], lr_scheduler_type=e['programador'], warmup_steps=e['pasos_calentamiento'],
        weight_decay=e['weight_decay'], max_grad_norm=e['max_grad_norm'], optim=e['optimizador'],
        fp16=e['fp16'] and cuda, gradient_checkpointing=e['gradient_checkpointing'],
        gradient_checkpointing_kwargs={'use_reentrant': False},
        logging_steps=1 if args.prueba else e['pasos_registro'], eval_strategy='steps',
        eval_steps=1 if args.prueba else e['pasos_evaluacion'], save_strategy='steps',
        save_steps=1 if args.prueba else e['pasos_guardado'], save_total_limit=2,
        seed=config['semilla'], data_seed=config['semilla'], report_to='none', remove_unused_columns=False,
        dataloader_num_workers=0)
    trainer = Trainer(model=modelo, args=argumentos, train_dataset=datos_train, eval_dataset=datos_dev,
                      data_collator=DataCollatorForSeq2Seq(tokenizer, padding=True, label_pad_token_id=-100,
                                                           pad_to_multiple_of=8),
                      processing_class=tokenizer)

    reanudar = checkpoints.exists() and any(checkpoints.glob('checkpoint-*'))
    eval_inicial = None if reanudar else trainer.evaluate()['eval_loss']
    if cuda:
        torch.cuda.reset_peak_memory_stats()
    inicio = time.perf_counter()
    resultado = trainer.train(resume_from_checkpoint=True if reanudar else None)
    duracion = time.perf_counter() - inicio
    eval_final = trainer.evaluate()['eval_loss']
    memoria = torch.cuda.max_memory_allocated() / 2**30 if cuda else None

    salida_adapter.mkdir(parents=True, exist_ok=True)
    modelo.save_pretrained(str(salida_adapter))
    historial = trainer.state.log_history
    if eval_inicial is not None:
        historial = [{'step': 0, 'eval_loss': eval_inicial}, *historial]
    salida_resultados.mkdir(parents=True, exist_ok=True)
    guardar_json(salida_resultados / 'historial.json', historial)
    hay_curvas = curvas(historial, salida_resultados / 'curvas_loss.png')
    entorno = {'python': platform.python_version(), 'torch': torch.__version__,
               'gpu': torch.cuda.get_device_name(0) if cuda else None}
    try:
        import transformers
        import peft
        entorno.update(transformers=transformers.__version__, peft=peft.__version__)
    except ImportError:
        pass
    metricas = {
        'nombre': config['nombre'], 'fecha_utc': datetime.now(timezone.utc).isoformat(), 'prueba': args.prueba,
        'hipotesis': config['hipotesis'], 'config': config,
        'prompt_version': solucion.PROMPT_VERSION, 'revision_modelo': solucion._revision_modelo(config['modelo_base']),
        'parametros_entrenables': entrenables, 'parametros_totales': totales,
        'porcentaje_entrenable': round(100 * entrenables / totales, 4),
        'ejemplos_entrenamiento': len(datos_train), 'ejemplos_dev': len(datos_dev),
        'ids_dev': [p['id'] for p in dev], 'tokens_respuesta_entrenamiento': tokens_respuesta,
        'pasos': trainer.state.global_step, 'reanudado': reanudar,
        'tiempo_entrenamiento_s': round(duracion, 1), 'tiempo_trainer_s': round(resultado.metrics['train_runtime'], 1),
        'muestras_por_s': round(resultado.metrics['train_samples_per_second'], 3),
        'loss_entrenamiento_promedio': round(resultado.metrics['train_loss'], 5),
        'eval_loss_inicial': eval_inicial, 'eval_loss_final': eval_final,
        'memoria_pico_gib': round(memoria, 2) if memoria else None,
        'curvas': 'curvas_loss.png' if hay_curvas else None,
        'adapter': str(salida_adapter.relative_to(ROOT)) if not args.prueba else str(salida_adapter),
        'adapter_sha256': {f.name: hash_archivo(f) for f in sorted(salida_adapter.iterdir()) if f.is_file()},
        'datos_sha256': hash_archivo(ROOT / config['datos']),
        'config_sha256': hashlib.sha256(Path(args.config).read_bytes()).hexdigest(),
        'entorno': entorno}
    guardar_json(salida_resultados / 'metricas.json', metricas)
    print(json.dumps({k: metricas[k] for k in ['parametros_entrenables', 'porcentaje_entrenable', 'pasos',
                                                'tiempo_entrenamiento_s', 'eval_loss_inicial', 'eval_loss_final',
                                                'memoria_pico_gib', 'adapter']}, ensure_ascii=False, indent=2))
    print(f'Resultados en {salida_resultados}')


if __name__ == '__main__':
    main()
