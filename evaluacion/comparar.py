"""Comparación de resultados por ejecución, sin conexión a MySQL.

Reglas del enunciado (sección 4) y cómo se aplican:

- Se compara el resultado, no el texto SQL.
- Números (int, float, Decimal) se redondean a 2 decimales con ROUND_HALF_UP en ambos
  lados; así 5, 5.0 y Decimal('5.000') son iguales. Fechas y horas se comparan en ISO.
- El orden de filas solo cuenta si la pregunta lo exige (`requiere_orden`). Si no, se
  comparan multiconjuntos: las filas duplicadas cuentan tantas veces como aparecen.
- Una columna adicional no penaliza. Alineación: cada columna de la referencia debe
  corresponder a una columna distinta de la predicción cuyos valores coincidan. Los
  nombres/alias no deciden el acierto; solo ordenan la búsqueda (primero mismo nombre,
  después misma posición). Se acepta la primera asignación inyectiva cuya proyección
  reproduce exactamente la referencia, fila por fila.
- Filas de más o de menos siempre fallan.
"""
from collections import Counter
from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from itertools import islice

PESOS = {'facil': 1, 'media': 2, 'dificil': 3}
# Tipos de columna de PyMySQL (FIELD_TYPE) que representan números.
TIPOS_NUMERICOS = {0, 1, 2, 3, 4, 5, 8, 9, 13, 16, 246}
MAX_ASIGNACIONES = 20000
CENTESIMA = Decimal('0.01')


def normalizar_celda(valor):
    if valor is None:
        return None
    if isinstance(valor, bool):
        valor = int(valor)
    if isinstance(valor, (int, float, Decimal)):
        try:
            return Decimal(str(valor)).quantize(CENTESIMA, rounding=ROUND_HALF_UP)
        except InvalidOperation:  # NaN o infinito
            return str(valor)
    if isinstance(valor, (datetime, date, time)):
        return valor.isoformat()
    if isinstance(valor, timedelta):
        return str(valor)
    if isinstance(valor, (bytes, bytearray)):
        return bytes(valor).decode('utf-8', errors='replace')
    return valor


def normalizar_filas(filas):
    return [tuple(normalizar_celda(v) for v in fila) for fila in filas]


def rehidratar(filas, tipos_mysql):
    """Convierte evidencia JSON (decimales como texto) a valores comparables."""
    return [[Decimal(v) if v is not None and t in TIPOS_NUMERICOS and isinstance(v, str) else v
             for v, t in zip(fila, tipos_mysql, strict=True)] for fila in filas]


def _iguales(a, b, orden):
    return a == b if orden else Counter(a) == Counter(b)


def comparar_resultados(columnas_ref, filas_ref, columnas_pred, filas_pred, requiere_orden):
    """Devuelve (acierto, mapeo, motivo). mapeo[j] = índice de la columna predicha para la columna j."""
    if len(filas_pred) != len(filas_ref):
        return False, None, f'filas: se esperaban {len(filas_ref)} y hubo {len(filas_pred)}'
    k = len(columnas_ref)
    if len(columnas_pred) < k:
        return False, None, f'columnas: se esperaban al menos {k} y hubo {len(columnas_pred)}'
    ref, pred = normalizar_filas(filas_ref), normalizar_filas(filas_pred)
    if any(len(f) != k for f in ref) or any(len(f) != len(columnas_pred) for f in pred):
        raise ValueError('Filas con número de columnas inconsistente')

    def firma(filas, j):  # condición necesaria, con o sin orden
        return Counter(f[j] for f in filas)

    nombres_pred = [str(c).lower() for c in columnas_pred]
    candidatos = []
    for j, nombre in enumerate(columnas_ref):
        objetivo = firma(ref, j)
        opciones = [i for i in range(len(columnas_pred)) if firma(pred, i) == objetivo]
        if not opciones:
            return False, None, f'ninguna columna coincide con {nombre!r}'
        opciones.sort(key=lambda i: (nombres_pred[i] != str(nombre).lower(), i != j, i))
        candidatos.append(opciones)

    def asignaciones(j, usadas):
        if j == k:
            yield []
            return
        for i in candidatos[j]:
            if i not in usadas:
                for resto in asignaciones(j + 1, usadas | {i}):
                    yield [i, *resto]

    sin_orden = False
    for mapeo in islice(asignaciones(0, frozenset()), MAX_ASIGNACIONES):
        proyeccion = [tuple(f[i] for i in mapeo) for f in pred]
        if _iguales(proyeccion, ref, requiere_orden):
            return True, mapeo, 'ok'
        sin_orden = sin_orden or (requiere_orden and _iguales(proyeccion, ref, False))
    return False, None, 'orden distinto' if sin_orden else 'valores distintos por fila'


def categoria_error_mysql(codigo):
    """Categoría automática para errores de ejecución. JOIN/filtro se clasifican en el turno 4."""
    if codigo == 1064:
        return 'sintaxis'
    if codigo in {1054, 1146, 1049}:
        return 'columna_tabla_inexistente'
    if codigo in {1055, 1056, 1111, 1140, 3029}:
        return 'agregacion'
    if codigo == 3024:
        return 'tiempo_ejecucion'
    return 'error_ejecucion'


def resumir(registros):
    """EX global, por nivel y por esquema; denominador = suma de pesos de todas las preguntas."""
    def bloque(filas):
        total = sum(r['peso'] for r in filas)
        logrado = sum(r['peso'] for r in filas if r['acierto'])
        return {'preguntas': len(filas), 'aciertos': sum(r['acierto'] for r in filas),
                'peso_aciertos': logrado, 'peso_total': total,
                'ex': round(logrado / total, 4) if total else None}
    niveles = [n for n in PESOS if any(r['nivel'] == n for r in registros)]
    esquemas = sorted({r['esquema_id'] for r in registros})
    return {**bloque(registros),
            'por_nivel': {n: bloque([r for r in registros if r['nivel'] == n]) for n in niveles},
            'por_esquema': {e: bloque([r for r in registros if r['esquema_id'] == e]) for e in esquemas},
            'categorias': dict(Counter(r['categoria'] for r in registros))}
