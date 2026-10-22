"""Genera esquemas, semillas y candidatos sintéticos; NO certifica ejecución SQL.

Uso: python -m scripts.generar_datos
No usa preguntas de validación para construir entrenamiento.
"""
import argparse
import json
from datetime import date, timedelta

from scripts.comun import DATOS, guardar_json, guardar_jsonl

# Diez dominios propios. Comparten una estructura comercial deliberadamente;
# esta limitación se documenta y no se presenta como diversidad estructural plena.
DOMINIOS = [
    ('tienda', 'clientes', 'pedidos', 'productos', 'categorias', 'detalle_pedido', 'pagos', 'cliente', 'pedido', 'producto'),
    ('cafeteria', 'comensales', 'ordenes', 'platillos', 'familias', 'consumos', 'cobros', 'comensal', 'orden', 'platillo'),
    ('ferreteria', 'compradores', 'ventas', 'articulos', 'rubros', 'renglones', 'abonos', 'comprador', 'venta', 'articulo'),
    ('farmacia', 'pacientes', 'recetas', 'medicamentos', 'grupos', 'dispensaciones', 'transacciones', 'paciente', 'receta', 'medicamento'),
    ('libreria', 'lectores', 'compras', 'libros', 'generos', 'items', 'recibos', 'lector', 'compra', 'libro'),
    ('repuestos', 'talleres', 'solicitudes', 'piezas', 'tipos', 'lineas', 'depositos', 'taller', 'solicitud', 'pieza'),
    ('floreria', 'destinatarios', 'encargos', 'arreglos', 'colecciones', 'selecciones', 'anticipos', 'destinatario', 'encargo', 'arreglo'),
    ('deportes', 'socios', 'reservas', 'equipos', 'disciplinas', 'alquileres', 'cuotas', 'socio', 'reserva', 'equipo'),
    ('electronica', 'usuarios', 'facturas', 'dispositivos', 'marcas', 'detalles', 'cargos', 'usuario', 'factura', 'dispositivo'),
    ('panaderia', 'distribuidores', 'despachos', 'panes', 'clases', 'partidas', 'liquidaciones', 'distribuidor', 'despacho', 'pan'),
]


def tabla(nombre, columnas, comentario):
    return f"CREATE TABLE `{nombre}` (\n  " + ',\n  '.join(columnas) + f"\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{comentario}';"


def insertar(nombre, filas):
    def literal(v):
        if v is None:
            return 'NULL'
        if isinstance(v, str):
            return "'" + v.replace("'", "''") + "'"
        return str(v)
    return f'INSERT INTO `{nombre}` VALUES\n' + ',\n'.join('(' + ', '.join(map(literal, fila)) + ')' for fila in filas) + ';'


def esquema_comercial(d):
    dominio, a, o, p, c, l, m, actor, orden, producto = d
    tablas = [
        tabla(a, ["id INT PRIMARY KEY COMMENT 'Identificador'", "nombre VARCHAR(80) NOT NULL COMMENT 'Nombre del contacto'", "ciudad VARCHAR(60) NOT NULL", "alta DATE NOT NULL", "correo VARCHAR(100) NULL"], f'Contactos de {dominio}'),
        tabla(c, ["id INT PRIMARY KEY", "nombre VARCHAR(80) NOT NULL"], f'Clasificacion de {producto}'),
        tabla(p, ["id INT PRIMARY KEY", "nombre VARCHAR(80) NOT NULL", "categoria_id INT NOT NULL", "precio DECIMAL(10,2) NOT NULL", "activo BOOLEAN NOT NULL", f'FOREIGN KEY (categoria_id) REFERENCES `{c}`(id)'], f'Catalogo de {producto}; precio actual, no historico'),
        tabla(o, ["id INT PRIMARY KEY", "cliente_id INT NOT NULL", "fecha DATE NOT NULL", "estado VARCHAR(20) NOT NULL COMMENT 'completado, pendiente o cancelado'", f'FOREIGN KEY (cliente_id) REFERENCES `{a}`(id)'], f'Cabeceras de {orden}'),
        tabla(l, ["id INT PRIMARY KEY", "pedido_id INT NOT NULL", "producto_id INT NOT NULL", "cantidad INT NOT NULL", "precio_unitario DECIMAL(10,2) NOT NULL COMMENT 'Precio historico de esta linea'", f'FOREIGN KEY (pedido_id) REFERENCES `{o}`(id)', f'FOREIGN KEY (producto_id) REFERENCES `{p}`(id)'], 'Lineas: importe = cantidad * precio_unitario'),
        tabla(m, ["id INT PRIMARY KEY", "pedido_id INT NOT NULL", "fecha DATE NOT NULL", "importe DECIMAL(10,2) NOT NULL", "metodo VARCHAR(20) NOT NULL", f'FOREIGN KEY (pedido_id) REFERENCES `{o}`(id)'], 'Abonos parciales; puede haber varios por cabecera'),
    ]
    semillas = [
        insertar(a, [(i, f'{actor.title()} {i:02}', ['Guatemala', 'Antigua', 'Xela', 'Coban'][i % 4], str(date(2024, 1, 1) + timedelta(days=i * 13)), None if i % 5 == 0 else f'contacto{i}@example.invalid') for i in range(1, 25)]),
        insertar(c, [(i, f'Grupo {i}') for i in range(1, 9)]),
        insertar(p, [(i, f'{producto.title()} {i:02}', (i - 1) % 8 + 1, (i * 17 % 180) + 10.5, int(i % 7 != 0)) for i in range(1, 33)]),
        insertar(o, [(i, (i * 7) % 20 + 1, str(date(2024, 1, 1) + timedelta(days=(i * 11) % 730)), ['completado', 'pendiente', 'cancelado'][i % 3]) for i in range(1, 121)]),
    ]
    filas = []
    for i in range(1, 121):
        for j in range(1, i % 3 + 2):
            filas.append((len(filas) + 1, i, (i * 3 + j) % 28 + 1, (i + j) % 5 + 1, (i * 7 + j * 13) % 170 + 5.25))
    semillas.append(insertar(l, filas))
    pagos = []
    for i in range(1, 121):
        if i % 4:
            for j in range(1, i % 2 + 2):
                pagos.append((len(pagos) + 1, i, str(date(2024, 1, 1) + timedelta(days=(i * 11) % 730 + j)), i * 3 + j + 0.5, ['efectivo', 'tarjeta', 'transferencia'][(i + j) % 3]))
    semillas.append(insertar(m, pagos))
    return tablas, semillas


def candidatos(d):
    dominio, a, o, p, c, l, m, actor, orden, producto = d
    for k in range(1, 9):
        ciudad = ['Guatemala', 'Antigua', 'Xela', 'Coban'][(k - 1) % 4]
        fecha = str(date(2024, 1, 1) + timedelta(days=k * 30))
        umbral = k * 25
        # La variación de parámetros se cuenta de forma explícita; no son 240
        # estructuras SQL independientes por esquema.
        ejemplos = [
            ('facil', 'filtro_id', f'Muestra id y nombre de {actor} con id {k}.', f'SELECT id, nombre FROM {a} WHERE id = {k}'),
            ('facil', 'filtro_ciudad', f'Muestra id y nombre de {actor} en {ciudad} con id mayor que {k}.', f"SELECT id, nombre FROM {a} WHERE ciudad = '{ciudad}' AND id > {k}"),
            ('facil', 'precio', f'Lista id, nombre y precio de {producto} con precio superior a {umbral}.', f'SELECT id, nombre, precio FROM {p} WHERE precio > {umbral}'),
            ('facil', 'rango_fecha', f'Cuenta las cabeceras de {orden} desde {fecha} inclusive; devuelve total.', f"SELECT COUNT(*) AS total FROM {o} WHERE fecha >= '{fecha}'"),
            ('facil', 'top_precio', f'Devuelve los {k} {producto} mas caros con id, nombre y precio; desempata por id ascendente.', f'SELECT id, nombre, precio FROM {p} ORDER BY precio DESC, id ASC LIMIT {k}'),
            ('facil', 'null', f'Lista id y nombre de {actor} sin correo y con id mayor o igual a {k}.', f'SELECT id, nombre FROM {a} WHERE correo IS NULL AND id >= {k}'),
            ('facil', 'activos', f'Cuenta los {producto} activos de la categoria {k}; devuelve total.', f'SELECT COUNT(*) AS total FROM {p} WHERE activo = 1 AND categoria_id = {k}'),
            ('facil', 'promedio', f'Devuelve el precio promedio de {producto} de categoria {k} como promedio.', f'SELECT AVG(precio) AS promedio FROM {p} WHERE categoria_id = {k}'),
            ('media', 'join_actor', f'Lista id de {orden}, fecha y nombre del contacto para {actor} id {k}.', f'SELECT o.id, o.fecha, a.nombre FROM {o} o JOIN {a} a ON a.id = o.cliente_id WHERE a.id = {k}'),
            ('media', 'join_categoria', f'Lista nombre de {producto} y nombre de categoria para categoria {k}.', f'SELECT p.nombre AS producto, c.nombre AS categoria FROM {p} p JOIN {c} c ON c.id = p.categoria_id WHERE c.id = {k}'),
            ('media', 'total_lineas', f'Por cabecera de {orden} con id mayor que {k}, devuelve id e importe total de lineas.', f'SELECT o.id, SUM(l.cantidad * l.precio_unitario) AS total FROM {o} o JOIN {l} l ON l.pedido_id = o.id WHERE o.id > {k} GROUP BY o.id'),
            ('media', 'having', f'Por contacto, cuenta sus {orden}; devuelve cliente_id y total solo si tiene al menos {k}.', f'SELECT cliente_id, COUNT(*) AS total FROM {o} GROUP BY cliente_id HAVING COUNT(*) >= {k}'),
            ('media', 'left_join', f'Lista id y nombre de contactos sin {orden}, con id mayor que {k}.', f'SELECT a.id, a.nombre FROM {a} a LEFT JOIN {o} o ON o.cliente_id = a.id WHERE o.id IS NULL AND a.id > {k}'),
            ('media', 'suma_pagos', f'Para {orden} id {k}, devuelve pedido_id y suma de importes pagados.', f'SELECT pedido_id, SUM(importe) AS pagado FROM {m} WHERE pedido_id = {k} GROUP BY pedido_id'),
            ('media', 'unidades', f'Por {producto} en categoria {k}, devuelve id y unidades registradas en lineas, incluyendo cero y todos los estados de cabecera.', f'SELECT p.id, COALESCE(SUM(l.cantidad), 0) AS unidades FROM {p} p LEFT JOIN {l} l ON l.producto_id = p.id WHERE p.categoria_id = {k} GROUP BY p.id'),
            ('media', 'cuenta_distinta', f'Devuelve cantidad de contactos distintos con {orden} desde {fecha} inclusive como total.', f"SELECT COUNT(DISTINCT cliente_id) AS total FROM {o} WHERE fecha >= '{fecha}'"),
            ('media', 'mes', f'Por año y mes desde {fecha}, devuelve anio, mes y cantidad de {orden}.', f"SELECT YEAR(fecha) AS anio, MONTH(fecha) AS mes, COUNT(*) AS total FROM {o} WHERE fecha >= '{fecha}' GROUP BY YEAR(fecha), MONTH(fecha)"),
            ('media', 'categoria_having', f'Por categoria, devuelve categoria_id y precio medio, solo si supera {umbral}.', f'SELECT categoria_id, AVG(precio) AS promedio FROM {p} GROUP BY categoria_id HAVING AVG(precio) > {umbral}'),
            ('media', 'join_tres', f'Lista nombre de {actor}, id de {orden} y cantidad de lineas para {actor} id {k}.', f'SELECT a.nombre, o.id, COUNT(l.id) AS lineas FROM {a} a JOIN {o} o ON o.cliente_id = a.id JOIN {l} l ON l.pedido_id = o.id WHERE a.id = {k} GROUP BY a.id, a.nombre, o.id'),
            ('media', 'metodos', f'Por metodo de pago desde {fecha}, devuelve metodo y total pagado.', f"SELECT metodo, SUM(importe) AS total FROM {m} WHERE fecha >= '{fecha}' GROUP BY metodo"),
            ('dificil', 'subconsulta', f'Lista id y nombre de {producto} en categoria {k} cuyo precio supera el promedio de esa categoria.', f'SELECT id, nombre FROM {p} WHERE categoria_id = {k} AND precio > (SELECT AVG(precio) FROM {p} WHERE categoria_id = {k})'),
            ('dificil', 'not_exists', f'Lista id de {orden} sin pagos con id mayor que {k}.', f'SELECT o.id FROM {o} o WHERE o.id > {k} AND NOT EXISTS (SELECT 1 FROM {m} m WHERE m.pedido_id = o.id)'),
            ('dificil', 'cte', f'Devuelve pedido_id e importe de cabeceras de {orden} cuyas lineas suman mas de {umbral}, usando una CTE.', f'WITH totales AS (SELECT pedido_id, SUM(cantidad * precio_unitario) AS importe FROM {l} GROUP BY pedido_id) SELECT pedido_id, importe FROM totales WHERE importe > {umbral}'),
            ('dificil', 'ventana_ranking', f'Lista id, nombre, categoria_id y rango de precios descendente sin saltos de {producto} de categoria {k}.', f'SELECT id, nombre, categoria_id, DENSE_RANK() OVER (PARTITION BY categoria_id ORDER BY precio DESC) AS rango FROM {p} WHERE categoria_id = {k}'),
            ('dificil', 'acumulado', f'Para {actor} id {k}, devuelve id de {orden}, fecha y numero acumulado de cabeceras ordenadas por fecha e id.', f'SELECT id, fecha, COUNT(*) OVER (ORDER BY fecha, id ROWS UNBOUNDED PRECEDING) AS acumulado FROM {o} WHERE cliente_id = {k} ORDER BY fecha, id'),
            ('dificil', 'ultima', f'Devuelve id, cliente_id y fecha de la ultima cabecera de cada contacto con id mayor que {k}; desempata por id mayor.', f'WITH ordenadas AS (SELECT id, cliente_id, fecha, ROW_NUMBER() OVER (PARTITION BY cliente_id ORDER BY fecha DESC, id DESC) AS rn FROM {o}) SELECT id, cliente_id, fecha FROM ordenadas WHERE rn = 1 AND cliente_id > {k}'),
            ('dificil', 'fecha_intervalo', f'Lista id y fecha de {orden} entre {fecha} inclusive y 30 dias despues exclusivo.', f"SELECT id, fecha FROM {o} WHERE fecha >= '{fecha}' AND fecha < DATE_ADD('{fecha}', INTERVAL 30 DAY)"),
            ('dificil', 'doble_agregacion', f'Devuelve cliente_id y gasto total en lineas para contactos que superen {umbral}; no cuentes pagos.', f'WITH t AS (SELECT pedido_id, SUM(cantidad * precio_unitario) AS total FROM {l} GROUP BY pedido_id) SELECT o.cliente_id, SUM(t.total) AS gasto FROM {o} o JOIN t ON t.pedido_id = o.id GROUP BY o.cliente_id HAVING SUM(t.total) > {umbral}'),
            ('dificil', 'correlacion', f'Lista id y nombre de {actor} con id mayor que {k} y alguna cabecera completada.', f"SELECT a.id, a.nombre FROM {a} a WHERE a.id > {k} AND EXISTS (SELECT 1 FROM {o} o WHERE o.cliente_id = a.id AND o.estado = 'completado')"),
            ('dificil', 'anti_producto', f'Lista id y nombre de {producto} de categoria {k} que nunca aparecieron en lineas.', f'SELECT p.id, p.nombre FROM {p} p WHERE p.categoria_id = {k} AND NOT EXISTS (SELECT 1 FROM {l} l WHERE l.producto_id = p.id)'),
        ]
        for nivel, familia, pregunta, sql in ejemplos:
            yield {'id': f'{dominio}_{familia}_{k:02}', 'esquema_id': f'train_{dominio}',
                   'pregunta': pregunta, 'sql': sql, 'nivel': nivel,
                   'peso': {'facil': 1, 'media': 2, 'dificil': 3}[nivel],
                   'familia': familia, 'procedencia': 'sintetico_plantillas_asistidas_IA',
                   'semilla': 2026}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reemplazar', action='store_true', help='Regenerar candidatos existentes; no modifica validación propia')
    args = parser.parse_args()
    ruta = DATOS / 'candidatos' / 'entrenamiento.jsonl'
    if ruta.exists() and not args.reemplazar:
        parser.error('Los candidatos ya existen. Usa --reemplazar solo si deseas regenerarlos.')
    from scripts.dominios_diversos import DOMINIOS_DIVERSOS, construir, candidatos_diversos
    registros, esquemas = [], []
    for d in DOMINIOS:
        nombre = 'train_' + d[0]
        ddl, semillas = esquema_comercial(d)
        carpeta = DATOS / 'esquemas' / nombre
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / 'schema.sql').write_text('\n\n'.join(ddl) + '\n', encoding='utf-8')
        (carpeta / 'seed.sql').write_text('\n\n'.join(semillas) + '\n', encoding='utf-8')
        registros.extend(candidatos(d))
        esquemas.append(nombre)
    for d in DOMINIOS_DIVERSOS:
        nombre = 'train_' + d[0]
        ddl, semillas = construir(d)
        carpeta = DATOS / 'esquemas' / nombre
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / 'schema.sql').write_text('\n\n'.join(ddl) + '\n', encoding='utf-8')
        (carpeta / 'seed.sql').write_text('\n\n'.join(semillas) + '\n', encoding='utf-8')
        registros.extend(candidatos_diversos(d))
        esquemas.append(nombre)
    guardar_jsonl(ruta, registros)
    guardar_json(DATOS / 'particiones.json', {
        'semilla': 2026, 'entrenamiento': esquemas,
        'validacion': ['val_biblioteca', 'val_hospital'],
        'regla': 'Separación por esquema completo. Validación nunca alimenta entrenamiento.'})
    print(json.dumps({'candidatos': len(registros), 'esquemas_entrenamiento': len(esquemas)}, indent=2))


if __name__ == '__main__':
    main()
