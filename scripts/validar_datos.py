"""Importa bases propias y certifica candidatos ejecutándolos en MySQL 8.4.10.

Usar --inicializar solo en el servidor de desarrollo del proyecto.
No elimina bases existentes. --recrear permite reconstruir solo las del manifiesto.
"""
import argparse
from collections import Counter
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
import re
import secrets
import time

from scripts.comun import DATOS, ROOT, conectar, guardar_json, guardar_jsonl, leer_jsonl


def hash_archivo(ruta):
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def cargar_particiones():
    particiones = json.loads((DATOS / 'particiones.json').read_text())
    train, val = particiones['entrenamiento'], particiones['validacion']
    if len(train) != len(set(train)) or len(val) != len(set(val)) or set(train) & set(val):
        raise ValueError('Particiones duplicadas o fuga de esquemas entre entrenamiento y validación.')
    if len(train) < 10 or len(val) < 2:
        raise ValueError('Se requieren al menos 10 esquemas train y 2 de validación.')
    for nombre in train + val:
        if not re.fullmatch(r'(train|val)_[a-z][a-z0-9_]*', nombre):
            raise ValueError(f'Nombre de esquema inválido: {nombre}')
    return particiones


def comprobar_registro(registro, permitidos):
    for campo in ['id', 'esquema_id', 'pregunta', 'sql', 'nivel', 'procedencia']:
        if not isinstance(registro.get(campo), str) or not registro[campo].strip():
            raise ValueError(f'Campo inválido: {campo}')
    if re.search(r'\b(?:train|val)_[a-z0-9_]+\s*\.', registro['sql'], re.IGNORECASE):
        raise ValueError('No se permiten referencias SQL a otros esquemas')
    if registro['esquema_id'] not in permitidos:
        raise ValueError('Esquema fuera de la partición permitida')
    if registro['nivel'] not in {'facil', 'media', 'dificil'}:
        raise ValueError('Nivel desconocido')
    if registro.get('peso') != {'facil': 1, 'media': 2, 'dificil': 3}[registro['nivel']]:
        raise ValueError('Peso no corresponde a nivel')
    sql = registro['sql'].strip().rstrip(';').strip()
    # Contrato conservador para candidatos propios. La seguridad efectiva es
    # el usuario SELECT + transacción READ ONLY, no esta comprobación textual.
    if not re.match(r'^(SELECT|WITH)\b', sql, re.IGNORECASE) or ';' in sql:
        raise ValueError('Se exige una única consulta SELECT o WITH')
    if re.search(r'\b(INTO|OUTFILE|DUMPFILE|SLEEP|BENCHMARK|GET_LOCK)\b', sql, re.IGNORECASE):
        raise ValueError('Consulta con efectos laterales no admitidos')


def comprobar_autoria(registros):
    if len(registros) < 40:
        raise ValueError('Faltan preguntas propias: se requieren al menos 40')
    if len({r['esquema_id'] for r in registros}) < 2:
        raise ValueError('Las preguntas propias deben cubrir al menos dos esquemas')
    if {r['nivel'] for r in registros} != {'facil', 'media', 'dificil'}:
        raise ValueError('Faltan niveles de dificultad')
    if len({r['id'] for r in registros}) != len(registros):
        raise ValueError('Identificadores de preguntas propias duplicados')
    for r in registros:
        if r.get('autor') not in {'Jorge Lopez', 'Angel Herrarte'} or r.get('estado') != 'redactada_por_integrante':
            raise ValueError('Falta autoría humana declarada; los borradores IA no cumplen el requisito')
        if not r.get('fecha_redaccion') or r.get('procedencia') != 'redaccion_propia':
            raise ValueError('Falta fecha/procedencia de redacción propia')
        date.fromisoformat(r['fecha_redaccion'])
        if not isinstance(r.get('requiere_orden'), bool) or not r.get('columnas_esperadas'):
            raise ValueError('Faltan reglas de columnas u orden')


def comprobar_motor(cursor):
    cursor.execute('SELECT VERSION(), @@SESSION.sql_mode')
    version, modo = cursor.fetchone()
    if version.split('-')[0] != '8.4.10':
        raise RuntimeError(f'Versión incorrecta: {version}; se exige MySQL 8.4.10')
    if 'ONLY_FULL_GROUP_BY' not in modo.split(','):
        raise RuntimeError('ONLY_FULL_GROUP_BY no está activo')
    return version, modo


def importar(cursor, nombres, recrear):
    # Solo se ejecutan archivos SQL propios, generados por los scripts del repo.
    # El cliente admin admite scripts; el lector de candidatos NO admite
    # múltiples sentencias. MySQL interpreta los ';' dentro de COMMENT.
    for nombre in nombres:
        cursor.execute('SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = %s', (nombre,))
        if cursor.fetchone():
            if not recrear:
                raise RuntimeError(f'{nombre} ya existe. Omite --inicializar para validar; --recrear elimina y repuebla SOLO bases del manifiesto.')
            cursor.execute(f'DROP DATABASE `{nombre}`')
        cursor.execute(f'CREATE DATABASE `{nombre}` CHARACTER SET utf8mb4')
        cursor.execute(f'USE `{nombre}`')
        for archivo in ['schema.sql', 'seed.sql']:
            texto = (DATOS / 'esquemas' / nombre / archivo).read_text(encoding='utf-8')
            cursor.execute(texto)
            while cursor.nextset():
                pass


def serializar(valor):
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return str(valor)
    raise TypeError(type(valor).__name__)


def ejecutar_lote(conexion, registros, permitidos, esquemas, validar_columnas=False):
    aceptados, descartes, resultados = [], [], []
    ids, ejemplos = set(), set()
    import pymysql
    for r in registros:
        inicio = time.perf_counter()
        try:
            comprobar_registro(r, permitidos)
            clave = (r['esquema_id'], r['pregunta'].strip(), r['sql'].strip())
            if r['id'] in ids or clave in ejemplos:
                raise ValueError('Registro duplicado por id o por esquema/pregunta/SQL')
            ids.add(r['id'])
            ejemplos.add(clave)
            with conexion.cursor() as cursor:
                cursor.execute(f"USE `{r['esquema_id']}`")
                cursor.execute('START TRANSACTION READ ONLY')
                try:
                    cursor.execute(r['sql'])
                    columnas = [c[0] for c in cursor.description]
                    tipos = [c[1] for c in cursor.description]
                    filas = cursor.fetchall()
                    if validar_columnas and columnas != r['columnas_esperadas']:
                        raise ValueError(f'Columnas distintas: {columnas}')
                finally:
                    conexion.rollback()
            aceptados.append({**r, 'esquema': esquemas[r['esquema_id']],
                              'validado_mysql': '8.4.10', 'filas_resultado': len(filas)})
            resultados.append({'id': r['id'], 'columnas': columnas,
                               'tipos_mysql': tipos,
                               'filas': json.loads(json.dumps(filas, default=serializar)),
                               'segundos': round(time.perf_counter() - inicio, 6)})
        except (ValueError, pymysql.MySQLError) as exc:
            # Un fallo de conexión no es un par inválido: abortar la certificación.
            if isinstance(exc, pymysql.err.OperationalError) and exc.args[0] in {2002, 2003, 2006, 2013}:
                raise
            descartes.append({**r, 'motivo': str(exc),
                              'categoria': 'mysql' if isinstance(exc, pymysql.MySQLError) else 'integridad',
                              'codigo_mysql': exc.args[0] if isinstance(exc, pymysql.MySQLError) else None})
    return aceptados, descartes, resultados


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inicializar', action='store_true')
    parser.add_argument('--recrear', action='store_true', help='Elimina y repuebla únicamente las bases propias del manifiesto')
    args = parser.parse_args()
    if args.recrear and not args.inicializar:
        parser.error('--recrear requiere --inicializar')
    particiones = cargar_particiones()
    nombres = particiones['entrenamiento'] + particiones['validacion']
    ruta_train = DATOS / 'candidatos' / 'entrenamiento.jsonl'
    ruta_propias = DATOS / 'validacion' / 'preguntas_propias.jsonl'
    train = leer_jsonl(ruta_train)
    propias = leer_jsonl(ruta_propias)
    comprobar_autoria(propias)
    admin = conectar(permitir_scripts=True)
    lector = None
    usuario = 'sqlv_' + secrets.token_hex(6)
    clave = secrets.token_hex(24)
    creado = False
    try:
        with admin.cursor() as cursor:
            version, modo = comprobar_motor(cursor)
            if args.inicializar:
                importar(cursor, nombres, args.recrear)
            esquemas = {}
            for nombre in nombres:
                cursor.execute(f'USE `{nombre}`')
                cursor.execute('SHOW TABLES')
                tablas = [r[0] for r in cursor.fetchall()]
                sentencias = []
                for t in tablas:
                    cursor.execute(f'SHOW CREATE TABLE `{t}`')
                    sentencias.append(cursor.fetchone()[1] + ';')
                esquemas[nombre] = '\n\n'.join(sentencias)
                (DATOS / 'esquemas' / nombre / 'show_create.sql').write_text(esquemas[nombre] + '\n', encoding='utf-8')
            cursor.execute('CREATE USER %s@%s IDENTIFIED BY %s', (usuario, '%', clave))
            creado = True
            for nombre in nombres:
                cursor.execute(f'GRANT SELECT ON `{nombre}`.* TO %s@%s', (usuario, '%'))
        import pymysql
        lector = pymysql.connect(host=admin.host, port=admin.port, user=usuario, password=clave,
                                 charset='utf8mb4', autocommit=True, read_timeout=10)
        with lector.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME = 3000')
            comprobar_motor(cursor)
        aceptados, descartes, evidencia = ejecutar_lote(lector, train, particiones['entrenamiento'], esquemas)
        p_ok, p_desc, p_resultados = ejecutar_lote(lector, propias, particiones['validacion'], esquemas, True)
    finally:
        if lector is not None:
            lector.close()
        try:
            if creado:
                with admin.cursor() as cursor:
                    cursor.execute('DROP USER %s@%s', (usuario, '%'))
        finally:
            admin.close()
    guardar_jsonl(DATOS / 'entrenamiento' / 'pares.jsonl', aceptados)
    guardar_jsonl(DATOS / 'descartes' / 'entrenamiento.jsonl', descartes)
    guardar_jsonl(DATOS / 'descartes' / 'validacion_propia.jsonl', p_desc)
    guardar_jsonl(DATOS / 'validacion' / 'pares.jsonl', p_ok)
    guardar_jsonl(DATOS / 'validacion' / 'referencias_resultados.jsonl', p_resultados)
    guardar_jsonl(ROOT / 'resultados' / 'ejecucion_entrenamiento.jsonl', evidencia)
    rutas = [DATOS / 'particiones.json', ruta_train, ruta_propias]
    rutas += [DATOS / 'esquemas' / n / f for n in nombres for f in ['schema.sql', 'seed.sql', 'show_create.sql']]
    rutas += sorted((ROOT / 'scripts').glob('*.py'))
    rutas += [DATOS / 'entrenamiento' / 'pares.jsonl', DATOS / 'validacion' / 'pares.jsonl',
              DATOS / 'descartes' / 'entrenamiento.jsonl', DATOS / 'descartes' / 'validacion_propia.jsonl',
              DATOS / 'validacion' / 'referencias_resultados.jsonl', ROOT / 'resultados' / 'ejecucion_entrenamiento.jsonl']
    listo = len(aceptados) >= 2000 and len({r['esquema_id'] for r in aceptados}) >= 10 and len(p_ok) >= 40 and not p_desc
    reporte = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'mysql_version': version,
               'sql_mode': modo, 'candidatos': len(train), 'aceptados_entrenamiento': len(aceptados),
               'descartados_entrenamiento': len(descartes), 'motivos_descartes': dict(Counter(r['motivo'] for r in descartes)),
               'por_esquema': dict(Counter(r['esquema_id'] for r in aceptados)),
               'por_nivel': dict(Counter(r['nivel'] for r in aceptados)),
               'familias_plantillas': len({r['familia'] for r in aceptados}),
               'resultados_vacios': sum(r['filas_resultado'] == 0 for r in aceptados),
               'validacion_por_nivel': dict(Counter(r['nivel'] for r in p_ok)),
               'validacion_por_autor': dict(Counter(r['autor'] for r in p_ok)),
               'validacion_por_esquema': dict(Counter(r['esquema_id'] for r in p_ok)),
               'validacion_peso_total': sum(r['peso'] for r in p_ok),
               'validacion_resultados_vacios': [r['id'] for r in p_ok if r['filas_resultado'] == 0],
               'preguntas_propias_ejecutables': len(p_ok), 'preguntas_propias_descartadas': len(p_desc),
               'etapa_1_completa': listo,
               'pendiente': [] if listo else ['Redactar 40 preguntas propias y volver a validar; revisar mínimos y descartes.'],
               'sha256': {str(p.relative_to(ROOT)): hash_archivo(p) for p in rutas}}
    guardar_json(ROOT / 'resultados' / 'reporte_datos.json', reporte)
    print(json.dumps({k: v for k, v in reporte.items() if k != 'sha256'}, ensure_ascii=False, indent=2))
    if len(aceptados) < 2000 or len({r['esquema_id'] for r in aceptados}) < 10 or p_desc:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
