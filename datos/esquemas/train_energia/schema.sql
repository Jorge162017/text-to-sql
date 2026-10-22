CREATE TABLE `regiones` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de energia';

CREATE TABLE `estaciones` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  region_id INT NOT NULL,
  FOREIGN KEY (region_id) REFERENCES regiones(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de energia';

CREATE TABLE `sensores` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  estacion_id INT NOT NULL,
  umbral DECIMAL(10,2) NOT NULL,
  activo BOOLEAN NOT NULL,
  FOREIGN KEY (estacion_id) REFERENCES estaciones(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Recursos de energia; umbral es un valor del catalogo';

CREATE TABLE `mediciones` (
  id INT PRIMARY KEY,
  sensor_id INT NOT NULL,
  fecha DATE NOT NULL,
  valor DECIMAL(10,2) NOT NULL,
  estado VARCHAR(20) NOT NULL COMMENT 'ok, pendiente o anulado',
  FOREIGN KEY (sensor_id) REFERENCES sensores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Eventos de energia; la medida es valor, no dinero salvo indicacion';

CREATE TABLE `alertas` (
  id INT PRIMARY KEY,
  medicion_id INT NOT NULL,
  nivel VARCHAR(20) NOT NULL,
  FOREIGN KEY (medicion_id) REFERENCES mediciones(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Alertas asociadas a mediciones';

CREATE TABLE `mantenimientos` (
  id INT PRIMARY KEY,
  estacion_id INT NOT NULL,
  fecha DATE NOT NULL,
  costo DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (estacion_id) REFERENCES estaciones(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Intervenciones en estaciones, no en sensores';
