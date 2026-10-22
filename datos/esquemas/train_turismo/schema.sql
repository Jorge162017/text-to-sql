CREATE TABLE `destinos` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de turismo';

CREATE TABLE `viajeros` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de turismo';

CREATE TABLE `hoteles` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  destino_id INT NOT NULL,
  tarifa DECIMAL(10,2) NOT NULL,
  activo BOOLEAN NOT NULL,
  FOREIGN KEY (destino_id) REFERENCES destinos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Recursos de turismo; tarifa es un valor del catalogo';

CREATE TABLE `habitaciones` (
  id INT PRIMARY KEY,
  hotel_id INT NOT NULL,
  numero INT NOT NULL,
  FOREIGN KEY (hotel_id) REFERENCES hoteles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Habitaciones fisicas de cada hotel';

CREATE TABLE `estancias` (
  id INT PRIMARY KEY,
  hotel_id INT NOT NULL,
  fecha DATE NOT NULL,
  noches DECIMAL(10,2) NOT NULL,
  estado VARCHAR(20) NOT NULL COMMENT 'ok, pendiente o anulado',
  FOREIGN KEY (hotel_id) REFERENCES hoteles(id),
  viajero_id INT NOT NULL,
  habitacion_id INT NOT NULL,
  FOREIGN KEY (viajero_id) REFERENCES viajeros(id),
  FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Eventos de turismo; la medida es noches, no dinero salvo indicacion';

CREATE TABLE `extras` (
  id INT PRIMARY KEY,
  estancia_id INT NOT NULL,
  importe DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (estancia_id) REFERENCES estancias(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Cargos adicionales por estancia; no confundir con noches';
