CREATE TABLE `centros` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de logistica';

CREATE TABLE `vehiculos` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de logistica';

CREATE TABLE `conductores` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de logistica';

CREATE TABLE `rutas` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  origen_id INT NOT NULL,
  distancia DECIMAL(10,2) NOT NULL,
  activa BOOLEAN NOT NULL,
  FOREIGN KEY (origen_id) REFERENCES centros(id),
  destino_id INT NOT NULL,
  FOREIGN KEY (destino_id) REFERENCES centros(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Recursos de logistica; distancia es un valor del catalogo';

CREATE TABLE `envios` (
  id INT PRIMARY KEY,
  ruta_id INT NOT NULL,
  fecha DATE NOT NULL,
  peso DECIMAL(10,2) NOT NULL,
  estado VARCHAR(20) NOT NULL COMMENT 'ok, pendiente o anulado',
  FOREIGN KEY (ruta_id) REFERENCES rutas(id),
  vehiculo_id INT NOT NULL,
  conductor_id INT NOT NULL,
  FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id),
  FOREIGN KEY (conductor_id) REFERENCES conductores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Eventos de logistica; la medida es peso, no dinero salvo indicacion';

CREATE TABLE `eventos_envio` (
  id INT PRIMARY KEY,
  envio_id INT NOT NULL,
  fecha DATE NOT NULL,
  descripcion VARCHAR(50) NOT NULL,
  FOREIGN KEY (envio_id) REFERENCES envios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Seguimiento: varias filas por envio';
