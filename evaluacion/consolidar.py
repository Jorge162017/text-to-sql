"""Consolida la validación propia de todas las configuraciones en resultados/validacion_propia.csv.

Une las predicciones de cada corrida con la clasificación manual de errores
(resultados/clasificacion_errores.json) y escribe además resultados/analisis_errores.json
con conteos por categoría y EX por dificultad. No ejecuta el modelo ni MySQL.

    python -m evaluacion.consolidar
"""
import csv
import json
from collections import Counter

from scripts.comun import ROOT, guardar_json, leer_jsonl

EVALUACIONES = ROOT / 'resultados' / 'evaluaciones'
# Configuración -> (corrida, adapter, estrategia, es_entrega). Base y A usan la auditoría final del turno 4.
CONFIGURACIONES = {
    'base': ('auditoria_final_base', 'ninguno', 'directa', False),
    'a': ('auditoria_final_a', 'lora_a_r8', 'directa', True),
    'b': ('lora_b', 'lora_b_r16', 'directa', False),
    'base_correccion': ('inferencia_base_correccion', 'ninguno', 'correccion', False),
    'a_correccion': ('inferencia_a_correccion', 'lora_a_r8', 'correccion', False),
}
CATEGORIAS = ['sintaxis', 'columna_tabla_inexistente', 'join', 'agregacion', 'filtro', 'resultado_distinto']
# Errores de ejecución: el código MySQL decide la categoría (ver regla en clasificacion_errores.json).
POR_CODIGO = {1064: 'sintaxis', 1235: 'sintaxis', 1054: 'columna_tabla_inexistente',
              1146: 'columna_tabla_inexistente', 1055: 'agregacion', 1111: 'agregacion', 1247: 'agregacion'}
CAMPOS = ['configuracion', 'corrida', 'adapter', 'estrategia', 'entrega', 'id', 'esquema_id', 'nivel', 'peso',
          'requiere_orden', 'pregunta', 'sql_referencia', 'sql_generado', 'ejecucion', 'codigo_mysql', 'error_mysql',
          'filas_generadas', 'filas_referencia', 'acierto', 'latencia_s', 'llamadas_ejecutar',
          'categoria_automatica', 'categoria_error', 'causa']


def filas_configuracion(nombre, manual):
    corrida, adapter, estrategia, entrega = CONFIGURACIONES[nombre]
    resumen = json.loads((EVALUACIONES / corrida / 'resumen.json').read_text())
    filas = []
    for p in leer_jsonl(EVALUACIONES / corrida / 'predicciones.jsonl'):
        clasificacion = manual.get(p['id'], {}).get(nombre)
        if p['acierto']:
            if clasificacion:
                raise ValueError(f'{nombre}/{p["id"]}: acierto con clasificación manual')
            categoria, causa = '', ''
        else:
            if not clasificacion:
                raise ValueError(f'{nombre}/{p["id"]}: fallo sin clasificación manual')
            categoria, causa = clasificacion
            if categoria not in CATEGORIAS:
                raise ValueError(f'{nombre}/{p["id"]}: categoría desconocida {categoria}')
            if p['codigo_mysql'] is not None and POR_CODIGO.get(p['codigo_mysql']) != categoria:
                raise ValueError(f'{nombre}/{p["id"]}: el código {p["codigo_mysql"]} exige {POR_CODIGO.get(p["codigo_mysql"])}')
        ejecuta = p['codigo_mysql'] is None and p['categoria'] not in {'formato_invalido', 'excepcion'}
        filas.append({
            'configuracion': nombre, 'corrida': corrida, 'adapter': adapter, 'estrategia': estrategia,
            'entrega': entrega, 'id': p['id'], 'esquema_id': p['esquema_id'], 'nivel': p['nivel'], 'peso': p['peso'],
            'requiere_orden': p['requiere_orden'], 'pregunta': p['pregunta'], 'sql_referencia': p['sql_referencia'],
            'sql_generado': p['sql_generado'], 'ejecucion': 'ok' if ejecuta else 'error',
            'codigo_mysql': p['codigo_mysql'] or '', 'error_mysql': '' if ejecuta else p['motivo'],
            'filas_generadas': '' if p['filas_generadas'] is None else p['filas_generadas'],
            'filas_referencia': p['filas_referencia'], 'acierto': p['acierto'], 'latencia_s': p['latencia_s'],
            'llamadas_ejecutar': p['llamadas_ejecutar'], 'categoria_automatica': '' if p['acierto'] else p['categoria'],
            'categoria_error': categoria, 'causa': causa})
    peso = sum(f['peso'] for f in filas if f['acierto'])
    if peso != resumen['peso_aciertos']:
        raise ValueError(f'{nombre}: {peso} no coincide con resumen {resumen["peso_aciertos"]}')
    return filas, resumen


def main():
    manual = json.loads((ROOT / 'resultados' / 'clasificacion_errores.json').read_text())['fallos']
    todas, analisis = [], {}
    for nombre in CONFIGURACIONES:
        filas, resumen = filas_configuracion(nombre, manual)
        todas += filas
        fallos = [f for f in filas if not f['acierto']]
        analisis[nombre] = {
            'corrida': CONFIGURACIONES[nombre][0], 'ex': resumen['ex'], 'peso_aciertos': resumen['peso_aciertos'],
            'peso_total': resumen['peso_total'], 'por_nivel': resumen['por_nivel'], 'por_esquema': resumen['por_esquema'],
            'fallos': len(fallos), 'peso_fallado': sum(f['peso'] for f in fallos),
            'categorias': {c: n for c, n in Counter(f['categoria_error'] for f in fallos).most_common()},
            'peso_por_categoria': {c: sum(f['peso'] for f in fallos if f['categoria_error'] == c) for c in CATEGORIAS},
            'ids_fallados': [f['id'] for f in fallos]}
    salida = ROOT / 'resultados' / 'validacion_propia.csv'
    with salida.open('w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(todas)
    guardar_json(ROOT / 'resultados' / 'analisis_errores.json',
                 {'fuente': 'resultados/validacion_propia.csv', 'categorias': CATEGORIAS,
                  'configuraciones': {n: {'corrida': c, 'adapter': a, 'estrategia': e, 'entrega': s}
                                      for n, (c, a, e, s) in CONFIGURACIONES.items()},
                  'analisis': analisis})
    for nombre, a in analisis.items():
        print(f'{nombre:16s} {a["peso_aciertos"]}/{a["peso_total"]} fallos={a["fallos"]} {a["categorias"]}')


if __name__ == '__main__':
    main()
