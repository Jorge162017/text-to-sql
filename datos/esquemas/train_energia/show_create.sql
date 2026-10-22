CREATE TABLE `alertas` (
  `id` int NOT NULL,
  `medicion_id` int NOT NULL,
  `nivel` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `medicion_id` (`medicion_id`),
  CONSTRAINT `alertas_ibfk_1` FOREIGN KEY (`medicion_id`) REFERENCES `mediciones` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Alertas asociadas a mediciones';

CREATE TABLE `estaciones` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `region_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `region_id` (`region_id`),
  CONSTRAINT `estaciones_ibfk_1` FOREIGN KEY (`region_id`) REFERENCES `regiones` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de energia';

CREATE TABLE `mantenimientos` (
  `id` int NOT NULL,
  `estacion_id` int NOT NULL,
  `fecha` date NOT NULL,
  `costo` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `estacion_id` (`estacion_id`),
  CONSTRAINT `mantenimientos_ibfk_1` FOREIGN KEY (`estacion_id`) REFERENCES `estaciones` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Intervenciones en estaciones, no en sensores';

CREATE TABLE `mediciones` (
  `id` int NOT NULL,
  `sensor_id` int NOT NULL,
  `fecha` date NOT NULL,
  `valor` decimal(10,2) NOT NULL,
  `estado` varchar(20) NOT NULL COMMENT 'ok, pendiente o anulado',
  PRIMARY KEY (`id`),
  KEY `sensor_id` (`sensor_id`),
  CONSTRAINT `mediciones_ibfk_1` FOREIGN KEY (`sensor_id`) REFERENCES `sensores` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Eventos de energia; la medida es valor, no dinero salvo indicacion';

CREATE TABLE `regiones` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de energia';

CREATE TABLE `sensores` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `estacion_id` int NOT NULL,
  `umbral` decimal(10,2) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `estacion_id` (`estacion_id`),
  CONSTRAINT `sensores_ibfk_1` FOREIGN KEY (`estacion_id`) REFERENCES `estaciones` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recursos de energia; umbral es un valor del catalogo';
