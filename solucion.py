"""Contrato de entrega: texto a SQL para MySQL 8.4.10 con Qwen2.5-Coder y LoRA.

El modelo indicado en config.json se carga una sola vez al importar el módulo
(límite: 5 minutos). generar_sql() solo construye el prompt, genera de forma
determinista (greedy) y limpia la respuesta (límite: 30 segundos).

Con "usar_adapter": false se usa el modelo base con el MISMO prompt y la misma
configuración de generación; solo cambia la presencia del adapter.

Variables de entorno (solo para desarrollo y evaluación propia):
- SOLUCION_CARGA_DIFERIDA=1: no cargar al importar; llamar cargar() después.
"""
import json
import os
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
MODELOS_PERMITIDOS = {'Qwen/Qwen2.5-Coder-1.5B-Instruct', 'Qwen/Qwen2.5-Coder-0.5B-Instruct', 'Qwen/Qwen3-1.7B'}

# --- Prompt congelado. Cualquier cambio exige repetir baseline y adapters. ---
PROMPT_VERSION = 'v1'
INSTRUCCIONES = (
    'Eres un experto en MySQL 8.4. Recibes el esquema de una base de datos como sentencias '
    'CREATE TABLE con comentarios y una pregunta en español. Responde únicamente con una consulta '
    'SQL de solo lectura (SELECT o WITH ... SELECT) que responda la pregunta, sin explicaciones.\n'
    'Reglas:\n'
    '- Usa solo tablas y columnas que existan en el esquema; lee los comentarios.\n'
    '- Devuelve las columnas que pide la pregunta, en ese orden.\n'
    '- La consulta debe ser válida con ONLY_FULL_GROUP_BY: toda columna no agregada del SELECT va en GROUP BY.\n'
    '- Usa ORDER BY solo si la pregunta pide un orden o los primeros N resultados.\n'
    '- Nunca modifiques datos.'
)
# Presupuesto de generación congelado. max_time es solo una red de seguridad
# para el límite de 30 s; con 320 tokens no debería activarse en una T4.
MAX_TOKENS_NUEVOS = 320
MAX_SEGUNDOS_GENERACION = 25.0
CONSULTA_NEUTRA = 'SELECT 1'

_estado = {}


def leer_config(ruta=RAIZ / 'config.json'):
    config = json.loads(Path(ruta).read_text(encoding='utf-8'))
    faltan = {'modelo_base', 'adapter', 'usar_adapter', 'semilla'} - set(config)
    if faltan:
        raise ValueError(f'config.json incompleto; faltan {sorted(faltan)}')
    if config['modelo_base'] not in MODELOS_PERMITIDOS and not Path(config['modelo_base']).is_dir():
        raise ValueError(f'Modelo no permitido por el enunciado: {config["modelo_base"]}')
    if not isinstance(config['usar_adapter'], bool) or not isinstance(config['semilla'], int):
        raise ValueError('usar_adapter debe ser booleano y semilla entero')
    return config


def compactar_esquema(esquema):
    """Quita índices simples y opciones físicas de tabla; conserva columnas, PK, UNIQUE, FK y COMMENT."""
    salida = []
    for bloque in re.split(r';\s*(?=CREATE\s+TABLE\b)|;\s*$', esquema.strip(), flags=re.IGNORECASE):
        lineas = [l.rstrip() for l in bloque.strip().splitlines() if l.strip()]
        if not lineas:
            continue
        if not re.match(r'CREATE\s+TABLE\b', lineas[0], re.IGNORECASE) or not lineas[-1].lstrip().startswith(')'):
            salida.append(bloque.strip())  # Formato inesperado: conservar tal cual.
            continue
        cuerpo = [l.rstrip(',') for l in lineas[1:-1] if not re.match(r'\s*(KEY|INDEX|FULLTEXT KEY)\s', l)]
        cierre = lineas[-1]
        corte = cierre.find(' COMMENT=')
        opciones, comentario = (cierre, '') if corte < 0 else (cierre[:corte], cierre[corte:])
        opciones = re.sub(r'\s+(ENGINE|AUTO_INCREMENT|DEFAULT CHARSET|CHARSET|COLLATE|ROW_FORMAT|STATS_\w+)=\S+', '', opciones)
        cuerpo = [re.sub(r'\s+(CHARACTER SET \w+|COLLATE \w+)', '', l) for l in cuerpo]
        salida.append('\n'.join([lineas[0], ',\n'.join(cuerpo), opciones.rstrip() + comentario]))
    return ';\n\n'.join(salida) + ';'


def construir_mensajes(esquema, pregunta):
    """Mensajes de chat compartidos por base, adapter y entrenamiento."""
    return [{'role': 'system', 'content': INSTRUCCIONES},
            {'role': 'user', 'content': f'### Esquema\n{compactar_esquema(esquema)}\n\n### Pregunta\n{pregunta.strip()}'}]


def _enmascarar(sql):
    """Sustituye literales, identificadores con comillas y comentarios por espacios (misma longitud)."""
    resultado, i, n = list(sql), 0, len(sql)
    while i < n:
        c = sql[i]
        if c in '\'"`':
            j = i + 1
            while j < n:
                if sql[j] == '\\' and c != '`':
                    j += 2
                    continue
                if sql[j] == c:
                    if j + 1 < n and sql[j + 1] == c:  # comilla duplicada
                        j += 2
                        continue
                    break
                j += 1
            fin = min(j, n - 1)
            for k in range(i + 1, fin):
                resultado[k] = ' '
            i = fin + 1
        elif re.match(r'--(\s|$)', sql[i:i + 3]) or c == '#' or sql.startswith('/*', i):
            fin = sql.find('*/', i + 2) + 2 if c == '/' else sql.find('\n', i)
            fin = n if fin < (2 if c == '/' else 0) else fin
            for k in range(i, fin):
                resultado[k] = ' '
            i = fin
        else:
            i += 1
    return ''.join(resultado)


# Dentro de una sola sentencia SELECT/WITH, los riesgos reales son WITH ... UPDATE/DELETE,
# SELECT ... INTO, bloqueos FOR UPDATE y funciones que retienen el servidor. INSERT( y
# REPLACE( como funciones de texto sí se permiten.
PROHIBIDAS = re.compile(
    r'\b(?:(?:INSERT|UPDATE|DELETE|REPLACE)\b(?!\s*\()|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|'
    r'INTO|OUTFILE|DUMPFILE|SLEEP|BENCHMARK|GET_LOCK)\b', re.IGNORECASE)


def es_consulta_lectura(sql):
    """True si es exactamente una sentencia SELECT o WITH ... SELECT sin operaciones de escritura."""
    mascara = _enmascarar(sql).strip().rstrip(';').strip()
    return bool(re.match(r'(SELECT|WITH)\b', mascara, re.IGNORECASE)) and ';' not in mascara \
        and not PROHIBIDAS.search(mascara)


def limpiar_sql(texto):
    """Extrae una sola consulta de la respuesta del modelo; si no es de lectura devuelve CONSULTA_NEUTRA."""
    bloque = re.search(r'```(?:[a-zA-Z]*)\s*\n?(.*?)(?:```|$)', texto, re.DOTALL)
    candidato = bloque.group(1) if bloque else texto
    inicio = re.search(r'\b(SELECT|WITH)\b', _enmascarar(candidato), re.IGNORECASE)
    if not inicio:
        return CONSULTA_NEUTRA
    candidato = candidato[inicio.start():]
    fin = _enmascarar(candidato).find(';')
    if fin >= 0:
        candidato = candidato[:fin]
    candidato = re.split(r'\n\s*\n', candidato, maxsplit=1)[0]  # texto explicativo tras línea vacía
    candidato = candidato.strip()
    return candidato if es_consulta_lectura(candidato) else CONSULTA_NEUTRA


def cargar(usar_adapter=None, ruta_config=RAIZ / 'config.json'):
    """Carga tokenizer y modelo una sola vez. usar_adapter=None respeta config.json."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, set_seed

    config = leer_config(ruta_config)
    if usar_adapter is not None:
        config['usar_adapter'] = bool(usar_adapter)
    set_seed(config['semilla'])
    if torch.cuda.is_available():
        dispositivo, tipo = 'cuda', torch.float16  # T4: fp16 (sin bf16 nativo)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    elif torch.backends.mps.is_available():
        dispositivo, tipo = 'mps', torch.float16
    else:
        dispositivo, tipo = 'cpu', torch.float32
    tokenizer = AutoTokenizer.from_pretrained(config['modelo_base'])
    modelo = AutoModelForCausalLM.from_pretrained(config['modelo_base'], dtype=tipo)
    ruta_adapter = None
    if config['usar_adapter']:
        from peft import PeftModel
        ruta_adapter = (RAIZ / config['adapter']).resolve()
        if not (ruta_adapter / 'adapter_config.json').is_file():
            raise FileNotFoundError(f'usar_adapter=true pero no existe un adapter en {ruta_adapter}')
        modelo = PeftModel.from_pretrained(modelo, str(ruta_adapter)).merge_and_unload()
    modelo.to(dispositivo).eval()
    generacion = GenerationConfig(
        max_new_tokens=MAX_TOKENS_NUEVOS, max_time=MAX_SEGUNDOS_GENERACION, do_sample=False, num_beams=1,
        repetition_penalty=1.0, eos_token_id=modelo.generation_config.eos_token_id,
        pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id)
    # Reemplaza el generation_config.json de Qwen (do_sample, temperature, top_p, top_k,
    # repetition_penalty=1.1) para que generate() no complete valores con muestreo.
    modelo.generation_config = generacion
    _estado.update(config=config, tokenizer=tokenizer, modelo=modelo, dispositivo=dispositivo,
                   generacion=generacion, adapter=str(ruta_adapter) if ruta_adapter else None)
    return _estado


def generar_respuesta(esquema, pregunta):
    """Texto crudo del modelo, sin limpiar. Útil para análisis de errores."""
    import torch
    if not _estado:
        cargar()
    tokenizer, modelo = _estado['tokenizer'], _estado['modelo']
    texto = tokenizer.apply_chat_template(construir_mensajes(esquema, pregunta), tokenize=False,
                                          add_generation_prompt=True)
    entradas = tokenizer(texto, return_tensors='pt').to(_estado['dispositivo'])
    with torch.inference_mode():
        salida = modelo.generate(**entradas, generation_config=_estado['generacion'])
    return tokenizer.decode(salida[0, entradas['input_ids'].shape[1]:], skip_special_tokens=True)


def generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str:
    """Devuelve una sola consulta SELECT o WITH ... SELECT.

    Estrategia actual: generación directa, sin llamadas a `ejecutar` (0 de 3
    permitidas). El experimento de corrección con `ejecutar` corresponde al turno 3.
    """
    return limpiar_sql(generar_respuesta(esquema, pregunta))


if os.environ.get('SOLUCION_CARGA_DIFERIDA') != '1':
    cargar()
