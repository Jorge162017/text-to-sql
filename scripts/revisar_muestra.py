"""Revisa todos los pares con cálculos Python independientes sobre tablas fuente.

Conserva el nombre del comando usado por las etapas anteriores. La revisión
es automática, asistida por IA; no constituye autoría o revisión humana.
"""
from datetime import date, datetime, timezone
from decimal import Decimal
import json

from scripts.comun import DATOS, ROOT, conectar, guardar_json, leer_jsonl
from scripts.generar_datos import DOMINIOS
from scripts.dominios_diversos import DOMINIOS_DIVERSOS
from scripts.oraculos import comercial, diverso, validacion
from scripts.validar_datos import cargar_particiones, comprobar_motor, hash_archivo

NUMERICOS = {0, 1, 2, 3, 4, 5, 8, 9, 13, 16, 246}


def normalizar(filas, tipos):
    def celda(v, tipo):
        if v is None:
            return None
        if tipo in NUMERICOS:
            return str(Decimal(str(v)).quantize(Decimal('0.01')))
        return v.isoformat() if isinstance(v, (date, datetime)) else v
    return [tuple(celda(v, tipo) for v, tipo in zip(fila, tipos, strict=True)) for fila in filas]


def comparar(actual, esperado, orden):
    a, e = normalizar(actual['filas'], actual['tipos_mysql']), normalizar(esperado, actual['tipos_mysql'])
    if orden:
        return a == e
    # Ordenar no elimina duplicados. JSON permite comparar también NULL/texto.
    clave = lambda fila: json.dumps(fila, ensure_ascii=False)
    return sorted(a, key=clave) == sorted(e, key=clave)


def cargar_tablas(cursor, nombre):
    cursor.execute(f'USE `{nombre}`')
    cursor.execute('SHOW TABLES')
    nombres = [r[0] for r in cursor.fetchall()]
    tablas = {}
    for tabla in nombres:
        cursor.execute(f'SELECT * FROM `{tabla}`')
        columnas = [r[0] for r in cursor.description]
        tablas[tabla] = [dict(zip(columnas, fila, strict=True)) for fila in cursor.fetchall()]
    return tablas


def main():
    particiones = cargar_particiones()
    train = leer_jsonl(DATOS / 'entrenamiento' / 'pares.jsonl')
    propias = leer_jsonl(DATOS / 'validacion' / 'pares.jsonl')
    evidencia = {r['id']: r for r in leer_jsonl(ROOT / 'resultados' / 'ejecucion_entrenamiento.jsonl')}
    refs = {r['id']: r for r in leer_jsonl(DATOS / 'validacion' / 'referencias_resultados.jsonl')}
    conexion = conectar()
    try:
        with conexion.cursor() as cursor:
            comprobar_motor(cursor)
            cursor.execute('START TRANSACTION READ ONLY')
            tablas = {n: cargar_tablas(cursor, n) for n in particiones['entrenamiento'] + particiones['validacion']}
            conexion.rollback()
    finally:
        conexion.close()
    comerciales = {'train_' + d[0]: d for d in DOMINIOS}
    diversos = {'train_' + d[0]: d for d in DOMINIOS_DIVERSOS}
    cache, revisiones = {}, []
    for r in train:
        nombre, k = r['esquema_id'], int(r['id'].rsplit('_', 1)[1])
        clave = (nombre, k)
        if clave not in cache:
            funcion, d = (comercial, comerciales[nombre]) if nombre in comerciales else (diverso, diversos[nombre])
            cache[clave] = funcion(d, tablas[nombre], k)
        esperado = cache[clave][r['familia']]
        orden = r['familia'] in {'top_precio', 'acumulado', 'div_top', 'div_acumulado'}
        ok = comparar(evidencia[r['id']], esperado, orden)
        revisiones.append({'id': r['id'], 'particion': 'entrenamiento', 'familia': r['familia'], 'ok': ok})
    referencias = validacion(tablas['val_biblioteca'], tablas['val_hospital'])
    for r in propias:
        ok = comparar(refs[r['id']], referencias[r['numero']], r['requiere_orden'])
        revisiones.append({'id': r['id'], 'particion': 'validacion', 'ok': ok})
    fuentes = [ROOT / 'resultados' / 'ejecucion_entrenamiento.jsonl', DATOS / 'entrenamiento' / 'pares.jsonl',
               DATOS / 'validacion' / 'referencias_resultados.jsonl', DATOS / 'validacion' / 'pares.jsonl',
               ROOT / 'scripts' / 'revisar_muestra.py', ROOT / 'scripts' / 'oraculos.py']
    fuentes += [DATOS / 'esquemas' / n / 'seed.sql' for n in tablas]
    guardar_json(ROOT / 'resultados' / 'revision_semantica.json', {
        'fecha_utc': datetime.now(timezone.utc).isoformat(),
        'tipo': 'Comprobación automática asistida por IA con algoritmos Python; no revisión humana',
        'muestra': len(revisiones), 'correctos': sum(r['ok'] for r in revisiones),
        'entrenamiento_revisados': len(train), 'validacion_revisados': len(propias),
        'limite': 'Cubre los datos sintéticos actuales y las familias declaradas; no garantiza generalización a bases desconocidas.',
        'sha256': {str(p.relative_to(ROOT)): hash_archivo(p) for p in fuentes},
        'revisiones': revisiones})
    errores = [r['id'] for r in revisiones if not r['ok']]
    print(f'Revisión semántica: {len(revisiones) - len(errores)}/{len(revisiones)} correctos')
    if errores:
        print('Discrepancias:', errores[:30])
        raise SystemExit(1)


if __name__ == '__main__':
    main()
