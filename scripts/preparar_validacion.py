"""Crea los dos esquemas reservados con casos positivos, negativos y límites.

No crea ni sobrescribe datos/validacion/preguntas_propias.jsonl.
"""
import argparse
from datetime import date, timedelta

from scripts.comun import DATOS
from scripts.generar_datos import insertar, tabla


def biblioteca():
    ddl = [
        tabla('sedes', ['id INT PRIMARY KEY', 'nombre VARCHAR(80) NOT NULL', 'ciudad VARCHAR(60) NOT NULL'], 'Sedes de biblioteca'),
        tabla('autores', ['id INT PRIMARY KEY', 'nombre VARCHAR(80) NOT NULL', 'pais VARCHAR(50) NOT NULL'], 'Autores; cada titulo tiene un autor principal'),
        tabla('titulos', ['id INT PRIMARY KEY', 'nombre VARCHAR(100) NOT NULL', 'autor_id INT NOT NULL', 'anio INT NOT NULL', 'FOREIGN KEY (autor_id) REFERENCES autores(id)'], 'Obras bibliograficas, no ejemplares fisicos'),
        tabla('ejemplares', ['id INT PRIMARY KEY', 'titulo_id INT NOT NULL', 'sede_id INT NOT NULL', 'FOREIGN KEY (titulo_id) REFERENCES titulos(id)', 'FOREIGN KEY (sede_id) REFERENCES sedes(id)'], 'Copias fisicas por sede'),
        tabla('miembros', ['id INT PRIMARY KEY', 'nombre VARCHAR(80) NOT NULL', 'alta DATE NOT NULL', 'correo VARCHAR(100) NULL'], 'Usuarios de biblioteca'),
        tabla('prestamos', ['id INT PRIMARY KEY', 'ejemplar_id INT NOT NULL', 'miembro_id INT NOT NULL', 'inicio DATE NOT NULL', 'vence DATE NOT NULL', "devolucion DATE NULL COMMENT 'NULL significa pendiente de devolver'", 'FOREIGN KEY (ejemplar_id) REFERENCES ejemplares(id)', 'FOREIGN KEY (miembro_id) REFERENCES miembros(id)'], 'Prestamos; usar fecha de corte explicita para atraso'),
    ]
    seed = [
        insertar('sedes', [(1, 'Central', 'Guatemala'), (2, 'Norte', 'Coban'), (3, 'Occidente', 'Xela'), (4, 'Sur', 'Escuintla'), (5, 'Anexo', 'Guatemala')]),
        insertar('autores', [(i, f'Autor {i}', ['Guatemala', 'Mexico', 'Chile'][i % 3]) for i in range(1, 9)] + [(9, 'Autor 1', 'Guatemala')]),
        insertar('titulos', [(i, f'Obra {i:02}', (i - 1) % 7 + 1, 1990 + i) for i in range(1, 21)] + [(21, 'Obra 21', 6, 2024), (22, 'Obra 22', 6, 2024), (23, 'Obra 23', 9, 2021)]),
        insertar('ejemplares', [(i, (i - 1) % 18 + 1, (i - 1) % 4 + 1) for i in range(1, 41)] + [(41, 21, 1), (42, 22, 2), (43, 23, 1), (44, 21, 1)]),
        insertar('miembros', [(i, f'Miembro {i:02}', str(date(2024, 1, 1) + timedelta(days=i * 11)), None if i % 4 == 0 else f'm{i}@example.invalid') for i in range(1, 17)]),
    ]
    filas = []
    for i in range(1, 61):
        inicio = date(2025, 1, 1) + timedelta(days=i * 4)
        filas.append((i, (i - 1) % 35 + 1, (i * 3) % 13 + 1, str(inicio), str(inicio + timedelta(days=14)), None if i % 4 == 0 else str(inicio + timedelta(days=10 + i % 10))))
    filas += [
        (61, 41, 1, '2025-01-01', '2025-01-15', None),
        (62, 42, 1, '2025-01-01', '2025-01-15', '2025-01-10'),
        (63, 44, 2, '2025-12-31', '2026-01-14', None),
        (64, 41, 3, '2026-01-01', '2026-01-15', None),
        (65, 43, 16, '2024-12-31', '2025-01-14', '2025-01-10'),
        (66, 42, 2, '2025-12-31', '2026-01-14', None),
    ]
    seed.append(insertar('prestamos', filas))
    return ddl, seed


def hospital():
    ddl = [
        tabla('especialidades', ['id INT PRIMARY KEY', 'nombre VARCHAR(80) NOT NULL'], 'Especialidades medicas'),
        tabla('medicos', ['id INT PRIMARY KEY', 'nombre VARCHAR(80) NOT NULL', 'especialidad_id INT NOT NULL', 'FOREIGN KEY (especialidad_id) REFERENCES especialidades(id)'], 'Medicos con una especialidad principal'),
        tabla('personas', ['id INT PRIMARY KEY', 'nombre VARCHAR(80) NOT NULL', 'nacimiento DATE NOT NULL', 'municipio VARCHAR(60) NOT NULL'], 'Pacientes ficticios, sin datos personales reales'),
        tabla('citas', ['id INT PRIMARY KEY', 'persona_id INT NOT NULL', 'medico_id INT NOT NULL', 'fecha DATE NOT NULL', "estado VARCHAR(20) NOT NULL COMMENT 'atendida, pendiente o cancelada'", 'FOREIGN KEY (persona_id) REFERENCES personas(id)', 'FOREIGN KEY (medico_id) REFERENCES medicos(id)'], 'Agenda clinica'),
        tabla('procedimientos', ['id INT PRIMARY KEY', 'nombre VARCHAR(80) NOT NULL', 'costo DECIMAL(10,2) NOT NULL'], 'Catalogo de procedimientos'),
        tabla('atenciones', ['id INT PRIMARY KEY', 'cita_id INT NOT NULL', 'procedimiento_id INT NOT NULL', 'cantidad INT NOT NULL', 'FOREIGN KEY (cita_id) REFERENCES citas(id)', 'FOREIGN KEY (procedimiento_id) REFERENCES procedimientos(id)'], 'Procedimientos realizados en una cita'),
    ]
    citas = [(i, (i * 7) % 17 + 1, (i - 1) % 8 + 1,
              str(date(2025, 1, 1) + timedelta(days=i * 3)),
              ['atendida', 'pendiente', 'cancelada'][i % 3]) for i in range(1, 73)]
    citas += [
        (73, 1, 1, '2025-01-01', 'atendida'),
        (74, 1, 1, '2025-12-31', 'atendida'),
        (75, 1, 2, '2025-12-31', 'atendida'),
        (76, 1, 3, '2026-01-01', 'pendiente'),
        (77, 2, 3, '2026-01-02', 'pendiente'),
        (78, 3, 2, '2026-02-01', 'cancelada'),
        (79, 4, 3, '2026-01-02', 'atendida'),
        (80, 21, 10, '2025-06-01', 'atendida'),
        (81, 21, 10, '2025-06-02', 'atendida'),
        (82, 21, 10, '2025-06-03', 'atendida'),
        (83, 21, 10, '2025-06-04', 'atendida'),
        (84, 2, 1, '2025-01-01', 'atendida'),
        (85, 2, 1, '2025-01-01', 'atendida'),
        (86, 1, 1, '2024-12-31', 'cancelada'),
    ]
    seed = [
        insertar('especialidades', [(i, n) for i, n in enumerate(['General', 'Pediatria', 'Cardiologia', 'Dermatologia', 'Neurologia'], 1)]),
        insertar('medicos', [(i, f'Medico {i:02}', (i - 1) % 4 + 1) for i in range(1, 10)] + [(10, 'Medico 01', 3)]),
        insertar('personas', [(i, f'Persona {i:02}', str(date(1980, 1, 1) + timedelta(days=i * 400)), ['Guatemala', 'Antigua', 'Xela'][i % 3]) for i in range(1, 21)] + [(21, 'Persona 01', '2000-01-01', 'Guatemala')]),
        insertar('citas', citas),
        insertar('procedimientos', [(i, f'Procedimiento {i:02}', 50 + (i % 5) * 35.5) for i in range(1, 13)]),
    ]
    filas = []
    for i, _, _, _, estado in citas:
        if estado == 'atendida':
            for j in range(1, i % 2 + 2):
                filas.append((len(filas) + 1, i, (i + j) % 10 + 1, j))
    seed.append(insertar('atenciones', filas))
    return ddl, seed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reemplazar-esquemas', action='store_true')
    args = parser.parse_args()
    nombres = [('val_biblioteca', biblioteca), ('val_hospital', hospital)]
    if not args.reemplazar_esquemas and any((DATOS / 'esquemas' / n).exists() for n, _ in nombres):
        parser.error('Los esquemas ya existen. Respaldar cambios y usar --reemplazar-esquemas para regenerar.')
    for nombre, construir in nombres:
        carpeta = DATOS / 'esquemas' / nombre
        ddl, seed = construir()
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / 'schema.sql').write_text('\n\n'.join(ddl) + '\n', encoding='utf-8')
        (carpeta / 'seed.sql').write_text('\n\n'.join(seed) + '\n', encoding='utf-8')
    print('Dos esquemas reservados preparados; preguntas_propias.jsonl permanece intacto.')


if __name__ == '__main__':
    main()
