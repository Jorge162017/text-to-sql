"""Auditoría sin conexión de fuentes, resultados, particiones y revisión semántica."""
import argparse
from collections import Counter
import json
from itertools import permutations
import re

from scripts.comun import DATOS, ROOT, leer_jsonl
from scripts.validar_datos import cargar_particiones, comprobar_autoria, comprobar_registro, hash_archivo


def verificar_hashes(reporte, requeridos):
    hashes = reporte.get('sha256', {})
    if not set(requeridos) <= set(hashes):
        raise ValueError('La evidencia no contiene todos los archivos requeridos')
    for nombre, esperado in hashes.items():
        ruta = ROOT / nombre
        if not ruta.is_file() or hash_archivo(ruta) != esperado:
            raise ValueError(f'Evidencia desactualizada: {nombre}; repetir certificación y revisión semántica.')


def verificar_lote(registros, particion):
    ids, claves = set(), set()
    for r in registros:
        comprobar_registro(r, particion)
        clave = (r['esquema_id'], r['pregunta'].strip(), r['sql'].strip())
        if r['id'] in ids or clave in claves:
            raise ValueError('Registro duplicado')
        ids.add(r['id'])
        claves.add(clave)


def topologias(nombres):
    """Compara grafos dirigidos de FK sin depender de nombres de tablas."""
    grupos = {}
    for nombre in nombres:
        ddl = (DATOS / 'esquemas' / nombre / 'schema.sql').read_text()
        # Los COMMENT propios pueden contener ';': extraer por siguiente CREATE.
        bloques = re.findall(r'CREATE TABLE `([^`]+)` (.*?)(?=CREATE TABLE|\Z)', ddl, re.DOTALL)
        tablas = [n for n, _ in bloques]
        aristas = Counter((tabla, destino) for tabla, bloque in bloques
                          for destino in re.findall(r'REFERENCES\s+`?([a-z_]+)`?', bloque))
        if not 5 <= len(tablas) <= 10:
            raise ValueError(f'Cantidad de tablas fuera del rango previsto: {nombre}')
        # Los esquemas actuales tienen seis tablas (720 permutaciones).
        firma = min(tuple(aristas[(a, b)] for a in orden for b in orden) for orden in permutations(tablas))
        grupos.setdefault((len(tablas), firma), []).append(nombre)
    return list(grupos.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exigir-cierre', action='store_true')
    args = parser.parse_args()
    p = cargar_particiones()
    train = leer_jsonl(DATOS / 'candidatos' / 'entrenamiento.jsonl')
    propias = leer_jsonl(DATOS / 'validacion' / 'preguntas_propias.jsonl')
    verificar_lote(train, p['entrenamiento'])
    verificar_lote(propias, p['validacion'])
    comprobar_autoria(propias)
    grafos = topologias(p['entrenamiento'])
    reporte_ruta = ROOT / 'resultados' / 'reporte_datos.json'
    muestra_ruta = ROOT / 'resultados' / 'revision_semantica.json'
    completo, aceptados = False, []
    if reporte_ruta.exists() and muestra_ruta.exists():
        reporte, muestra = (json.loads(r.read_text()) for r in [reporte_ruta, muestra_ruta])
        requeridos = ['datos/particiones.json', 'datos/candidatos/entrenamiento.jsonl',
                      'datos/entrenamiento/pares.jsonl', 'datos/validacion/preguntas_propias.jsonl',
                      'datos/validacion/pares.jsonl', 'datos/validacion/referencias_resultados.jsonl',
                      'datos/descartes/entrenamiento.jsonl', 'datos/descartes/validacion_propia.jsonl',
                      'resultados/ejecucion_entrenamiento.jsonl']
        requeridos += [str(f.relative_to(ROOT)) for f in (ROOT / 'scripts').glob('*.py')]
        requeridos += [f'datos/esquemas/{n}/{f}' for n in p['entrenamiento'] + p['validacion'] for f in ['schema.sql', 'seed.sql', 'show_create.sql']]
        verificar_hashes(reporte, requeridos)
        verificar_hashes(muestra, ['resultados/ejecucion_entrenamiento.jsonl', 'datos/validacion/referencias_resultados.jsonl'])
        aceptados = leer_jsonl(DATOS / 'entrenamiento' / 'pares.jsonl')
        val = leer_jsonl(DATOS / 'validacion' / 'pares.jsonl')
        evidencia = leer_jsonl(ROOT / 'resultados' / 'ejecucion_entrenamiento.jsonl')
        referencias = leer_jsonl(DATOS / 'validacion' / 'referencias_resultados.jsonl')
        verificar_lote(aceptados, p['entrenamiento'])
        verificar_lote(val, p['validacion'])
        comprobar_autoria(val)
        if {r['id'] for r in evidencia} != {r['id'] for r in aceptados} or len(evidencia) != len(aceptados):
            raise ValueError('Evidencia de entrenamiento incompleta o duplicada')
        if {r['id'] for r in referencias} != {r['id'] for r in val} or len(referencias) != len(val):
            raise ValueError('Referencias de validación incompletas o duplicadas')
        revisiones = muestra.get('revisiones', [])
        esperados = {r['id'] for r in aceptados + val}
        if len(revisiones) != len(esperados) or {r['id'] for r in revisiones} != esperados or not all(r['ok'] for r in revisiones):
            raise ValueError('Revisión semántica ausente, incompleta o con discrepancias')
        if reporte['aceptados_entrenamiento'] != len(aceptados) or reporte['preguntas_propias_ejecutables'] != len(val):
            raise ValueError('Conteos del reporte incorrectos')
        descartes = leer_jsonl(DATOS / 'descartes' / 'entrenamiento.jsonl')
        if len(train) != len(aceptados) + len(descartes):
            raise ValueError('Candidatos sin clasificar')
        if len(aceptados) < 2000 or len({r['esquema_id'] for r in aceptados}) < 10 or len(val) != len(propias):
            raise ValueError('Mínimos de datos no cumplidos')
        if not reporte.get('etapa_1_completa'):
            raise ValueError('La certificación no declara mínimos cumplidos')
        completo = True
    salida = {'candidatos': len(train), 'pares_train_certificados': len(aceptados),
              'esquemas_train': len(p['entrenamiento']), 'esquemas_val': len(p['validacion']),
              'preguntas_propias': len(propias), 'niveles_validacion': dict(Counter(r['nivel'] for r in propias)),
              'autores_declarados': dict(Counter(r['autor'] for r in propias)),
              'peso_total_validacion': sum(r['peso'] for r in propias), 'etapa_1_completa': completo,
              'topologias_entrenamiento': len(grafos),
              'pendiente': [] if completo else ['Ejecutar certificación MySQL y revisión semántica completas.']}
    print(json.dumps(salida, ensure_ascii=False, indent=2))
    if args.exigir_cierre and not completo:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
