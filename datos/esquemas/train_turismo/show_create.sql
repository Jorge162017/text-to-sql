CREATE TABLE `destinos` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de turismo';

CREATE TABLE `estancias` (
  `id` int NOT NULL,
  `hotel_id` int NOT NULL,
  `fecha` date NOT NULL,
  `noches` decimal(10,2) NOT NULL,
  `estado` varchar(20) NOT NULL COMMENT 'ok, pendiente o anulado',
  `viajero_id` int NOT NULL,
  `habitacion_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `hotel_id` (`hotel_id`),
  KEY `viajero_id` (`viajero_id`),
  KEY `habitacion_id` (`habitacion_id`),
  CONSTRAINT `estancias_ibfk_1` FOREIGN KEY (`hotel_id`) REFERENCES `hoteles` (`id`),
  CONSTRAINT `estancias_ibfk_2` FOREIGN KEY (`viajero_id`) REFERENCES `viajeros` (`id`),
  CONSTRAINT `estancias_ibfk_3` FOREIGN KEY (`habitacion_id`) REFERENCES `habitaciones` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Eventos de turismo; la medida es noches, no dinero salvo indicacion';

CREATE TABLE `extras` (
  `id` int NOT NULL,
  `estancia_id` int NOT NULL,
  `importe` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `estancia_id` (`estancia_id`),
  CONSTRAINT `extras_ibfk_1` FOREIGN KEY (`estancia_id`) REFERENCES `estancias` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Cargos adicionales por estancia; no confundir con noches';

CREATE TABLE `habitaciones` (
  `id` int NOT NULL,
  `hotel_id` int NOT NULL,
  `numero` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `hotel_id` (`hotel_id`),
  CONSTRAINT `habitaciones_ibfk_1` FOREIGN KEY (`hotel_id`) REFERENCES `hoteles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Habitaciones fisicas de cada hotel';

CREATE TABLE `hoteles` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `destino_id` int NOT NULL,
  `tarifa` decimal(10,2) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `destino_id` (`destino_id`),
  CONSTRAINT `hoteles_ibfk_1` FOREIGN KEY (`destino_id`) REFERENCES `destinos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recursos de turismo; tarifa es un valor del catalogo';

CREATE TABLE `viajeros` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de turismo';
