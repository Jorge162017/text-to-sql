CREATE TABLE `fabricas` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de manufactura';

CREATE TABLE `inspectores` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de manufactura';

CREATE TABLE `insumos` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catalogo propio de manufactura';

CREATE TABLE `lotes` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  fabrica_id INT NOT NULL,
  costo DECIMAL(10,2) NOT NULL,
  activo BOOLEAN NOT NULL,
  FOREIGN KEY (fabrica_id) REFERENCES fabricas(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Recursos de manufactura; costo es un valor del catalogo';

CREATE TABLE `controles` (
  id INT PRIMARY KEY,
  lote_id INT NOT NULL,
  fecha DATE NOT NULL,
  defectos DECIMAL(10,2) NOT NULL,
  estado VARCHAR(20) NOT NULL COMMENT 'ok, pendiente o anulado',
  FOREIGN KEY (lote_id) REFERENCES lotes(id),
  inspector_id INT NOT NULL,
  FOREIGN KEY (inspector_id) REFERENCES inspectores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Eventos de manufactura; la medida es defectos, no dinero salvo indicacion';

CREATE TABLE `consumos` (
  id INT PRIMARY KEY,
  lote_id INT NOT NULL,
  insumo_id INT NOT NULL,
  cantidad DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (lote_id) REFERENCES lotes(id),
  FOREIGN KEY (insumo_id) REFERENCES insumos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Relacion de muchos a muchos entre lotes e insumos';
