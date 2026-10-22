CREATE TABLE `compradores` (
  id INT PRIMARY KEY COMMENT 'Identificador',
  nombre VARCHAR(80) NOT NULL COMMENT 'Nombre del contacto',
  ciudad VARCHAR(60) NOT NULL,
  alta DATE NOT NULL,
  correo VARCHAR(100) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Contactos de ferreteria';

CREATE TABLE `rubros` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Clasificacion de articulo';

CREATE TABLE `articulos` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  categoria_id INT NOT NULL,
  precio DECIMAL(10,2) NOT NULL,
  activo BOOLEAN NOT NULL,
  FOREIGN KEY (categoria_id) REFERENCES `rubros`(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo de articulo; precio actual, no historico';

CREATE TABLE `ventas` (
  id INT PRIMARY KEY,
  cliente_id INT NOT NULL,
  fecha DATE NOT NULL,
  estado VARCHAR(20) NOT NULL COMMENT 'completado, pendiente o cancelado',
  FOREIGN KEY (cliente_id) REFERENCES `compradores`(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Cabeceras de venta';

CREATE TABLE `renglones` (
  id INT PRIMARY KEY,
  pedido_id INT NOT NULL,
  producto_id INT NOT NULL,
  cantidad INT NOT NULL,
  precio_unitario DECIMAL(10,2) NOT NULL COMMENT 'Precio historico de esta linea',
  FOREIGN KEY (pedido_id) REFERENCES `ventas`(id),
  FOREIGN KEY (producto_id) REFERENCES `articulos`(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Lineas: importe = cantidad * precio_unitario';

CREATE TABLE `abonos` (
  id INT PRIMARY KEY,
  pedido_id INT NOT NULL,
  fecha DATE NOT NULL,
  importe DECIMAL(10,2) NOT NULL,
  metodo VARCHAR(20) NOT NULL,
  FOREIGN KEY (pedido_id) REFERENCES `ventas`(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Abonos parciales; puede haber varios por cabecera';
