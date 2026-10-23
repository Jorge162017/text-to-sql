"""Estrategia experimental: corregir errores MySQL, sin ejemplos de validación.

No altera el contrato de entrega hasta comparar en T4. El primer intento usa
exactamente la generación directa. Las filas del callback no se usan como juez
semántico: una consulta ejecutable puede seguir siendo incorrecta.
"""
from copy import deepcopy
import time

VERSION = 'correccion_errores_v1'
INSTRUCCION = ('La consulta anterior falló en MySQL 8.4.10 con ONLY_FULL_GROUP_BY. '
               'Corrígela usando solo el esquema y la pregunta originales. '
               'Devuelve únicamente una consulta SELECT o WITH ... SELECT, sin explicaciones.\nError MySQL: ')
PRESUPUESTO_S = 29.0
RESERVA_CALLBACK_S = 10.5  # arnés propio: MAX_EXECUTION_TIME=10000 ms
MIN_REPARACION_S = 2.0
MAX_REPARACION_S = 8.0
MAX_LLAMADAS = 3


def generar_reparacion(solucion, mensajes, segundos):
    import torch
    estado = solucion._estado
    tokenizer = estado['tokenizer']
    texto = tokenizer.apply_chat_template(mensajes, tokenize=False, add_generation_prompt=True)
    entradas = tokenizer(texto, return_tensors='pt').to(estado['dispositivo'])
    config = deepcopy(estado['generacion'])
    config.max_time = segundos
    with torch.inference_mode():
        salida = estado['modelo'].generate(**entradas, generation_config=config)
    return tokenizer.decode(salida[0, entradas['input_ids'].shape[1]:], skip_special_tokens=True)


def generar_sql(solucion, esquema, pregunta, ejecutar=None, *, traza=None,
                reloj=time.monotonic, reparar=None):
    """Hasta 3 callbacks; sin callback equivale a directa. Nunca consulta referencias.

    max_time de Transformers se comprueba entre pasos y no es un corte duro.
    El evaluador registra cualquier exceso real de 30 s y descarta la estrategia
    si no respeta los límites; el callback debe respetar su timeout de 10 s.
    """
    traza = traza if traza is not None else []
    limite = reloj() + PRESUPUESTO_S
    sql = solucion.generar_sql(esquema, pregunta)
    if ejecutar is None or sql == solucion.CONSULTA_NEUTRA:
        return sql
    mensajes = solucion.construir_mensajes(esquema, pregunta)
    reparar = reparar or (lambda m, s: generar_reparacion(solucion, m, s))
    ultimo = sql
    vistos = set()
    for intento in range(MAX_LLAMADAS):
        if sql in vistos or not solucion.es_consulta_lectura(sql):
            break
        if limite - reloj() < RESERVA_CALLBACK_S:
            traza.append({'evento': 'sin_presupuesto_callback'})
            break
        vistos.add(sql)
        try:
            resultado = ejecutar(sql)
        except Exception as exc:
            traza.append({'evento': 'callback_excepcion', 'tipo': type(exc).__name__})
            break
        traza.append({'evento': 'callback', 'sql': sql, 'ok': bool(resultado.get('ok')),
                      'error': str(resultado.get('error') or '')[:1500]})
        if resultado.get('ok'):
            return sql
        if intento == MAX_LLAMADAS - 1:
            break
        disponible = limite - reloj() - RESERVA_CALLBACK_S
        if disponible < MIN_REPARACION_S:
            traza.append({'evento': 'sin_presupuesto_reparacion'})
            break
        mensajes += [{'role': 'assistant', 'content': sql},
                     {'role': 'user', 'content': INSTRUCCION + str(resultado.get('error') or 'Error desconocido')[:1500]}]
        try:
            nuevo = solucion.limpiar_sql(reparar(mensajes, min(MAX_REPARACION_S, disponible)))
        except Exception as exc:
            traza.append({'evento': 'reparacion_excepcion', 'tipo': type(exc).__name__})
            break
        if nuevo == solucion.CONSULTA_NEUTRA or not solucion.es_consulta_lectura(nuevo):
            break
        ultimo = sql = nuevo
    return ultimo
