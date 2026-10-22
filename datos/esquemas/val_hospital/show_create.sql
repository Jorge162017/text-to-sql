CREATE TABLE `atenciones` (
  `id` int NOT NULL,
  `cita_id` int NOT NULL,
  `procedimiento_id` int NOT NULL,
  `cantidad` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cita_id` (`cita_id`),
  KEY `procedimiento_id` (`procedimiento_id`),
  CONSTRAINT `atenciones_ibfk_1` FOREIGN KEY (`cita_id`) REFERENCES `citas` (`id`),
  CONSTRAINT `atenciones_ibfk_2` FOREIGN KEY (`procedimiento_id`) REFERENCES `procedimientos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Procedimientos realizados en una cita';

CREATE TABLE `citas` (
  `id` int NOT NULL,
  `persona_id` int NOT NULL,
  `medico_id` int NOT NULL,
  `fecha` date NOT NULL,
  `estado` varchar(20) NOT NULL COMMENT 'atendida, pendiente o cancelada',
  PRIMARY KEY (`id`),
  KEY `persona_id` (`persona_id`),
  KEY `medico_id` (`medico_id`),
  CONSTRAINT `citas_ibfk_1` FOREIGN KEY (`persona_id`) REFERENCES `personas` (`id`),
  CONSTRAINT `citas_ibfk_2` FOREIGN KEY (`medico_id`) REFERENCES `medicos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Agenda clinica';

CREATE TABLE `especialidades` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Especialidades medicas';

CREATE TABLE `medicos` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `especialidad_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `especialidad_id` (`especialidad_id`),
  CONSTRAINT `medicos_ibfk_1` FOREIGN KEY (`especialidad_id`) REFERENCES `especialidades` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Medicos con una especialidad principal';

CREATE TABLE `personas` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `nacimiento` date NOT NULL,
  `municipio` varchar(60) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Pacientes ficticios, sin datos personales reales';

CREATE TABLE `procedimientos` (
  `id` int NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `costo` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Catalogo de procedimientos';
