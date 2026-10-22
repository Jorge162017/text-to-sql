CREATE TABLE `consumos` (
  `id` int NOT NULL,
  `lote_id` int NOT NULL,
  `insumo_id` int NOT NULL,
  `cantidad` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `lote_id` (`lote_id`),
  KEY `insumo_id` (`insumo_id`),
  CONSTRAINT `consumos_ibfk_1` FOREIGN KEY (`lote_id`) REFERENCES `lotes` (`id`),
  CONSTRAINT `consumos_ibfk_2` FOREIGN KEY (`insumo_id`) REFERENCES `insumos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Relacion de muchos a muchos entre lotes e insumos';

CREATE TABLE `controles` (
  `id` int NOT NULL,
  `lote_id` int NOT NULL,
  `fecha` date NOT NULL,
  `defectos` decimal(10,2) NOT NULL,
  `estado` varchar(20) NOT NULL COMMENT 'ok, pendiente o anulado',
  `inspector_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `lote_id` (`lote_id`),
  KEY `inspector_id` (`inspector_id`),
  CONSTRAINT `controles_ibfk_1` FOREIGN KEY (`lote_id`) REFERENCES `lotes` (`id`),
  CONSTRAINT `controles_ibfk_2` FOREIGN KEY (`inspector_id`) REFERENCES `inspectores` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Eventos de manufactura; la medida es defectos, no dinero salvo indicacion';

CREATE TABLE `fabricas` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de manufactura';

CREATE TABLE `inspectores` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de manufactura';

CREATE TABLE `insumos` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de manufactura';

CREATE TABLE `lotes` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `fabrica_id` int NOT NULL,
  `costo` decimal(10,2) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fabrica_id` (`fabrica_id`),
  CONSTRAINT `lotes_ibfk_1` FOREIGN KEY (`fabrica_id`) REFERENCES `fabricas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recursos de manufactura; costo es un valor del catalogo';
