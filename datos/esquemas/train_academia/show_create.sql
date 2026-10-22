CREATE TABLE `alumnos` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de academia';

CREATE TABLE `areas` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de academia';

CREATE TABLE `asignaturas` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `profesor_id` int NOT NULL,
  `creditos` decimal(10,2) NOT NULL,
  `activa` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `profesor_id` (`profesor_id`),
  CONSTRAINT `asignaturas_ibfk_1` FOREIGN KEY (`profesor_id`) REFERENCES `profesores` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Recursos de academia; creditos es un valor del catalogo';

CREATE TABLE `inscripciones` (
  `id` int NOT NULL,
  `asignatura_id` int NOT NULL,
  `fecha` date NOT NULL,
  `nota` decimal(10,2) NOT NULL,
  `estado` varchar(20) NOT NULL COMMENT 'ok, pendiente o anulado',
  `alumno_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `asignatura_id` (`asignatura_id`),
  KEY `alumno_id` (`alumno_id`),
  CONSTRAINT `inscripciones_ibfk_1` FOREIGN KEY (`asignatura_id`) REFERENCES `asignaturas` (`id`),
  CONSTRAINT `inscripciones_ibfk_2` FOREIGN KEY (`alumno_id`) REFERENCES `alumnos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Eventos de academia; la medida es nota, no dinero salvo indicacion';

CREATE TABLE `prerrequisitos` (
  `id` int NOT NULL,
  `asignatura_id` int NOT NULL,
  `requerida_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `asignatura_id` (`asignatura_id`),
  KEY `requerida_id` (`requerida_id`),
  CONSTRAINT `prerrequisitos_ibfk_1` FOREIGN KEY (`asignatura_id`) REFERENCES `asignaturas` (`id`),
  CONSTRAINT `prerrequisitos_ibfk_2` FOREIGN KEY (`requerida_id`) REFERENCES `asignaturas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Dependencia dirigida entre asignaturas';

CREATE TABLE `profesores` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `area_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `area_id` (`area_id`),
  CONSTRAINT `profesores_ibfk_1` FOREIGN KEY (`area_id`) REFERENCES `areas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo propio de academia';
