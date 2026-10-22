CREATE TABLE `areas` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de academia';

CREATE TABLE `profesores` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  area_id INT NOT NULL,
  FOREIGN KEY (area_id) REFERENCES areas(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de academia';

CREATE TABLE `alumnos` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de academia';

CREATE TABLE `asignaturas` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  profesor_id INT NOT NULL,
  creditos DECIMAL(10,2) NOT NULL,
  activa BOOLEAN NOT NULL,
  FOREIGN KEY (profesor_id) REFERENCES profesores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Recursos de academia; creditos es un valor del catalogo';

CREATE TABLE `inscripciones` (
  id INT PRIMARY KEY,
  asignatura_id INT NOT NULL,
  fecha DATE NOT NULL,
  nota DECIMAL(10,2) NOT NULL,
  estado VARCHAR(20) NOT NULL COMMENT 'ok, pendiente o anulado',
  FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id),
  alumno_id INT NOT NULL,
  FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Eventos de academia; la medida es nota, no dinero salvo indicacion';

CREATE TABLE `prerrequisitos` (
  id INT PRIMARY KEY,
  asignatura_id INT NOT NULL,
  requerida_id INT NOT NULL,
  FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id),
  FOREIGN KEY (requerida_id) REFERENCES asignaturas(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Dependencia dirigida entre asignaturas';
