CREATE TABLE `autores` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `pais` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Autores; cada titulo tiene un autor principal';

CREATE TABLE `ejemplares` (
  `id` int NOT NULL,
  `titulo_id` int NOT NULL,
  `sede_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `titulo_id` (`titulo_id`),
  KEY `sede_id` (`sede_id`),
  CONSTRAINT `ejemplares_ibfk_1` FOREIGN KEY (`titulo_id`) REFERENCES `titulos` (`id`),
  CONSTRAINT `ejemplares_ibfk_2` FOREIGN KEY (`sede_id`) REFERENCES `sedes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Copias fisicas por sede';

CREATE TABLE `miembros` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `alta` date NOT NULL,
  `correo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Usuarios de biblioteca';

CREATE TABLE `prestamos` (
  `id` int NOT NULL,
  `ejemplar_id` int NOT NULL,
  `miembro_id` int NOT NULL,
  `inicio` date NOT NULL,
  `vence` date NOT NULL,
  `devolucion` date DEFAULT NULL COMMENT 'NULL significa pendiente de devolver',
  PRIMARY KEY (`id`),
  KEY `ejemplar_id` (`ejemplar_id`),
  KEY `miembro_id` (`miembro_id`),
  CONSTRAINT `prestamos_ibfk_1` FOREIGN KEY (`ejemplar_id`) REFERENCES `ejemplares` (`id`),
  CONSTRAINT `prestamos_ibfk_2` FOREIGN KEY (`miembro_id`) REFERENCES `miembros` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Prestamos; usar fecha de corte explicita para atraso';

CREATE TABLE `sedes` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `ciudad` varchar(60) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Sedes de biblioteca';

CREATE TABLE `titulos` (
  `id` int NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `autor_id` int NOT NULL,
  `anio` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `autor_id` (`autor_id`),
  CONSTRAINT `titulos_ibfk_1` FOREIGN KEY (`autor_id`) REFERENCES `autores` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Obras bibliograficas, no ejemplares fisicos';
