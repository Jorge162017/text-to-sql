CREATE TABLE `centros` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de logistica';

CREATE TABLE `conductores` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de logistica';

CREATE TABLE `envios` (
  `id` int NOT NULL,
  `ruta_id` int NOT NULL,
  `fecha` date NOT NULL,
  `peso` decimal(10,2) NOT NULL,
  `estado` varchar(20) NOT NULL COMMENT 'ok, pendiente o anulado',
  `vehiculo_id` int NOT NULL,
  `conductor_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ruta_id` (`ruta_id`),
  KEY `vehiculo_id` (`vehiculo_id`),
  KEY `conductor_id` (`conductor_id`),
  CONSTRAINT `envios_ibfk_1` FOREIGN KEY (`ruta_id`) REFERENCES `rutas` (`id`),
  CONSTRAINT `envios_ibfk_2` FOREIGN KEY (`vehiculo_id`) REFERENCES `vehiculos` (`id`),
  CONSTRAINT `envios_ibfk_3` FOREIGN KEY (`conductor_id`) REFERENCES `conductores` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Eventos de logistica; la medida es peso, no dinero salvo indicacion';

CREATE TABLE `eventos_envio` (
  `id` int NOT NULL,
  `envio_id` int NOT NULL,
  `fecha` date NOT NULL,
  `descripcion` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `envio_id` (`envio_id`),
  CONSTRAINT `eventos_envio_ibfk_1` FOREIGN KEY (`envio_id`) REFERENCES `envios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Seguimiento: varias filas por envio';

CREATE TABLE `rutas` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `origen_id` int NOT NULL,
  `distancia` decimal(10,2) NOT NULL,
  `activa` tinyint(1) NOT NULL,
  `destino_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `origen_id` (`origen_id`),
  KEY `destino_id` (`destino_id`),
  CONSTRAINT `rutas_ibfk_1` FOREIGN KEY (`origen_id`) REFERENCES `centros` (`id`),
  CONSTRAINT `rutas_ibfk_2` FOREIGN KEY (`destino_id`) REFERENCES `centros` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recursos de logistica; distancia es un valor del catalogo';

CREATE TABLE `vehiculos` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de logistica';
