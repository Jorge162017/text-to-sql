CREATE TABLE `clases` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Clasificacion de pan';

CREATE TABLE `despachos` (
  `id` int NOT NULL,
  `cliente_id` int NOT NULL,
  `fecha` date NOT NULL,
  `estado` varchar(20) NOT NULL COMMENT 'completado, pendiente o cancelado',
  PRIMARY KEY (`id`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `despachos_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `distribuidores` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cabeceras de despacho';

CREATE TABLE `distribuidores` (
  `id` int NOT NULL COMMENT 'Identificador',
  `nombre` varchar(80) NOT NULL COMMENT 'Nombre del contacto',
  `ciudad` varchar(60) NOT NULL,
  `alta` date NOT NULL,
  `correo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Contactos de panaderia';

CREATE TABLE `liquidaciones` (
  `id` int NOT NULL,
  `pedido_id` int NOT NULL,
  `fecha` date NOT NULL,
  `importe` decimal(10,2) NOT NULL,
  `metodo` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `pedido_id` (`pedido_id`),
  CONSTRAINT `liquidaciones_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `despachos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Abonos parciales; puede haber varios por cabecera';

CREATE TABLE `panes` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `categoria_id` int NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `categoria_id` (`categoria_id`),
  CONSTRAINT `panes_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `clases` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo de pan; precio actual, no historico';

CREATE TABLE `partidas` (
  `id` int NOT NULL,
  `pedido_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL COMMENT 'Precio historico de esta linea',
  PRIMARY KEY (`id`),
  KEY `pedido_id` (`pedido_id`),
  KEY `producto_id` (`producto_id`),
  CONSTRAINT `partidas_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `despachos` (`id`),
  CONSTRAINT `partidas_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `panes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Lineas: importe = cantidad * precio_unitario';
