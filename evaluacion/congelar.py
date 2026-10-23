"""Congela la configuración experimental compartida por baseline, LoRA A y LoRA B.

Escribe resultados/configuracion_experimental.json. Las evaluaciones registran
prompt_sha256; si no coincide con este archivo, la comparación no es válida.
"""
import hashlib
import json
import os
import sys

from scripts.comun import DATOS, ROOT, guardar_json
from scripts.validar_datos import hash_archivo

RUTA = ROOT / 'resultados' / 'configuracion_experimental.json'


def huella_prompt(solucion):
    prompt = json.dumps({'version': solucion.PROMPT_VERSION, 'instrucciones': solucion.INSTRUCCIONES,
                         'max_tokens_nuevos': solucion.MAX_TOKENS_NUEVOS}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(prompt.encode()).hexdigest()


def configuracion(solucion):
    archivos = ['solucion.py', 'entrenamiento/entrenar.py', 'evaluacion/comparar.py', 'evaluacion/evaluar.py',
                'evaluacion/correccion.py',
                'datos/particiones.json', 'datos/entrenamiento/pares.jsonl', 'datos/validacion/pares.jsonl',
                'datos/validacion/referencias_resultados.jsonl']
    return {
        'modelo_base': solucion.leer_config()['modelo_base'],
        'revision_modelo': solucion._revision_modelo(solucion.leer_config()['modelo_base']),
        'limpieza_version': solucion.LIMPIEZA_VERSION,
        'semilla': solucion.leer_config()['semilla'],
        'prompt': {'version': solucion.PROMPT_VERSION, 'sha256': huella_prompt(solucion),
                   'instrucciones': solucion.INSTRUCCIONES,
                   'formato_usuario': '### Esquema\\n{compactar_esquema(esquema)}\\n\\n### Pregunta\\n{pregunta}',
                   'plantilla_chat': 'apply_chat_template del tokenizer del modelo base, add_generation_prompt=True'},
        'generacion': {'do_sample': False, 'num_beams': 1, 'repetition_penalty': 1.0,
                       'max_new_tokens': solucion.MAX_TOKENS_NUEVOS, 'max_time_s': solucion.MAX_SEGUNDOS_GENERACION,
                       'consulta_neutra': solucion.CONSULTA_NEUTRA, 'estrategia': 'directa, sin llamadas a ejecutar'},
        'experimento_inferencia': {'version': 'correccion_errores_v1',
                                  'control': 'directa', 'tratamiento': 'correccion',
                                  'mismo_prompt_inicial': True,
                                  'reparaciones_maximas': 2, 'llamadas_maximas': 3,
                                  'presupuesto_s': 29, 'reserva_callback_s': 10.5,
                                  'min_reparacion_s': 2, 'max_reparacion_s': 8,
                                  'seleccion': 'Mayor EX cumpliendo límites y determinismo; empate favorece directa'},
        'evaluacion': {'conjunto': 'datos/validacion/pares.jsonl', 'preguntas': 40, 'peso_total': 76,
                       'pesos': {'facil': 1, 'media': 2, 'dificil': 3}, 'redondeo': '2 decimales, ROUND_HALF_UP',
                       'duplicados': 'multiconjunto', 'orden': 'solo si requiere_orden',
                       'columnas': 'alineación inyectiva por valores; columnas adicionales permitidas',
                       'limites': {'segundos_por_pregunta': 30, 'llamadas_ejecutar': 3, 'filas_callback': 10,
                                   'max_execution_time_ms': 10000}},
        'sha256': {a: hash_archivo(ROOT / a) for a in archivos},
        'regla': 'No cambiar prompt, generación, datos ni criterio entre baseline, LoRA A y LoRA B. '
                 'Si cambian, repetir todas las mediciones afectadas.'}


def coincide_configuracion(congelada, solucion):
    """La igualdad del prompt no basta si cambian carga, limpieza o datos."""
    actual = configuracion(solucion)
    return all(congelada.get(k) == actual[k] for k in actual)


def main():
    os.environ['SOLUCION_CARGA_DIFERIDA'] = '1'
    sys.path.insert(0, str(ROOT))
    import solucion
    guardar_json(RUTA, configuracion(solucion))
    print(f'Configuración congelada en {RUTA.relative_to(ROOT)} (prompt {huella_prompt(solucion)[:12]})')


if __name__ == '__main__':
    main()
