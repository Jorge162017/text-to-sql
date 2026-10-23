"""Evalúa solucion.generar_sql sobre la validación propia (40 preguntas, peso 76) en MySQL 8.4.10.

Imita el arnés del enunciado: entrega el esquema SHOW CREATE TABLE, la pregunta y un
callback ejecutar(sql) de solo lectura con máximo 3 llamadas y 10 filas. Las
referencias se reejecutan y deben coincidir con la evidencia del turno 1.

Ejemplos:
    python -m evaluacion.evaluar --nombre oraculo --oraculo        # control: EX debe ser 1.0
    python -m evaluacion.evaluar --nombre baseline --adapter no
    python -m evaluacion.evaluar --nombre lora_a --adapter si
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import secrets
import statistics
import subprocess
import sys
import time

from evaluacion.congelar import RUTA as RUTA_CONGELADA, huella_prompt, coincide_configuracion
from evaluacion.comparar import categoria_error_mysql, comparar_resultados, rehidratar, resumir
from scripts.comun import DATOS, ROOT, conectar, guardar_json, guardar_jsonl, leer_jsonl
from scripts.validar_datos import cargar_particiones, comprobar_motor, importar, serializar

LIMITE_LLAMADAS = 3
LIMITE_FILAS_CALLBACK = 10
LIMITE_SEGUNDOS = 30.0
MAX_EXECUTION_MS = 10000


def ejecutar_sql(conexion, esquema_id, sql):
    """Ejecuta en transacción READ ONLY. Devuelve dict con ok, columnas, filas, error y código."""
    import pymysql
    try:
        with conexion.cursor() as cursor:
            cursor.execute(f'USE `{esquema_id}`')
            cursor.execute('START TRANSACTION READ ONLY')
            try:
                cursor.execute(sql)
                columnas = [c[0] for c in cursor.description] if cursor.description else []
                filas = [list(f) for f in cursor.fetchall()]
            finally:
                conexion.rollback()
        return {'ok': True, 'columnas': columnas, 'filas': filas, 'error': None, 'codigo': None}
    except pymysql.MySQLError as exc:
        if isinstance(exc, pymysql.err.OperationalError) and exc.args[0] in {2002, 2003, 2006, 2013}:
            raise  # caída de conexión: no es un error del modelo
        return {'ok': False, 'columnas': [], 'filas': [], 'error': str(exc), 'codigo': exc.args[0]}


def crear_callback(conexion, esquema_id, es_lectura):
    llamadas = []

    def ejecutar(sql):
        llamadas.append(sql)
        if len(llamadas) > LIMITE_LLAMADAS:
            return {'ok': False, 'columnas': [], 'filas': [], 'error': f'Límite de {LIMITE_LLAMADAS} llamadas por pregunta'}
        if not isinstance(sql, str) or not es_lectura(sql):
            return {'ok': False, 'columnas': [], 'filas': [], 'error': 'Solo se admite una consulta SELECT o WITH'}
        r = ejecutar_sql(conexion, esquema_id, sql)
        return {'ok': r['ok'], 'columnas': r['columnas'], 'filas': r['filas'][:LIMITE_FILAS_CALLBACK], 'error': r['error']}
    return ejecutar, llamadas


def comprobar_sin_fuga(validacion):
    usados = {r['esquema_id'] for r in leer_jsonl(DATOS / 'entrenamiento' / 'pares.jsonl')}
    if usados & set(validacion):
        raise RuntimeError(f'Fuga: esquemas de validación en entrenamiento: {usados & set(validacion)}')


def git_estado():
    def correr(*args):
        try:
            return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    estado = correr('status', '--porcelain')
    return {'commit': correr('rev-parse', 'HEAD'), 'cambios_sin_commit': bool(estado) if estado is not None else None}


def entorno(solucion, cargado):
    info = {'python': platform.python_version(), 'plataforma': platform.platform()}
    try:
        import torch
        import transformers
        import peft
        info.update(torch=torch.__version__, transformers=transformers.__version__, peft=peft.__version__,
                    gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)
    except ImportError:
        pass
    if cargado:
        info['dispositivo'] = cargado['dispositivo']
    return info


def preparar_bases(admin, validacion, inicializar):
    with admin.cursor() as cursor:
        version, modo = comprobar_motor(cursor)
        cursor.execute('SELECT SCHEMA_NAME FROM information_schema.SCHEMATA')
        existentes = {r[0] for r in cursor.fetchall()}
        faltan = [n for n in validacion if n not in existentes]
        if faltan and not inicializar:
            raise SystemExit(f'Faltan bases {faltan}. Repite con --inicializar (solo crea las que faltan).')
        if faltan:
            importar(cursor, faltan, recrear=False)
    return version, modo


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--nombre', required=True, help='Carpeta de salida en resultados/evaluaciones/')
    parser.add_argument('--adapter', choices=['config', 'si', 'no'], default='config')
    parser.add_argument('--estrategia', choices=['directa', 'correccion'], default='directa')
    parser.add_argument('--oraculo', action='store_true', help='Usa el SQL de referencia como predicción (control)')
    parser.add_argument('--limite', type=int, help='Evaluar solo las primeras N preguntas (pruebas rápidas)')
    parser.add_argument('--inicializar', action='store_true', help='Importa las bases de validación que falten')
    parser.add_argument('--reemplazar', action='store_true', help='Sobrescribe una evaluación existente')
    args = parser.parse_args()

    salida = ROOT / 'resultados' / 'evaluaciones' / args.nombre
    if (salida / 'resumen.json').exists() and not args.reemplazar:
        raise SystemExit(f'{salida} ya existe; usa otro --nombre o --reemplazar.')
    validacion = cargar_particiones()['validacion']
    comprobar_sin_fuga(validacion)
    pares = leer_jsonl(DATOS / 'validacion' / 'pares.jsonl')[:args.limite]
    evidencia = {r['id']: r for r in leer_jsonl(DATOS / 'validacion' / 'referencias_resultados.jsonl')}

    os.environ['SOLUCION_CARGA_DIFERIDA'] = '1'
    sys.path.insert(0, str(ROOT))
    import solucion
    congelada = json.loads(RUTA_CONGELADA.read_text()) if RUTA_CONGELADA.exists() else None
    coincide = coincide_configuracion(congelada, solucion) if congelada else None
    if congelada and not coincide:
        raise SystemExit('La configuración experimental está desactualizada. Congela la nueva versión y repite '
                         'las evaluaciones afectadas sin sobrescribir las históricas.')
    cargado, tiempo_carga = None, None
    if not args.oraculo:
        inicio = time.perf_counter()
        cargado = solucion.cargar(usar_adapter={'config': None, 'si': True, 'no': False}[args.adapter])
        tiempo_carga = round(time.perf_counter() - inicio, 2)
        print(f'Modelo cargado en {tiempo_carga} s (adapter={cargado["config"]["usar_adapter"]})', flush=True)

    admin = conectar(permitir_scripts=True)
    lector, usuario, clave, creado = None, 'sqle_' + secrets.token_hex(6), secrets.token_hex(24), False
    registros = []
    try:
        version, modo = preparar_bases(admin, validacion, args.inicializar)
        with admin.cursor() as cursor:
            cursor.execute('CREATE USER %s@%s IDENTIFIED BY %s', (usuario, '%', clave))
            creado = True
            for nombre in validacion:
                cursor.execute(f'GRANT SELECT ON `{nombre}`.* TO %s@%s', (usuario, '%'))
        import pymysql
        lector = pymysql.connect(host=admin.host, port=admin.port, user=usuario, password=clave,
                                 charset='utf8mb4', autocommit=True, read_timeout=35)
        with lector.cursor() as cursor:
            cursor.execute(f'SET SESSION MAX_EXECUTION_TIME = {MAX_EXECUTION_MS}')
            comprobar_motor(cursor)

        for n, par in enumerate(pares, 1):
            ref = ejecutar_sql(lector, par['esquema_id'], par['sql'])
            guardada = evidencia[par['id']]
            vigente = ref['ok'] and ref['columnas'] == guardada['columnas'] and comparar_resultados(
                guardada['columnas'], rehidratar(guardada['filas'], guardada['tipos_mysql']),
                ref['columnas'], ref['filas'], par['requiere_orden'])[0]
            if not vigente:
                raise RuntimeError(f'{par["id"]}: la referencia ya no coincide con la evidencia; revisar bases/semillas.')

            ejecutar, llamadas = crear_callback(lector, par['esquema_id'], solucion.es_consulta_lectura)
            inicio = time.perf_counter()
            excepcion = None
            traza = []
            try:
                if args.oraculo:
                    sql = par['sql']
                elif args.estrategia == 'correccion':
                    from evaluacion.correccion import generar_sql as corregir
                    sql = corregir(solucion, par['esquema'], par['pregunta'], ejecutar, traza=traza)
                else:
                    sql = solucion.generar_sql(par['esquema'], par['pregunta'], ejecutar)
            except Exception as exc:  # el contrato no debe lanzar; se registra como fallo
                sql, excepcion = '', f'{type(exc).__name__}: {exc}'
            latencia = round(time.perf_counter() - inicio, 3)
            respuesta_cruda = None

            pred, acierto, motivo = None, False, None
            if excepcion:
                categoria, motivo = 'excepcion', excepcion
            elif not isinstance(sql, str) or not solucion.es_consulta_lectura(sql):
                categoria, motivo = 'formato_invalido', 'No es una única consulta SELECT/WITH de solo lectura'
            else:
                pred = ejecutar_sql(lector, par['esquema_id'], sql)
                if not pred['ok']:
                    categoria, motivo = categoria_error_mysql(pred['codigo']), pred['error']
                else:
                    acierto, _, motivo = comparar_resultados(par['columnas_esperadas'], ref['filas'], pred['columnas'],
                                                             pred['filas'], par['requiere_orden'])
                    categoria = 'correcto' if acierto else 'resultado_distinto'
            if sql == solucion.CONSULTA_NEUTRA and not args.oraculo:
                categoria, acierto = 'formato_invalido', False
            if latencia > LIMITE_SEGUNDOS or len(llamadas) > LIMITE_LLAMADAS:
                categoria, acierto = 'limite_excedido', False
                motivo = f'latencia {latencia} s, llamadas {len(llamadas)}'

            registros.append({
                'id': par['id'], 'numero': par['numero'], 'esquema_id': par['esquema_id'], 'nivel': par['nivel'],
                'peso': par['peso'], 'requiere_orden': par['requiere_orden'], 'pregunta': par['pregunta'],
                'columnas_esperadas': par['columnas_esperadas'], 'sql_referencia': par['sql'], 'sql_generado': sql,
                'respuesta_cruda': respuesta_cruda, 'traza_inferencia': traza, 'acierto': acierto, 'categoria': categoria, 'motivo': motivo,
                'codigo_mysql': pred['codigo'] if pred else None,
                'columnas_generadas': pred['columnas'] if pred else None,
                'filas_generadas': len(pred['filas']) if pred and pred['ok'] else None,
                'muestra_filas': json.loads(json.dumps(pred['filas'][:5], default=serializar)) if pred and pred['ok'] else None,
                'filas_referencia': len(ref['filas']), 'latencia_s': latencia, 'llamadas_ejecutar': len(llamadas)})
            print(f'[{n:02d}/{len(pares)}] {par["id"]} {par["nivel"]:<7} {"OK " if acierto else "MAL"} '
                  f'{categoria:<26} {latencia:6.2f} s', flush=True)
    finally:
        if lector is not None:
            lector.close()
        try:
            if creado:
                with admin.cursor() as cursor:
                    cursor.execute('DROP USER %s@%s', (usuario, '%'))
        finally:
            admin.close()

    latencias = [r['latencia_s'] for r in registros]
    config = cargado['config'] if cargado else solucion.leer_config()
    huella = huella_prompt(solucion)
    resumen = {
        'nombre': args.nombre, 'fecha_utc': datetime.now(timezone.utc).isoformat(),
        'modo': 'oraculo' if args.oraculo else 'modelo', 'completa': args.limite is None,
        'config': config, 'adapter_cargado': cargado['adapter'] if cargado else None,
        'prompt_version': solucion.PROMPT_VERSION, 'prompt_sha256': huella,
        'coincide_configuracion_congelada': coincide,
        'configuracion_sha256': hashlib.sha256(RUTA_CONGELADA.read_bytes()).hexdigest() if congelada else None,
        'limpieza_version': solucion.LIMPIEZA_VERSION,
        'revision_modelo': cargado['revision_modelo'] if cargado else None,
        'generacion': cargado['generacion'].to_diff_dict() if cargado else None,
        'estrategia': args.estrategia,
        'correccion_version': __import__('evaluacion.correccion', fromlist=['VERSION']).VERSION if args.estrategia == 'correccion' else None,
        'mysql': {'version': version, 'sql_mode': modo},
        'tiempo_carga_s': tiempo_carga,
        'latencia_s': {'media': round(statistics.mean(latencias), 3), 'mediana': round(statistics.median(latencias), 3),
                       'max': max(latencias), 'mayores_a_30s': sum(x > LIMITE_SEGUNDOS for x in latencias)} if latencias else None,
        'llamadas_ejecutar': {'total': sum(r['llamadas_ejecutar'] for r in registros),
                              'max_por_pregunta': max((r['llamadas_ejecutar'] for r in registros), default=0)},
        'git': git_estado(), 'entorno': entorno(solucion, cargado),
        **resumir(registros)}
    guardar_jsonl(salida / 'predicciones.jsonl', registros)
    guardar_json(salida / 'resumen.json', resumen)
    print(json.dumps({k: resumen[k] for k in ['nombre', 'ex', 'peso_aciertos', 'peso_total', 'por_nivel',
                                               'categorias', 'latencia_s', 'tiempo_carga_s']},
                     ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
