CREATE TABLE `compras` (
  `id` int NOT NULL,
  `cliente_id` int NOT NULL,
  `fecha` date NOT NULL,
  `estado` varchar(20) NOT NULL COMMENT 'completado, pendiente o cancelado',
  PRIMARY KEY (`id`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `compras_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `lectores` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cabeceras de compra';

CREATE TABLE `generos` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Clasificacion de libro';

CREATE TABLE `items` (
  `id` int NOT NULL,
  `pedido_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL COMMENT 'Precio historico de esta linea',
  PRIMARY KEY (`id`),
  KEY `pedido_id` (`pedido_id`),
  KEY `producto_id` (`producto_id`),
  CONSTRAINT `items_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `compras` (`id`),
  CONSTRAINT `items_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `libros` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Lineas: importe = cantidad * precio_unitario';

CREATE TABLE `lectores` (
  `id` int NOT NULL COMMENT 'Identificador',
  `nombre` varchar(80) NOT NULL COMMENT 'Nombre del contacto',
  `ciudad` varchar(60) NOT NULL,
  `alta` date NOT NULL,
  `correo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Contactos de libreria';

CREATE TABLE `libros` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `categoria_id` int NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `categoria_id` (`categoria_id`),
  CONSTRAINT `libros_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `generos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo de libro; precio actual, no historico';

CREATE TABLE `recibos` (
  `id` int NOT NULL,
  `pedido_id` int NOT NULL,
  `fecha` date NOT NULL,
  `importe` decimal(10,2) NOT NULL,
  `metodo` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `pedido_id` (`pedido_id`),
  CONSTRAINT `recibos_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `compras` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Abonos parciales; puede haber varios por cabecera';
