"""Cinco dominios adicionales con relaciones distintas del esquema comercial.

Solo entrenamiento. No importa ni consulta datos de validación.
"""
from datetime import date, timedelta

from scripts.generar_datos import tabla, insertar


# dominio, raíz, recurso, evento, FK raíz, valor de recurso, FK recurso,
# medida de evento, bandera activo. Las tablas adicionales cambian cada grafo.
DOMINIOS_DIVERSOS = [
    ('academia', 'profesores', 'asignaturas', 'inscripciones', 'profesor_id', 'creditos', 'asignatura_id', 'nota', 'activa'),
    ('logistica', 'centros', 'rutas', 'envios', 'origen_id', 'distancia', 'ruta_id', 'peso', 'activa'),
    ('turismo', 'destinos', 'hoteles', 'estancias', 'destino_id', 'tarifa', 'hotel_id', 'noches', 'activo'),
    ('energia', 'estaciones', 'sensores', 'mediciones', 'estacion_id', 'umbral', 'sensor_id', 'valor', 'activo'),
    ('manufactura', 'fabricas', 'lotes', 'controles', 'fabrica_id', 'costo', 'lote_id', 'defectos', 'activo'),
]


def construir(d):
    dominio, a, b, c, fk_a, valor, fk_b, medida, activo = d
    tablas, semillas = [], []

    def agregar(nombre, columnas, filas, comentario):
        tablas.append(tabla(nombre, columnas, comentario))
        semillas.append(insertar(nombre, filas))

    def entidad(nombre, extra_columnas=(), extra_valores=None):
        filas = [(i, f'{nombre.title()} {i:02}', *(extra_valores(i) if extra_valores else ())) for i in range(1, 9)]
        agregar(nombre, ['id INT PRIMARY KEY', 'nombre VARCHAR(80) NOT NULL', *extra_columnas], filas, f'Catalogo propio de {dominio}')

    if dominio == 'academia':
        entidad('areas')
        entidad(a, ['area_id INT NOT NULL', 'FOREIGN KEY (area_id) REFERENCES areas(id)'], lambda i: ((i - 1) % 6 + 1,))
        entidad('alumnos')
    elif dominio == 'energia':
        entidad('regiones')
        entidad(a, ['region_id INT NOT NULL', 'FOREIGN KEY (region_id) REFERENCES regiones(id)'], lambda i: ((i - 1) % 6 + 1,))
    else:
        entidad(a)
        for nombre in {'logistica': ['vehiculos', 'conductores'], 'turismo': ['viajeros'], 'manufactura': ['inspectores', 'insumos']}[dominio]:
            entidad(nombre)

    columnas_b = ['id INT PRIMARY KEY', 'nombre VARCHAR(80) NOT NULL', f'{fk_a} INT NOT NULL',
                  f'{valor} DECIMAL(10,2) NOT NULL', f'{activo} BOOLEAN NOT NULL',
                  f'FOREIGN KEY ({fk_a}) REFERENCES {a}(id)']
    if dominio == 'logistica':
        columnas_b += ['destino_id INT NOT NULL', 'FOREIGN KEY (destino_id) REFERENCES centros(id)']
    filas_b = [(i, f'{b.title()} {i:02}', (i - 1) % 6 + 1, i * 3 + 0.5, int(i % 5 != 0),
                *((i % 6 + 1,) if dominio == 'logistica' else ())) for i in range(1, 25)]
    agregar(b, columnas_b, filas_b, f'Recursos de {dominio}; {valor} es un valor del catalogo')

    if dominio == 'turismo':
        agregar('habitaciones', ['id INT PRIMARY KEY', 'hotel_id INT NOT NULL', 'numero INT NOT NULL',
                                 'FOREIGN KEY (hotel_id) REFERENCES hoteles(id)'],
                [(i, i, 101) for i in range(1, 25)], 'Habitaciones fisicas de cada hotel')
    columnas_c = ['id INT PRIMARY KEY', f'{fk_b} INT NOT NULL', 'fecha DATE NOT NULL',
                  f'{medida} DECIMAL(10,2) NOT NULL', "estado VARCHAR(20) NOT NULL COMMENT 'ok, pendiente o anulado'",
                  f'FOREIGN KEY ({fk_b}) REFERENCES {b}(id)']
    extras = {
        'academia': (['alumno_id INT NOT NULL', 'FOREIGN KEY (alumno_id) REFERENCES alumnos(id)'], lambda i: (i % 8 + 1,)),
        'logistica': (['vehiculo_id INT NOT NULL', 'conductor_id INT NOT NULL', 'FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id)', 'FOREIGN KEY (conductor_id) REFERENCES conductores(id)'], lambda i: (i % 8 + 1, (i * 3) % 8 + 1)),
        'turismo': (['viajero_id INT NOT NULL', 'habitacion_id INT NOT NULL', 'FOREIGN KEY (viajero_id) REFERENCES viajeros(id)', 'FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id)'], lambda i: (i % 8 + 1, (i * 7) % 20 + 1)),
        'energia': ([], lambda i: ()),
        'manufactura': (['inspector_id INT NOT NULL', 'FOREIGN KEY (inspector_id) REFERENCES inspectores(id)'], lambda i: (i % 8 + 1,)),
    }
    extra_cols, extra_filas = extras[dominio]
    columnas_c += extra_cols
    filas_c = [(i, (i * 7) % 20 + 1, str(date(2024, 1, 1) + timedelta(days=i * 5)),
                ((i * 11) % 9 + 1 if medida == 'noches' else (i * 11) % 7 if medida == 'defectos' else (i * 11) % 90 + 0.5), ['ok', 'pendiente', 'anulado'][i % 3], *extra_filas(i)) for i in range(1, 121)]
    agregar(c, columnas_c, filas_c, f'Eventos de {dominio}; la medida es {medida}, no dinero salvo indicacion')
    if dominio == 'academia':
        agregar('prerrequisitos', ['id INT PRIMARY KEY', 'asignatura_id INT NOT NULL', 'requerida_id INT NOT NULL',
                                  'FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id)', 'FOREIGN KEY (requerida_id) REFERENCES asignaturas(id)'],
                [(i, i + 1, i) for i in range(1, 20)], 'Dependencia dirigida entre asignaturas')
    elif dominio == 'logistica':
        agregar('eventos_envio', ['id INT PRIMARY KEY', 'envio_id INT NOT NULL', 'fecha DATE NOT NULL', 'descripcion VARCHAR(50) NOT NULL', 'FOREIGN KEY (envio_id) REFERENCES envios(id)'],
                [(i, (i * 3) % 120 + 1, str(date(2024, 1, 1) + timedelta(days=((i * 3) % 120 + 1) * 5 + 1)), 'seguimiento') for i in range(1, 81)], 'Seguimiento: varias filas por envio')
    elif dominio == 'turismo':
        agregar('extras', ['id INT PRIMARY KEY', 'estancia_id INT NOT NULL', 'importe DECIMAL(10,2) NOT NULL', 'FOREIGN KEY (estancia_id) REFERENCES estancias(id)'],
                [(i, (i * 3) % 120 + 1, i * 2.5) for i in range(1, 81)], 'Cargos adicionales por estancia; no confundir con noches')
    elif dominio == 'energia':
        agregar('alertas', ['id INT PRIMARY KEY', 'medicion_id INT NOT NULL', 'nivel VARCHAR(20) NOT NULL', 'FOREIGN KEY (medicion_id) REFERENCES mediciones(id)'],
                [(i, i * 2, 'alto' if i % 2 else 'medio') for i in range(1, 41)], 'Alertas asociadas a mediciones')
        agregar('mantenimientos', ['id INT PRIMARY KEY', 'estacion_id INT NOT NULL', 'fecha DATE NOT NULL', 'costo DECIMAL(10,2) NOT NULL', 'FOREIGN KEY (estacion_id) REFERENCES estaciones(id)'],
                [(i, i % 6 + 1, str(date(2024, 1, 1) + timedelta(days=i * 10)), i * 12.5) for i in range(1, 31)], 'Intervenciones en estaciones, no en sensores')
    else:
        agregar('consumos', ['id INT PRIMARY KEY', 'lote_id INT NOT NULL', 'insumo_id INT NOT NULL', 'cantidad DECIMAL(10,2) NOT NULL', 'FOREIGN KEY (lote_id) REFERENCES lotes(id)', 'FOREIGN KEY (insumo_id) REFERENCES insumos(id)'],
                [(i, i % 24 + 1, i % 8 + 1, i * 1.5) for i in range(1, 61)], 'Relacion de muchos a muchos entre lotes e insumos')
    return tablas, semillas


def consultas_especificas(dominio, k):
    if dominio == 'academia':
        return [
            ('media', 'area_docente', f'Por area con id hasta {k}, devuelve id de area y cantidad de asignaturas de sus profesores.', f'SELECT a.id, COUNT(s.id) AS total FROM areas a LEFT JOIN profesores p ON p.area_id = a.id LEFT JOIN asignaturas s ON s.profesor_id = p.id WHERE a.id <= {k} GROUP BY a.id'),
            ('media', 'alumnos_distintos', f'Por asignatura con id mayor que {k}, devuelve asignatura_id y numero de alumnos distintos inscritos.', f'SELECT asignatura_id, COUNT(DISTINCT alumno_id) AS alumnos FROM inscripciones WHERE asignatura_id > {k} GROUP BY asignatura_id'),
            ('media', 'prerrequisito', f'Devuelve nombre de asignatura y nombre de su prerrequisito para asignaturas con id mayor que {k}.', f'SELECT a.nombre AS asignatura, r.nombre AS requerida FROM prerrequisitos p JOIN asignaturas a ON a.id = p.asignatura_id JOIN asignaturas r ON r.id = p.requerida_id WHERE a.id > {k}'),
            ('dificil', 'sin_requisito', f'Lista id y nombre de asignaturas sin prerrequisitos y con id mayor que {k}.', f'SELECT a.id, a.nombre FROM asignaturas a WHERE a.id > {k} AND NOT EXISTS (SELECT 1 FROM prerrequisitos p WHERE p.asignatura_id = a.id)'),
        ]
    if dominio == 'logistica':
        return [
            ('media', 'origen_destino', f'Para rutas con id hasta {k}, devuelve nombre de ruta, nombre del centro de origen y del centro de destino.', f'SELECT r.nombre AS ruta, o.nombre AS origen, d.nombre AS destino FROM rutas r JOIN centros o ON o.id = r.origen_id JOIN centros d ON d.id = r.destino_id WHERE r.id <= {k}'),
            ('media', 'conductor_vehiculo', f'Lista id de envio, nombre de conductor y de vehiculo de envios con id hasta {k}.', f'SELECT e.id, c.nombre AS conductor, v.nombre AS vehiculo FROM envios e JOIN conductores c ON c.id = e.conductor_id JOIN vehiculos v ON v.id = e.vehiculo_id WHERE e.id <= {k}'),
            ('dificil', 'sin_seguimiento', f'Lista id de envios mayores que {k} sin eventos de seguimiento.', f'SELECT e.id FROM envios e WHERE e.id > {k} AND NOT EXISTS (SELECT 1 FROM eventos_envio v WHERE v.envio_id = e.id)'),
            ('media', 'ultimo_evento', f'Para envios con id hasta {k}, devuelve envio_id y fecha de su ultimo evento de seguimiento, solo si tienen eventos.', f'SELECT envio_id, MAX(fecha) AS ultima_fecha FROM eventos_envio WHERE envio_id <= {k} GROUP BY envio_id'),
        ]
    if dominio == 'turismo':
        return [
            ('media', 'viajero_hotel', f'Lista id de estancia, nombre de viajero y hotel para estancias con id hasta {k}.', f'SELECT e.id, v.nombre AS viajero, h.nombre AS hotel FROM estancias e JOIN viajeros v ON v.id = e.viajero_id JOIN hoteles h ON h.id = e.hotel_id WHERE e.id <= {k}'),
            ('media', 'habitaciones', f'Por hotel con id hasta {k}, devuelve id y cantidad de habitaciones, incluso cero.', f'SELECT h.id, COUNT(r.id) AS habitaciones FROM hoteles h LEFT JOIN habitaciones r ON r.hotel_id = h.id WHERE h.id <= {k} GROUP BY h.id'),
            ('dificil', 'extras_preagregados', f'Para hoteles con id hasta {k}, devuelve hotel_id y total de extras de sus estancias; incluye cero, sin multiplicar cargos por habitaciones.', f'WITH x AS (SELECT estancia_id, SUM(importe) AS total FROM extras GROUP BY estancia_id) SELECT e.hotel_id, COALESCE(SUM(x.total), 0) AS total_extras FROM estancias e LEFT JOIN x ON x.estancia_id = e.id WHERE e.hotel_id <= {k} GROUP BY e.hotel_id'),
            ('dificil', 'sin_extras', f'Lista id de estancias mayores que {k} sin cargos extras.', f'SELECT e.id FROM estancias e WHERE e.id > {k} AND NOT EXISTS (SELECT 1 FROM extras x WHERE x.estancia_id = e.id)'),
        ]
    if dominio == 'energia':
        return [
            ('media', 'regiones', f'Por region con id hasta {k}, devuelve id y cantidad de sensores, incluso cero.', f'SELECT r.id, COUNT(s.id) AS sensores FROM regiones r LEFT JOIN estaciones e ON e.region_id = r.id LEFT JOIN sensores s ON s.estacion_id = e.id WHERE r.id <= {k} GROUP BY r.id'),
            ('media', 'alertas', f'Devuelve sensor_id y cantidad de alertas para sensores con id hasta {k}.', f'SELECT m.sensor_id, COUNT(a.id) AS alertas FROM mediciones m JOIN alertas a ON a.medicion_id = m.id WHERE m.sensor_id <= {k} GROUP BY m.sensor_id'),
            ('media', 'umbral_correlacion', f'Lista id y valor de mediciones del sensor {k} cuyo valor supera el umbral de ese sensor.', f'SELECT m.id, m.valor FROM mediciones m JOIN sensores s ON s.id = m.sensor_id WHERE s.id = {k} AND m.valor > s.umbral'),
            ('dificil', 'sin_mantenimiento', f'Lista id y nombre de estaciones mayores que {k} sin mantenimiento.', f'SELECT e.id, e.nombre FROM estaciones e WHERE e.id > {k} AND NOT EXISTS (SELECT 1 FROM mantenimientos m WHERE m.estacion_id = e.id)'),
        ]
    return [
        ('media', 'inspector', f'Devuelve nombre de inspector y cantidad de controles para inspectores con id hasta {k}, incluso cero.', f'SELECT i.nombre, COUNT(c.id) AS controles FROM inspectores i LEFT JOIN controles c ON c.inspector_id = i.id WHERE i.id <= {k} GROUP BY i.id, i.nombre'),
        ('media', 'consumos', f'Por insumo con id hasta {k}, devuelve id y cantidad total consumida, incluso cero.', f'SELECT i.id, COALESCE(SUM(c.cantidad), 0) AS cantidad FROM insumos i LEFT JOIN consumos c ON c.insumo_id = i.id WHERE i.id <= {k} GROUP BY i.id'),
        ('media', 'insumos_distintos', f'Lista lote_id y cantidad de insumos distintos de lotes con al menos {k} insumos distintos.', f'SELECT lote_id, COUNT(DISTINCT insumo_id) AS insumos FROM consumos GROUP BY lote_id HAVING COUNT(DISTINCT insumo_id) >= {k}'),
        ('dificil', 'sin_controles', f'Lista id y nombre de lotes mayores que {k} que tienen consumos pero ningun control.', f'SELECT l.id, l.nombre FROM lotes l WHERE l.id > {k} AND EXISTS (SELECT 1 FROM consumos x WHERE x.lote_id = l.id) AND NOT EXISTS (SELECT 1 FROM controles c WHERE c.lote_id = l.id)'),
    ]


def candidatos_diversos(d):
    dominio, a, b, c, fk_a, valor, fk_b, medida, activo = d
    for k in range(1, 11):
        fecha = str(date(2024, 1, 1) + timedelta(days=k * 20))
        ejemplos = [
            ('facil', 'div_raiz', f'Devuelve id y nombre de {a} con id hasta {k}.', f'SELECT id, nombre FROM {a} WHERE id <= {k}'),
            ('facil', 'div_activos', f'Lista id y nombre de {b} activos cuyo {valor} supera {k * 5}.', f'SELECT id, nombre FROM {b} WHERE {activo} = 1 AND {valor} > {k * 5}'),
            ('facil', 'div_top', f'Devuelve id, nombre y {valor} de los {k} registros de {b} con mayor {valor}; desempata por id menor.', f'SELECT id, nombre, {valor} FROM {b} ORDER BY {valor} DESC, id ASC LIMIT {k}'),
            ('facil', 'div_fecha', f'Lista id y fecha de {c} desde {fecha}, inclusive.', f"SELECT id, fecha FROM {c} WHERE fecha >= '{fecha}'"),
            ('facil', 'div_estado', f'Cuenta registros de {c} con estado ok e id mayor que {k}; devuelve total.', f"SELECT COUNT(*) AS total FROM {c} WHERE estado = 'ok' AND id > {k}"),
            ('facil', 'div_promedio', f'Devuelve promedio de {valor} de {b} con id mayor que {k} como promedio.', f'SELECT AVG({valor}) AS promedio FROM {b} WHERE id > {k}'),
            ('media', 'div_join', f'Lista nombre de {b} y nombre de {a} asociados mediante {fk_a}, con id de {a} hasta {k}.', f'SELECT b.nombre AS recurso, a.nombre AS raiz FROM {b} b JOIN {a} a ON a.id = b.{fk_a} WHERE a.id <= {k}'),
            ('media', 'div_ceros', f'Por registro de {b} con id hasta {k}, devuelve id y cantidad de {c}, incluyendo cero.', f'SELECT b.id, COUNT(c.id) AS total FROM {b} b LEFT JOIN {c} c ON c.{fk_b} = b.id WHERE b.id <= {k} GROUP BY b.id'),
            ('media', 'div_having', f'Por {fk_a} en {b}, devuelve {fk_a} y cantidad de registros solo si hay al menos {k}.', f'SELECT {fk_a}, COUNT(*) AS total FROM {b} GROUP BY {fk_a} HAVING COUNT(*) >= {k}'),
            ('media', 'div_suma', f'Por {fk_b} de {c}, devuelve {fk_b} y suma de {medida} si esa suma supera {k * 20}. Incluye todos los estados.', f'SELECT {fk_b}, SUM({medida}) AS total FROM {c} GROUP BY {fk_b} HAVING SUM({medida}) > {k * 20}'),
            ('media', 'div_huerfanos', f'Lista id y nombre de {b} con id mayor que {k} sin registros en {c}.', f'SELECT b.id, b.nombre FROM {b} b LEFT JOIN {c} c ON c.{fk_b} = b.id WHERE c.id IS NULL AND b.id > {k}'),
            ('media', 'div_tres', f'Por id de {a} hasta {k}, devuelve id y cantidad de {c} vinculados a traves de {b} y {fk_a}, solo si existen registros.', f'SELECT a.id, COUNT(c.id) AS total FROM {a} a JOIN {b} b ON b.{fk_a} = a.id JOIN {c} c ON c.{fk_b} = b.id WHERE a.id <= {k} GROUP BY a.id'),
            ('dificil', 'div_subconsulta', f'Lista id y nombre de {b} con id mayor que {k} cuyo {valor} supera el promedio de los registros con el mismo {fk_a}.', f'SELECT b.id, b.nombre FROM {b} b WHERE b.id > {k} AND b.{valor} > (SELECT AVG(x.{valor}) FROM {b} x WHERE x.{fk_a} = b.{fk_a})'),
            ('dificil', 'div_ultima', f'Por {fk_b} de {c} con valor hasta {k}, devuelve {fk_b}, id y fecha del ultimo registro; desempata por id mayor.', f'WITH t AS (SELECT {fk_b}, id, fecha, ROW_NUMBER() OVER (PARTITION BY {fk_b} ORDER BY fecha DESC, id DESC) AS rn FROM {c}) SELECT {fk_b}, id, fecha FROM t WHERE rn = 1 AND {fk_b} <= {k}'),
            ('dificil', 'div_cte', f'Usando CTE, devuelve {fk_b} y promedio de {medida} en {c} solo si supera {k * 5}, incluyendo todos los estados.', f'WITH t AS (SELECT {fk_b}, AVG({medida}) AS promedio FROM {c} GROUP BY {fk_b}) SELECT {fk_b}, promedio FROM t WHERE promedio > {k * 5}'),
            ('dificil', 'div_acumulado', f'Para {fk_b} igual a {k} en {c}, devuelve id, fecha y suma acumulada de {medida}, ordenada por fecha e id.', f'SELECT id, fecha, SUM({medida}) OVER (ORDER BY fecha, id ROWS UNBOUNDED PRECEDING) AS acumulado FROM {c} WHERE {fk_b} = {k} ORDER BY fecha, id'),
        ] + consultas_especificas(dominio, k)
        for nivel, familia, pregunta, sql in ejemplos:
            yield {'id': f'{dominio}_{familia}_{k:02}', 'esquema_id': f'train_{dominio}',
                   'pregunta': pregunta, 'sql': sql, 'nivel': nivel,
                   'peso': {'facil': 1, 'media': 2, 'dificil': 3}[nivel],
                   'familia': familia, 'procedencia': 'sintetico_plantillas_asistidas_IA', 'semilla': 2026}
