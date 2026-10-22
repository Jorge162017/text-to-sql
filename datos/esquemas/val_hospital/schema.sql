CREATE TABLE `especialidades` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Especialidades medicas';

CREATE TABLE `medicos` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  especialidad_id INT NOT NULL,
  FOREIGN KEY (especialidad_id) REFERENCES especialidades(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Medicos con una especialidad principal';

CREATE TABLE `personas` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  nacimiento DATE NOT NULL,
  municipio VARCHAR(60) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Pacientes ficticios, sin datos personales reales';

CREATE TABLE `citas` (
  id INT PRIMARY KEY,
  persona_id INT NOT NULL,
  medico_id INT NOT NULL,
  fecha DATE NOT NULL,
  estado VARCHAR(20) NOT NULL COMMENT 'atendida, pendiente o cancelada',
  FOREIGN KEY (persona_id) REFERENCES personas(id),
  FOREIGN KEY (medico_id) REFERENCES medicos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agenda clinica';

CREATE TABLE `procedimientos` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  costo DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo de procedimientos';

CREATE TABLE `atenciones` (
  id INT PRIMARY KEY,
  cita_id INT NOT NULL,
  procedimiento_id INT NOT NULL,
  cantidad INT NOT NULL,
  FOREIGN KEY (cita_id) REFERENCES citas(id),
  FOREIGN KEY (procedimiento_id) REFERENCES procedimientos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Procedimientos realizados en una cita';
