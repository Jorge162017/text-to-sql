"""Referencias independientes en Python sobre filas fuente, sin ejecutar SQL analítico.

Permiten detectar joins multiplicados, filtros incorrectos, ceros omitidos,
desempates y pérdidas de duplicados. No utilizan resultados del modelo.
"""
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal


def promedio(valores):
    return sum(valores, Decimal(0)) / len(valores) if valores else None


def agrupar(filas, campo):
    grupos = defaultdict(list)
    for fila in filas:
        grupos[fila[campo]].append(fila)
    return grupos


def comercial(d, t, k):
    _, a, o, p, c, l, m, *_ = d
    a, o, p, c, l, m = (t[n] for n in (a, o, p, c, l, m))
    ai, ci = ({r['id']: r for r in filas} for filas in (a, c))
    oa, lp, lprod, mp = (agrupar(f, campo) for f, campo in [(o, 'cliente_id'), (l, 'pedido_id'), (l, 'producto_id'), (m, 'pedido_id')])
    importe = {i: sum(x['cantidad'] * x['precio_unitario'] for x in filas) for i, filas in lp.items()}
    categoria = [r for r in p if r['categoria_id'] == k]
    precios = sorted({r['precio'] for r in categoria}, reverse=True)
    fecha = date(2024, 1, 1) + timedelta(days=k * 30)
    ciudad = ['Guatemala', 'Antigua', 'Xela', 'Coban'][(k - 1) % 4]
    meses = Counter((r['fecha'].year, r['fecha'].month) for r in o if r['fecha'] >= fecha)
    porcat = agrupar(p, 'categoria_id')
    metodos = agrupar([r for r in m if r['fecha'] >= fecha], 'metodo')
    ultimas = [max(f, key=lambda r: (r['fecha'], r['id'])) for f in oa.values()]
    gasto = {i: sum(importe[x['id']] for x in f if x['id'] in importe) for i, f in oa.items()}
    ordenadas = sorted(oa.get(k, []), key=lambda r: (r['fecha'], r['id']))
    return {
        'filtro_id': [[r['id'], r['nombre']] for r in a if r['id'] == k],
        'filtro_ciudad': [[r['id'], r['nombre']] for r in a if r['ciudad'] == ciudad and r['id'] > k],
        'precio': [[r['id'], r['nombre'], r['precio']] for r in p if r['precio'] > k * 25],
        'rango_fecha': [[sum(r['fecha'] >= fecha for r in o)]],
        'top_precio': [[r['id'], r['nombre'], r['precio']] for r in sorted(p, key=lambda r: (-r['precio'], r['id']))[:k]],
        'null': [[r['id'], r['nombre']] for r in a if r['correo'] is None and r['id'] >= k],
        'activos': [[sum(r['activo'] == 1 for r in categoria)]],
        'promedio': [[promedio([r['precio'] for r in categoria])]],
        'join_actor': [[r['id'], r['fecha'], ai[k]['nombre']] for r in o if r['cliente_id'] == k],
        'join_categoria': [[r['nombre'], ci[k]['nombre']] for r in categoria],
        'total_lineas': [[r['id'], importe[r['id']]] for r in o if r['id'] > k and r['id'] in importe],
        'having': [[i, len(f)] for i, f in oa.items() if len(f) >= k],
        'left_join': [[r['id'], r['nombre']] for r in a if r['id'] > k and r['id'] not in oa],
        'suma_pagos': [[k, sum(x['importe'] for x in mp[k])]] if k in mp else [],
        'unidades': [[r['id'], sum(x['cantidad'] for x in lprod.get(r['id'], []))] for r in categoria],
        'cuenta_distinta': [[len({r['cliente_id'] for r in o if r['fecha'] >= fecha})]],
        'mes': [[y, mm, n] for (y, mm), n in meses.items()],
        'categoria_having': [[i, promedio([r['precio'] for r in f])] for i, f in porcat.items() if promedio([r['precio'] for r in f]) > k * 25],
        'join_tres': [[ai[k]['nombre'], r['id'], len(lp[r['id']])] for r in oa.get(k, []) if r['id'] in lp],
        'metodos': [[i, sum(r['importe'] for r in f)] for i, f in metodos.items()],
        'subconsulta': [[r['id'], r['nombre']] for r in categoria if r['precio'] > promedio([x['precio'] for x in categoria])],
        'not_exists': [[r['id']] for r in o if r['id'] > k and r['id'] not in mp],
        'cte': [[i, n] for i, n in importe.items() if n > k * 25],
        'ventana_ranking': [[r['id'], r['nombre'], k, precios.index(r['precio']) + 1] for r in categoria],
        'acumulado': [[r['id'], r['fecha'], i] for i, r in enumerate(ordenadas, 1)],
        'ultima': [[r['id'], r['cliente_id'], r['fecha']] for r in ultimas if r['cliente_id'] > k],
        'fecha_intervalo': [[r['id'], r['fecha']] for r in o if fecha <= r['fecha'] < fecha + timedelta(days=30)],
        'doble_agregacion': [[i, n] for i, n in gasto.items() if n > k * 25],
        'correlacion': [[r['id'], r['nombre']] for r in a if r['id'] > k and any(x['estado'] == 'completado' for x in oa.get(r['id'], []))],
        'anti_producto': [[r['id'], r['nombre']] for r in categoria if r['id'] not in lprod],
    }


def diverso(d, t, k):
    dominio, a, b, c, fk_a, valor, fk_b, medida, activo = d
    a, b, c = t[a], t[b], t[c]
    ai, bi = ({r['id']: r for r in f} for f in (a, b))
    ba, cb = agrupar(b, fk_a), agrupar(c, fk_b)
    fecha = date(2024, 1, 1) + timedelta(days=k * 20)
    acumuladas = sorted(cb.get(k, []), key=lambda r: (r['fecha'], r['id']))
    total = Decimal(0)
    acumulado = []
    for r in acumuladas:
        total += r[medida]
        acumulado.append([r['id'], r['fecha'], total])
    ultimas = [max(f, key=lambda r: (r['fecha'], r['id'])) for i, f in cb.items() if i <= k]
    salida = {
        'div_raiz': [[r['id'], r['nombre']] for r in a if r['id'] <= k],
        'div_activos': [[r['id'], r['nombre']] for r in b if r[activo] and r[valor] > k * 5],
        'div_top': [[r['id'], r['nombre'], r[valor]] for r in sorted(b, key=lambda r: (-r[valor], r['id']))[:k]],
        'div_fecha': [[r['id'], r['fecha']] for r in c if r['fecha'] >= fecha],
        'div_estado': [[sum(r['estado'] == 'ok' and r['id'] > k for r in c)]],
        'div_promedio': [[promedio([r[valor] for r in b if r['id'] > k])]],
        'div_join': [[r['nombre'], ai[r[fk_a]]['nombre']] for r in b if r[fk_a] <= k],
        'div_ceros': [[r['id'], len(cb.get(r['id'], []))] for r in b if r['id'] <= k],
        'div_having': [[i, len(f)] for i, f in ba.items() if len(f) >= k],
        'div_suma': [[i, sum(r[medida] for r in f)] for i, f in cb.items() if sum(r[medida] for r in f) > k * 20],
        'div_huerfanos': [[r['id'], r['nombre']] for r in b if r['id'] > k and r['id'] not in cb],
        'div_tres': [[i, sum(len(cb.get(r['id'], [])) for r in f)] for i, f in ba.items() if i <= k and sum(len(cb.get(r['id'], [])) for r in f)],
        'div_subconsulta': [[r['id'], r['nombre']] for r in b if r['id'] > k and r[valor] > promedio([x[valor] for x in ba[r[fk_a]]])],
        'div_ultima': [[r[fk_b], r['id'], r['fecha']] for r in ultimas],
        'div_cte': [[i, promedio([r[medida] for r in f])] for i, f in cb.items() if promedio([r[medida] for r in f]) > k * 5],
        'div_acumulado': acumulado,
    }
    if dominio == 'academia':
        salida['area_docente'] = [[r['id'], sum(len(ba.get(p['id'], [])) for p in a if p['area_id'] == r['id'])] for r in t['areas'] if r['id'] <= k]
        salida['alumnos_distintos'] = [[i, len({r['alumno_id'] for r in f})] for i, f in cb.items() if i > k]
        salida['prerrequisito'] = [[bi[r['asignatura_id']]['nombre'], bi[r['requerida_id']]['nombre']] for r in t['prerrequisitos'] if r['asignatura_id'] > k]
        requeridas = {r['asignatura_id'] for r in t['prerrequisitos']}
        salida['sin_requisito'] = [[r['id'], r['nombre']] for r in b if r['id'] > k and r['id'] not in requeridas]
    elif dominio == 'logistica':
        salida['origen_destino'] = [[r['nombre'], ai[r['origen_id']]['nombre'], ai[r['destino_id']]['nombre']] for r in b if r['id'] <= k]
        conductores, vehiculos = ({r['id']: r for r in t[n]} for n in ['conductores', 'vehiculos'])
        salida['conductor_vehiculo'] = [[r['id'], conductores[r['conductor_id']]['nombre'], vehiculos[r['vehiculo_id']]['nombre']] for r in c if r['id'] <= k]
        eventos = agrupar(t['eventos_envio'], 'envio_id')
        salida['sin_seguimiento'] = [[r['id']] for r in c if r['id'] > k and r['id'] not in eventos]
        salida['ultimo_evento'] = [[i, max(r['fecha'] for r in f)] for i, f in eventos.items() if i <= k]
    elif dominio == 'turismo':
        viajeros = {r['id']: r for r in t['viajeros']}
        salida['viajero_hotel'] = [[r['id'], viajeros[r['viajero_id']]['nombre'], bi[r['hotel_id']]['nombre']] for r in c if r['id'] <= k]
        habitaciones = Counter(r['hotel_id'] for r in t['habitaciones'])
        salida['habitaciones'] = [[r['id'], habitaciones[r['id']]] for r in b if r['id'] <= k]
        extras = agrupar(t['extras'], 'estancia_id')
        salida['extras_preagregados'] = [[i, sum(x['importe'] for r in f for x in extras.get(r['id'], []))] for i, f in cb.items() if i <= k]
        salida['sin_extras'] = [[r['id']] for r in c if r['id'] > k and r['id'] not in extras]
    elif dominio == 'energia':
        salida['regiones'] = [[r['id'], sum(len(ba.get(e['id'], [])) for e in a if e['region_id'] == r['id'])] for r in t['regiones'] if r['id'] <= k]
        alertas = Counter(r['medicion_id'] for r in t['alertas'])
        por_sensor = Counter()
        for r in c:
            por_sensor[r['sensor_id']] += alertas[r['id']]
        salida['alertas'] = [[i, n] for i, n in por_sensor.items() if i <= k and n]
        salida['umbral_correlacion'] = [[r['id'], r['valor']] for r in cb.get(k, []) if r['valor'] > bi[k]['umbral']]
        mantenidas = {r['estacion_id'] for r in t['mantenimientos']}
        salida['sin_mantenimiento'] = [[r['id'], r['nombre']] for r in a if r['id'] > k and r['id'] not in mantenidas]
    else:
        inspectores = Counter(r['inspector_id'] for r in c)
        salida['inspector'] = [[r['nombre'], inspectores[r['id']]] for r in t['inspectores'] if r['id'] <= k]
        consumos, por_lote = agrupar(t['consumos'], 'insumo_id'), agrupar(t['consumos'], 'lote_id')
        salida['consumos'] = [[r['id'], sum(x['cantidad'] for x in consumos.get(r['id'], []))] for r in t['insumos'] if r['id'] <= k]
        distintos = {i: len({r['insumo_id'] for r in f}) for i, f in por_lote.items()}
        salida['insumos_distintos'] = [[i, n] for i, n in distintos.items() if n >= k]
        salida['sin_controles'] = [[r['id'], r['nombre']] for r in b if r['id'] > k and r['id'] in por_lote and r['id'] not in cb]
    return salida


def validacion(b, h):
    miembros, titulos, autores, ejemplares = (b[n] for n in ['miembros', 'titulos', 'autores', 'ejemplares'])
    ti, ei = ({r['id']: r for r in f} for f in [titulos, ejemplares])
    prestamos = b['prestamos']
    pm = agrupar(prestamos, 'miembro_id')
    nlibros = Counter(r['autor_id'] for r in titulos)
    ntitulos = Counter(ei[r['ejemplar_id']]['titulo_id'] for r in prestamos)
    meses = Counter(r['inicio'].month for r in prestamos if r['inicio'].year == 2025)
    media = len(prestamos) / len(miembros)
    primer = {i: min(f, key=lambda r: (r['inicio'], r['id'])) for i, f in pm.items()}
    recientes = {i: min(f, key=lambda r: (-r['anio'], r['id'])) for i, f in agrupar(titulos, 'autor_id').items()}
    nombre_titulo = lambda p: ti[ei[p['ejemplar_id']]['titulo_id']]['nombre']
    s = {
        1: [[r['nombre'], r['anio']] for r in titulos],
        2: [[r['nombre'], r['anio']] for r in titulos if r['anio'] > 2020],
        3: [[r['nombre'], r['correo']] for r in miembros],
        4: [[r['id'], r['miembro_id'], r['inicio']] for r in prestamos if r['devolucion'] is None],
        5: [[r['nombre'], nlibros[r['id']]] for r in autores],
        6: [[r['nombre'], len(pm.get(r['id'], []))] for r in miembros if len(pm.get(r['id'], [])) > 3],
        7: [[nombre_titulo(r), r['inicio']] for r in prestamos],
        8: [[ti[i]['nombre'], n] for i, n in sorted(ntitulos.items(), key=lambda x: (-x[1], x[0]))[:5]],
        9: [[r['nombre'], len(pm.get(r['id'], []))] for r in miembros if len(pm.get(r['id'], [])) > media],
        10: [[r['nombre'], recientes[r['id']]['nombre'], recientes[r['id']]['anio']] for r in autores if r['id'] in recientes],
        11: [[r['nombre'], r['anio']] for r in titulos if r['anio'] < 2010],
        12: [[len(miembros)]],
        13: [[r['id'], r['inicio']] for r in prestamos if r['inicio'].year == 2025],
        14: [[len(titulos)]],
        15: [[r['nombre'], len(pm.get(r['id'], []))] for r in miembros],
        16: [[r['nombre'], nlibros[r['id']]] for r in autores if nlibros[r['id']] > 2],
        17: [[r['nombre'], nombre_titulo(p), p['inicio']] for r in miembros for p in pm.get(r['id'], []) if p['devolucion'] is None],
        18: [[r['nombre'], r['anio']] for r in titulos if r['id'] not in ntitulos],
        19: [[i, n] for i, n in sorted(meses.items(), key=lambda x: (-x[1], x[0]))[:1]],
        20: [[r['nombre'], nombre_titulo(primer[r['id']]), primer[r['id']]['inicio']] for r in miembros if r['id'] in primer],
    }
    personas, medicos, especialidades, citas = (h[n] for n in ['personas', 'medicos', 'especialidades', 'citas'])
    pi, mi, esi = ({r['id']: r for r in f} for f in [personas, medicos, especialidades])
    cp, cm = agrupar(citas, 'persona_id'), agrupar(citas, 'medico_id')
    atendidas = [r for r in citas if r['estado'] == 'atendida']
    ap, am = agrupar(atendidas, 'persona_id'), agrupar(atendidas, 'medico_id')
    media = len(citas) / len(personas)
    ultimas = {i: max(f, key=lambda r: (r['fecha'], r['id'])) for i, f in cp.items()}
    primeras = {i: min(f, key=lambda r: (r['fecha'], r['id'])) for i, f in cp.items()}
    meses = Counter(r['fecha'].month for r in citas if r['fecha'].year == 2025)
    especial = Counter(r['especialidad_id'] for r in medicos)
    s.update({
        21: [[r['nombre']] for r in personas],
        22: [[r['nombre'], r['nacimiento']] for r in personas if r['nacimiento'] > date(2000, 1, 1)],
        23: [[r['nombre'], esi[r['especialidad_id']]['nombre']] for r in medicos],
        24: [[r['id'], r['persona_id'], r['fecha']] for r in citas if r['estado'] == 'pendiente' and r['fecha'] > date(2026, 1, 1)],
        25: [[r['nombre'], len(cm.get(r['id'], []))] for r in medicos],
        26: [[r['nombre'], len(ap.get(r['id'], []))] for r in personas if len(ap.get(r['id'], [])) > 3],
        27: [[pi[r['persona_id']]['nombre'], mi[r['medico_id']]['nombre'], r['fecha']] for r in atendidas],
        28: [[r['nombre'], esi[r['especialidad_id']]['nombre'], len(am.get(r['id'], []))] for r in sorted(medicos, key=lambda r: (-len(am.get(r['id'], [])), r['id']))[:5]],
        29: [[r['nombre'], len(cp.get(r['id'], []))] for r in personas if len(cp.get(r['id'], [])) > media],
        30: [[r['nombre'], mi[ultimas[r['id']]['medico_id']]['nombre'], ultimas[r['id']]['fecha']] for r in personas if r['id'] in ultimas],
        31: [[len(medicos)]],
        32: [[r['nombre']] for r in medicos if esi[r['especialidad_id']]['nombre'] == 'Cardiologia'],
        33: [[len(personas)]],
        34: [[r['id'], r['fecha']] for r in atendidas if r['fecha'].year == 2025],
        35: [[r['nombre'], len({x['persona_id'] for x in am.get(r['id'], [])})] for r in medicos],
        36: [[r['nombre'], especial[r['id']]] for r in especialidades if especial[r['id']] > 2],
        37: [[pi[r['persona_id']]['nombre'], mi[r['medico_id']]['nombre'], r['fecha']] for r in atendidas if esi[mi[r['medico_id']]['especialidad_id']]['nombre'] == 'Cardiologia'],
        38: [[r['nombre'], esi[r['especialidad_id']]['nombre']] for r in medicos if r['id'] not in cm],
        39: [[i, n] for i, n in sorted(meses.items(), key=lambda x: (-x[1], x[0]))[:1]],
        40: [[r['nombre'], mi[primeras[r['id']]['medico_id']]['nombre'], primeras[r['id']]['fecha']] for r in personas if r['id'] in primeras],
    })
    return s
