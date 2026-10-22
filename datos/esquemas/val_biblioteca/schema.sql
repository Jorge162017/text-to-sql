CREATE TABLE `sedes` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  ciudad VARCHAR(60) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Sedes de biblioteca';

CREATE TABLE `autores` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  pais VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Autores; cada titulo tiene un autor principal';

CREATE TABLE `titulos` (
  id INT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  autor_id INT NOT NULL,
  anio INT NOT NULL,
  FOREIGN KEY (autor_id) REFERENCES autores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Obras bibliograficas, no ejemplares fisicos';

CREATE TABLE `ejemplares` (
  id INT PRIMARY KEY,
  titulo_id INT NOT NULL,
  sede_id INT NOT NULL,
  FOREIGN KEY (titulo_id) REFERENCES titulos(id),
  FOREIGN KEY (sede_id) REFERENCES sedes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Copias fisicas por sede';

CREATE TABLE `miembros` (
  id INT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  alta DATE NOT NULL,
  correo VARCHAR(100) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Usuarios de biblioteca';

CREATE TABLE `prestamos` (
  id INT PRIMARY KEY,
  ejemplar_id INT NOT NULL,
  miembro_id INT NOT NULL,
  inicio DATE NOT NULL,
  vence DATE NOT NULL,
  devolucion DATE NULL COMMENT 'NULL significa pendiente de devolver',
  FOREIGN KEY (ejemplar_id) REFERENCES ejemplares(id),
  FOREIGN KEY (miembro_id) REFERENCES miembros(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Prestamos; usar fecha de corte explicita para atraso';
