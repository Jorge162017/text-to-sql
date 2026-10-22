# Preguntas propias — referencias revisadas

Preguntas recibidas por chat el 22 de octubre de 2026. Autoría según los grupos proporcionados por Jorge: 20 de Jorge Lopez y 20 de Angel Herrarte. El SQL de referencia y las precisiones de redacción fueron preparados con asistencia de IA. La revisión técnica fue completada por el asistente a solicitud de Jorge; no se atribuye una revisión humana no realizada. Usar solo `nombre` fue aprobado expresamente por Jorge.

Archivo operativo: [preguntas_propias.jsonl](preguntas_propias.jsonl). Se conserva `pregunta_original` junto a la versión ajustada; los borradores originales de IA permanecen separados.

## Criterios aplicados

- Libro = título bibliográfico; no ejemplar físico.
- El esquema hospitalario solo tiene `nombre`, sin apellido separado. No se modificó el DDL.
- Las consultas realizadas o pacientes atendidos exigen `estado = atendida`; las citas registradas pueden tener cualquier estado, según se aclara en cada pregunta.
- Los promedios de las preguntas 9 y 29 incluyen a todos los usuarios/pacientes, también los que tienen cero registros.
- Los primeros/últimos y los top tienen desempates explícitos por identificador; los meses empatados se resuelven eligiendo el más temprano.
- Las preguntas 8, 23, 28 y 32 se clasifican como medias por JOIN/agregación. La distribución resultante es 14 fáciles, 16 medias y 10 difíciles; no hay una cuota obligatoria por nivel en el enunciado.
- La 24 exige citas pendientes posteriores al 1 de enero de 2026 y devuelve la cita 77. La 26 exige más de tres citas atendidas por paciente. Ambas tienen casos positivos y negativos en las semillas revisadas; se comprueban límites de fecha, estados y pacientes con nombres repetidos.
- No se requiere entrenar con estas preguntas. Los dos esquemas se mantienen reservados.

## Verificación de esta versión

40 de 40 consultas ejecutables en MySQL 8.4.10 con ONLY_FULL_GROUP_BY; cero descartes. Las 40 referencias también se contrastan con algoritmos Python independientes, conservando duplicados y las reglas de orden. La revisión técnica no garantiza generalización a bases desconocidas. La suma de pesos del conjunto es 76.

## 1. Jorge Lopez — val_biblioteca

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuáles son los títulos y años de publicación de todos los libros registrados?

**Versión ajustada para evaluar:** ¿Cuáles son los títulos y años de publicación de todos los libros registrados? En esta pregunta, libro significa título bibliográfico, no ejemplar físico.

Columnas: `titulo`, `anio`.

```sql
SELECT nombre AS titulo, anio FROM titulos;
```

## 2. Jorge Lopez — val_biblioteca

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué libros fueron publicados después del año 2020? Devuelve el título y el año de publicación.

**Versión ajustada para evaluar:** ¿Qué libros fueron publicados después del año 2020? Devuelve el título y el año de publicación. En esta pregunta, libro significa título bibliográfico, no ejemplar físico.

Columnas: `titulo`, `anio`.

```sql
SELECT nombre AS titulo, anio FROM titulos WHERE anio > 2020;
```

## 3. Jorge Lopez — val_biblioteca

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuáles son los nombres y correos electrónicos de los usuarios registrados?

**Versión ajustada para evaluar:** ¿Cuáles son los nombres y correos electrónicos de los usuarios registrados?

Columnas: `usuario`, `correo`.

```sql
SELECT nombre AS usuario, correo FROM miembros;
```

## 4. Jorge Lopez — val_biblioteca

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué préstamos tienen una fecha de devolución pendiente? Devuelve el identificador del préstamo, el identificador del usuario y la fecha del préstamo.

**Versión ajustada para evaluar:** ¿Qué préstamos tienen una fecha de devolución pendiente? Devuelve el identificador del préstamo, el identificador del usuario y la fecha del préstamo.

Columnas: `prestamo_id`, `usuario_id`, `fecha_prestamo`.

```sql
SELECT id AS prestamo_id, miembro_id AS usuario_id, inicio AS fecha_prestamo FROM prestamos WHERE devolucion IS NULL;
```

## 5. Jorge Lopez — val_biblioteca

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuántos libros tiene registrados cada autor? Devuelve el nombre del autor y la cantidad de libros.

**Versión ajustada para evaluar:** ¿Cuántos libros tiene registrados cada autor? Devuelve el nombre del autor y la cantidad de libros. En esta pregunta, libro significa título bibliográfico, no ejemplar físico. Incluye autores sin títulos, con cantidad cero.

Columnas: `autor`, `cantidad_libros`.

```sql
SELECT a.nombre AS autor, COUNT(t.id) AS cantidad_libros FROM autores a LEFT JOIN titulos t ON t.autor_id = a.id GROUP BY a.id, a.nombre;
```

## 6. Jorge Lopez — val_biblioteca

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué usuarios han realizado más de tres préstamos? Devuelve el nombre del usuario y la cantidad de préstamos.

**Versión ajustada para evaluar:** ¿Qué usuarios han realizado más de tres préstamos? Devuelve el nombre del usuario y la cantidad de préstamos.

Columnas: `usuario`, `cantidad_prestamos`.

```sql
SELECT m.nombre AS usuario, COUNT(p.id) AS cantidad_prestamos FROM miembros m JOIN prestamos p ON p.miembro_id = m.id GROUP BY m.id, m.nombre HAVING COUNT(p.id) > 3;
```

## 7. Jorge Lopez — val_biblioteca

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuáles son los títulos de los libros que han sido prestados? Devuelve el título y la fecha de cada préstamo.

**Versión ajustada para evaluar:** ¿Cuáles son los títulos de los libros que han sido prestados? Devuelve el título y la fecha de cada préstamo. En esta pregunta, libro significa título bibliográfico, no ejemplar físico. Devuelve una fila por préstamo, sin eliminar filas repetidas de título y fecha.

Columnas: `titulo`, `fecha_prestamo`.

```sql
SELECT t.nombre AS titulo, p.inicio AS fecha_prestamo FROM prestamos p JOIN ejemplares e ON e.id = p.ejemplar_id JOIN titulos t ON t.id = e.titulo_id;
```

## 8. Jorge Lopez — val_biblioteca

Nivel: **media** · peso: **2** · orden obligatorio: **sí**.

**Pregunta original recibida:** ¿Cuáles son los cinco libros más prestados? Devuelve el título y la cantidad de préstamos, ordenados de mayor a menor.

**Versión ajustada para evaluar:** ¿Cuáles son los cinco libros más prestados? Devuelve el título y la cantidad de préstamos, ordenados de mayor a menor. En esta pregunta, libro significa título bibliográfico, no ejemplar físico. Considera solo títulos con al menos un préstamo. En empate, prioriza el menor identificador del título.

Columnas: `titulo`, `cantidad_prestamos`.

```sql
SELECT t.nombre AS titulo, COUNT(p.id) AS cantidad_prestamos FROM titulos t JOIN ejemplares e ON e.titulo_id = t.id JOIN prestamos p ON p.ejemplar_id = e.id GROUP BY t.id, t.nombre ORDER BY cantidad_prestamos DESC, t.id ASC LIMIT 5;
```

## 9. Jorge Lopez — val_biblioteca

Nivel: **dificil** · peso: **3** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué usuarios han realizado más préstamos que el promedio de préstamos por usuario? Devuelve su nombre y la cantidad de préstamos.

**Versión ajustada para evaluar:** ¿Qué usuarios han realizado más préstamos que el promedio de préstamos por usuario? Devuelve su nombre y la cantidad de préstamos. Calcula el promedio sobre todos los usuarios registrados, incluidos quienes tienen cero préstamos.

Columnas: `usuario`, `cantidad_prestamos`.

```sql
WITH conteos AS (SELECT m.id, m.nombre, COUNT(p.id) AS cantidad_prestamos FROM miembros m LEFT JOIN prestamos p ON p.miembro_id = m.id GROUP BY m.id, m.nombre) SELECT nombre AS usuario, cantidad_prestamos FROM conteos WHERE cantidad_prestamos > (SELECT AVG(cantidad_prestamos) FROM conteos);
```

## 10. Jorge Lopez — val_biblioteca

Nivel: **dificil** · peso: **3** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuál es el libro más recientemente publicado de cada autor? Devuelve el nombre del autor, el título y el año de publicación.

**Versión ajustada para evaluar:** ¿Cuál es el libro más recientemente publicado de cada autor? Devuelve el nombre del autor, el título y el año de publicación. En esta pregunta, libro significa título bibliográfico, no ejemplar físico. Considera autores con títulos registrados. Si varios títulos comparten el año más reciente, elige el de menor identificador.

Columnas: `autor`, `titulo`, `anio`.

```sql
WITH ordenados AS (SELECT id, nombre, anio, autor_id, ROW_NUMBER() OVER (PARTITION BY autor_id ORDER BY anio DESC, id ASC) AS rn FROM titulos) SELECT a.nombre AS autor, t.nombre AS titulo, t.anio FROM ordenados t JOIN autores a ON a.id = t.autor_id WHERE t.rn = 1;
```

## 11. Angel Herrarte — val_biblioteca

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué libros fueron publicados antes del año 2010? Devuelve el título y el año de publicación.

**Versión ajustada para evaluar:** ¿Qué libros fueron publicados antes del año 2010? Devuelve el título y el año de publicación. En esta pregunta, libro significa título bibliográfico, no ejemplar físico.

Columnas: `titulo`, `anio`.

```sql
SELECT nombre AS titulo, anio FROM titulos WHERE anio < 2010;
```

## 12. Angel Herrarte — val_biblioteca

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuántos usuarios están registrados en la biblioteca? Devuelve el total de usuarios.

**Versión ajustada para evaluar:** ¿Cuántos usuarios están registrados en la biblioteca? Devuelve el total de usuarios.

Columnas: `total_usuarios`.

```sql
SELECT COUNT(*) AS total_usuarios FROM miembros;
```

## 13. Angel Herrarte — val_biblioteca

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuáles son los préstamos realizados durante el año 2025? Devuelve el identificador del préstamo y la fecha del préstamo.

**Versión ajustada para evaluar:** ¿Cuáles son los préstamos realizados durante el año 2025? Devuelve el identificador del préstamo y la fecha del préstamo.

Columnas: `prestamo_id`, `fecha_prestamo`.

```sql
SELECT id AS prestamo_id, inicio AS fecha_prestamo FROM prestamos WHERE inicio >= '2025-01-01' AND inicio < '2026-01-01';
```

## 14. Angel Herrarte — val_biblioteca

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuántos libros hay registrados en total? Devuelve la cantidad de libros.

**Versión ajustada para evaluar:** ¿Cuántos libros hay registrados en total? Devuelve la cantidad de libros. En esta pregunta, libro significa título bibliográfico, no ejemplar físico.

Columnas: `cantidad_libros`.

```sql
SELECT COUNT(*) AS cantidad_libros FROM titulos;
```

## 15. Angel Herrarte — val_biblioteca

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuántos préstamos ha realizado cada usuario? Devuelve el nombre del usuario y la cantidad de préstamos, incluyendo usuarios sin préstamos.

**Versión ajustada para evaluar:** ¿Cuántos préstamos ha realizado cada usuario? Devuelve el nombre del usuario y la cantidad de préstamos, incluyendo usuarios sin préstamos.

Columnas: `usuario`, `cantidad_prestamos`.

```sql
SELECT m.nombre AS usuario, COUNT(p.id) AS cantidad_prestamos FROM miembros m LEFT JOIN prestamos p ON p.miembro_id = m.id GROUP BY m.id, m.nombre;
```

## 16. Angel Herrarte — val_biblioteca

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué autores tienen más de dos libros registrados? Devuelve el nombre del autor y la cantidad de libros.

**Versión ajustada para evaluar:** ¿Qué autores tienen más de dos libros registrados? Devuelve el nombre del autor y la cantidad de libros. En esta pregunta, libro significa título bibliográfico, no ejemplar físico.

Columnas: `autor`, `cantidad_libros`.

```sql
SELECT a.nombre AS autor, COUNT(t.id) AS cantidad_libros FROM autores a JOIN titulos t ON t.autor_id = a.id GROUP BY a.id, a.nombre HAVING COUNT(t.id) > 2;
```

## 17. Angel Herrarte — val_biblioteca

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuáles son los usuarios que tienen préstamos pendientes de devolución? Devuelve el nombre del usuario, el título del libro y la fecha del préstamo.

**Versión ajustada para evaluar:** ¿Cuáles son los usuarios que tienen préstamos pendientes de devolución? Devuelve el nombre del usuario, el título del libro y la fecha del préstamo. En esta pregunta, libro significa título bibliográfico, no ejemplar físico.

Columnas: `usuario`, `titulo`, `fecha_prestamo`.

```sql
SELECT m.nombre AS usuario, t.nombre AS titulo, p.inicio AS fecha_prestamo FROM prestamos p JOIN miembros m ON m.id = p.miembro_id JOIN ejemplares e ON e.id = p.ejemplar_id JOIN titulos t ON t.id = e.titulo_id WHERE p.devolucion IS NULL;
```

## 18. Angel Herrarte — val_biblioteca

Nivel: **dificil** · peso: **3** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué libros nunca han sido prestados? Devuelve el título y el año de publicación.

**Versión ajustada para evaluar:** ¿Qué libros nunca han sido prestados? Devuelve el título y el año de publicación. En esta pregunta, libro significa título bibliográfico, no ejemplar físico.

Columnas: `titulo`, `anio`.

```sql
SELECT t.nombre AS titulo, t.anio FROM titulos t WHERE NOT EXISTS (SELECT 1 FROM ejemplares e JOIN prestamos p ON p.ejemplar_id = e.id WHERE e.titulo_id = t.id);
```

## 19. Angel Herrarte — val_biblioteca

Nivel: **dificil** · peso: **3** · orden obligatorio: **sí**.

**Pregunta original recibida:** ¿Cuál fue el mes con mayor cantidad de préstamos durante 2025? Devuelve el mes y la cantidad de préstamos.

**Versión ajustada para evaluar:** ¿Cuál fue el mes con mayor cantidad de préstamos durante 2025? Devuelve el mes y la cantidad de préstamos. Devuelve el mes como número del 1 al 12. En empate, elige el mes más temprano. Considera meses con préstamos.

Columnas: `mes`, `cantidad_prestamos`.

```sql
WITH meses AS (SELECT MONTH(inicio) AS mes, COUNT(*) AS cantidad_prestamos FROM prestamos WHERE inicio >= '2025-01-01' AND inicio < '2026-01-01' GROUP BY MONTH(inicio)) SELECT mes, cantidad_prestamos FROM meses ORDER BY cantidad_prestamos DESC, mes ASC LIMIT 1;
```

## 20. Angel Herrarte — val_biblioteca

Nivel: **dificil** · peso: **3** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuál fue el primer préstamo realizado por cada usuario? Devuelve el nombre del usuario, el título del libro y la fecha del préstamo.

**Versión ajustada para evaluar:** ¿Cuál fue el primer préstamo realizado por cada usuario? Devuelve el nombre del usuario, el título del libro y la fecha del préstamo. En esta pregunta, libro significa título bibliográfico, no ejemplar físico. Considera usuarios con préstamos. En empate de fecha, elige el préstamo de menor identificador.

Columnas: `usuario`, `titulo`, `fecha_prestamo`.

```sql
WITH ordenados AS (SELECT id, miembro_id, ejemplar_id, inicio, ROW_NUMBER() OVER (PARTITION BY miembro_id ORDER BY inicio ASC, id ASC) AS rn FROM prestamos) SELECT m.nombre AS usuario, t.nombre AS titulo, p.inicio AS fecha_prestamo FROM ordenados p JOIN miembros m ON m.id = p.miembro_id JOIN ejemplares e ON e.id = p.ejemplar_id JOIN titulos t ON t.id = e.titulo_id WHERE p.rn = 1;
```

## 21. Jorge Lopez — val_hospital

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuáles son los nombres y apellidos de todos los pacientes registrados?

**Versión ajustada para evaluar:** ¿Cuáles son los nombres de todos los pacientes registrados?

Columnas: `paciente`.

```sql
SELECT nombre AS paciente FROM personas;
```

## 22. Jorge Lopez — val_hospital

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué pacientes nacieron después del 1 de enero de 2000? Devuelve su nombre, apellido y fecha de nacimiento.

**Versión ajustada para evaluar:** ¿Qué pacientes nacieron después del 1 de enero de 2000? Devuelve su nombre y fecha de nacimiento.

Columnas: `paciente`, `fecha_nacimiento`.

```sql
SELECT nombre AS paciente, nacimiento AS fecha_nacimiento FROM personas WHERE nacimiento > '2000-01-01';
```

## 23. Jorge Lopez — val_hospital

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuáles son los nombres y especialidades de todos los médicos registrados?

**Versión ajustada para evaluar:** ¿Cuáles son los nombres y especialidades de todos los médicos registrados?

Columnas: `medico`, `especialidad`.

```sql
SELECT m.nombre AS medico, e.nombre AS especialidad FROM medicos m JOIN especialidades e ON e.id = m.especialidad_id;
```

## 24. Jorge Lopez — val_hospital

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué citas médicas están programadas para después del 1 de enero de 2026? Devuelve el identificador de la cita, el identificador del paciente y la fecha.

**Versión ajustada para evaluar:** ¿Qué citas médicas están programadas para después del 1 de enero de 2026? Devuelve el identificador de la cita, el identificador del paciente y la fecha. Considera únicamente citas pendientes, por tratarse de citas programadas.

Columnas: `cita_id`, `paciente_id`, `fecha`.

```sql
SELECT id AS cita_id, persona_id AS paciente_id, fecha FROM citas WHERE fecha > '2026-01-01' AND estado = 'pendiente';
```

## 25. Jorge Lopez — val_hospital

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuántas citas tiene asignadas cada médico? Devuelve su nombre y la cantidad de citas.

**Versión ajustada para evaluar:** ¿Cuántas citas tiene asignadas cada médico? Devuelve su nombre y la cantidad de citas. Incluye médicos sin citas con cantidad cero y cuenta citas de todos los estados.

Columnas: `medico`, `cantidad_citas`.

```sql
SELECT m.nombre AS medico, COUNT(c.id) AS cantidad_citas FROM medicos m LEFT JOIN citas c ON c.medico_id = m.id GROUP BY m.id, m.nombre;
```

## 26. Jorge Lopez — val_hospital

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué pacientes han tenido más de tres consultas médicas? Devuelve el nombre del paciente y la cantidad de consultas.

**Versión ajustada para evaluar:** ¿Qué pacientes han tenido más de tres consultas médicas? Devuelve el nombre del paciente y la cantidad de consultas. Una consulta realizada corresponde a una cita con estado atendida.

Columnas: `paciente`, `cantidad_consultas`.

```sql
SELECT p.nombre AS paciente, COUNT(c.id) AS cantidad_consultas FROM personas p JOIN citas c ON c.persona_id = p.id WHERE c.estado = 'atendida' GROUP BY p.id, p.nombre HAVING COUNT(c.id) > 3;
```

## 27. Jorge Lopez — val_hospital

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuáles son los pacientes atendidos por cada médico? Devuelve el nombre del paciente, el nombre del médico y la fecha de la cita.

**Versión ajustada para evaluar:** ¿Cuáles son los pacientes atendidos por cada médico? Devuelve el nombre del paciente, el nombre del médico y la fecha de la cita. Considera solo citas con estado atendida. Devuelve una fila por cita, sin eliminar repeticiones.

Columnas: `paciente`, `medico`, `fecha`.

```sql
SELECT p.nombre AS paciente, m.nombre AS medico, c.fecha FROM citas c JOIN personas p ON p.id = c.persona_id JOIN medicos m ON m.id = c.medico_id WHERE c.estado = 'atendida';
```

## 28. Jorge Lopez — val_hospital

Nivel: **media** · peso: **2** · orden obligatorio: **sí**.

**Pregunta original recibida:** ¿Cuáles son los cinco médicos con mayor cantidad de citas atendidas? Devuelve su nombre, especialidad y cantidad de citas, ordenados de mayor a menor.

**Versión ajustada para evaluar:** ¿Cuáles son los cinco médicos con mayor cantidad de citas atendidas? Devuelve su nombre, especialidad y cantidad de citas, ordenados de mayor a menor. Cuenta solo citas con estado atendida e incluye médicos con cantidad cero. En empate, prioriza el menor identificador del médico.

Columnas: `medico`, `especialidad`, `cantidad_citas`.

```sql
SELECT m.nombre AS medico, e.nombre AS especialidad, COUNT(c.id) AS cantidad_citas FROM medicos m JOIN especialidades e ON e.id = m.especialidad_id LEFT JOIN citas c ON c.medico_id = m.id AND c.estado = 'atendida' GROUP BY m.id, m.nombre, e.id, e.nombre ORDER BY cantidad_citas DESC, m.id ASC LIMIT 5;
```

## 29. Jorge Lopez — val_hospital

Nivel: **dificil** · peso: **3** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué pacientes han tenido más citas que el promedio de citas por paciente? Devuelve su nombre y cantidad de citas.

**Versión ajustada para evaluar:** ¿Qué pacientes han tenido más citas que el promedio de citas por paciente? Devuelve su nombre y cantidad de citas. Cuenta citas de todos los estados y calcula el promedio sobre todos los pacientes registrados, incluidos quienes tienen cero citas.

Columnas: `paciente`, `cantidad_citas`.

```sql
WITH conteos AS (SELECT p.id, p.nombre, COUNT(c.id) AS cantidad_citas FROM personas p LEFT JOIN citas c ON c.persona_id = p.id GROUP BY p.id, p.nombre) SELECT nombre AS paciente, cantidad_citas FROM conteos WHERE cantidad_citas > (SELECT AVG(cantidad_citas) FROM conteos);
```

## 30. Jorge Lopez — val_hospital

Nivel: **dificil** · peso: **3** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuál fue la cita más reciente de cada paciente? Devuelve el nombre del paciente, el nombre del médico y la fecha de la cita.

**Versión ajustada para evaluar:** ¿Cuál fue la cita más reciente de cada paciente? Devuelve el nombre del paciente, el nombre del médico y la fecha de la cita. Considera pacientes con citas de cualquier estado. En empate de fecha, elige la cita de mayor identificador.

Columnas: `paciente`, `medico`, `fecha`.

```sql
WITH ordenadas AS (SELECT id, persona_id, medico_id, fecha, ROW_NUMBER() OVER (PARTITION BY persona_id ORDER BY fecha DESC, id DESC) AS rn FROM citas) SELECT p.nombre AS paciente, m.nombre AS medico, c.fecha FROM ordenadas c JOIN personas p ON p.id = c.persona_id JOIN medicos m ON m.id = c.medico_id WHERE c.rn = 1;
```

## 31. Angel Herrarte — val_hospital

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuántos médicos hay registrados en el hospital? Devuelve la cantidad total.

**Versión ajustada para evaluar:** ¿Cuántos médicos hay registrados en el hospital? Devuelve la cantidad total.

Columnas: `cantidad_medicos`.

```sql
SELECT COUNT(*) AS cantidad_medicos FROM medicos;
```

## 32. Angel Herrarte — val_hospital

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuáles son los médicos cuya especialidad es Cardiología? Devuelve su nombre y apellido.

**Versión ajustada para evaluar:** ¿Cuáles son los médicos cuya especialidad es Cardiología? Devuelve su nombre.

Columnas: `medico`.

```sql
SELECT m.nombre AS medico FROM medicos m JOIN especialidades e ON e.id = m.especialidad_id WHERE e.nombre = 'Cardiologia';
```

## 33. Angel Herrarte — val_hospital

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuántos pacientes hay registrados en total? Devuelve la cantidad de pacientes.

**Versión ajustada para evaluar:** ¿Cuántos pacientes hay registrados en total? Devuelve la cantidad de pacientes.

Columnas: `cantidad_pacientes`.

```sql
SELECT COUNT(*) AS cantidad_pacientes FROM personas;
```

## 34. Angel Herrarte — val_hospital

Nivel: **facil** · peso: **1** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué citas médicas se realizaron durante el año 2025? Devuelve el identificador de la cita y la fecha.

**Versión ajustada para evaluar:** ¿Qué citas médicas se realizaron durante el año 2025? Devuelve el identificador de la cita y la fecha. Considera solo citas con estado atendida, porque se pregunta por citas realizadas.

Columnas: `cita_id`, `fecha`.

```sql
SELECT id AS cita_id, fecha FROM citas WHERE fecha >= '2025-01-01' AND fecha < '2026-01-01' AND estado = 'atendida';
```

## 35. Angel Herrarte — val_hospital

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuántos pacientes diferentes ha atendido cada médico? Devuelve el nombre del médico y la cantidad de pacientes.

**Versión ajustada para evaluar:** ¿Cuántos pacientes diferentes ha atendido cada médico? Devuelve el nombre del médico y la cantidad de pacientes. Considera solo citas con estado atendida, cuenta cada paciente una vez por médico e incluye médicos sin pacientes con cantidad cero.

Columnas: `medico`, `cantidad_pacientes`.

```sql
SELECT m.nombre AS medico, COUNT(DISTINCT c.persona_id) AS cantidad_pacientes FROM medicos m LEFT JOIN citas c ON c.medico_id = m.id AND c.estado = 'atendida' GROUP BY m.id, m.nombre;
```

## 36. Angel Herrarte — val_hospital

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué especialidades médicas tienen más de dos médicos registrados? Devuelve la especialidad y la cantidad de médicos.

**Versión ajustada para evaluar:** ¿Qué especialidades médicas tienen más de dos médicos registrados? Devuelve la especialidad y la cantidad de médicos.

Columnas: `especialidad`, `cantidad_medicos`.

```sql
SELECT e.nombre AS especialidad, COUNT(m.id) AS cantidad_medicos FROM especialidades e JOIN medicos m ON m.especialidad_id = e.id GROUP BY e.id, e.nombre HAVING COUNT(m.id) > 2;
```

## 37. Angel Herrarte — val_hospital

Nivel: **media** · peso: **2** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué pacientes han sido atendidos por médicos de Cardiología? Devuelve el nombre del paciente, el nombre del médico y la fecha de la cita.

**Versión ajustada para evaluar:** ¿Qué pacientes han sido atendidos por médicos de Cardiología? Devuelve el nombre del paciente, el nombre del médico y la fecha de la cita. Considera solo citas con estado atendida. Devuelve una fila por cita, sin eliminar repeticiones.

Columnas: `paciente`, `medico`, `fecha`.

```sql
SELECT p.nombre AS paciente, m.nombre AS medico, c.fecha FROM citas c JOIN personas p ON p.id = c.persona_id JOIN medicos m ON m.id = c.medico_id JOIN especialidades e ON e.id = m.especialidad_id WHERE e.nombre = 'Cardiologia' AND c.estado = 'atendida';
```

## 38. Angel Herrarte — val_hospital

Nivel: **dificil** · peso: **3** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Qué médicos no tienen ninguna cita registrada? Devuelve su nombre, apellido y especialidad.

**Versión ajustada para evaluar:** ¿Qué médicos no tienen ninguna cita registrada? Devuelve su nombre y especialidad.

Columnas: `medico`, `especialidad`.

```sql
SELECT m.nombre AS medico, e.nombre AS especialidad FROM medicos m JOIN especialidades e ON e.id = m.especialidad_id WHERE NOT EXISTS (SELECT 1 FROM citas c WHERE c.medico_id = m.id);
```

## 39. Angel Herrarte — val_hospital

Nivel: **dificil** · peso: **3** · orden obligatorio: **sí**.

**Pregunta original recibida:** ¿Cuál fue el mes con mayor cantidad de citas médicas durante el año 2025? Devuelve el mes y la cantidad de citas.

**Versión ajustada para evaluar:** ¿Cuál fue el mes con mayor cantidad de citas médicas durante el año 2025? Devuelve el mes y la cantidad de citas. Cuenta citas de todos los estados. Devuelve el mes como número del 1 al 12. En empate, elige el mes más temprano. Considera meses con citas.

Columnas: `mes`, `cantidad_citas`.

```sql
WITH meses AS (SELECT MONTH(fecha) AS mes, COUNT(*) AS cantidad_citas FROM citas WHERE fecha >= '2025-01-01' AND fecha < '2026-01-01' GROUP BY MONTH(fecha)) SELECT mes, cantidad_citas FROM meses ORDER BY cantidad_citas DESC, mes ASC LIMIT 1;
```

## 40. Angel Herrarte — val_hospital

Nivel: **dificil** · peso: **3** · orden obligatorio: **no**.

**Pregunta original recibida:** ¿Cuál fue la primera cita médica de cada paciente? Devuelve el nombre del paciente, el nombre del médico y la fecha de la cita.

**Versión ajustada para evaluar:** ¿Cuál fue la primera cita médica de cada paciente? Devuelve el nombre del paciente, el nombre del médico y la fecha de la cita. Considera pacientes con citas de cualquier estado. En empate de fecha, elige la cita de menor identificador.

Columnas: `paciente`, `medico`, `fecha`.

```sql
WITH ordenadas AS (SELECT id, persona_id, medico_id, fecha, ROW_NUMBER() OVER (PARTITION BY persona_id ORDER BY fecha ASC, id ASC) AS rn FROM citas) SELECT p.nombre AS paciente, m.nombre AS medico, c.fecha FROM ordenadas c JOIN personas p ON p.id = c.persona_id JOIN medicos m ON m.id = c.medico_id WHERE c.rn = 1;
```
