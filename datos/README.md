# Datos de entrenamiento y validación

## Fuentes y separación

Los datos de entrenamiento, DDL y semillas son sintéticos, diseñados con asistencia de IA. No se descargaron datasets externos, no contienen datos personales reales ni tienen traducciones de terceros. Las direcciones `example.invalid` son ficticias. No se ha establecido una licencia de redistribución del repositorio.

`particiones.json` define **15 esquemas de entrenamiento** y **dos de validación**. La separación es por esquema completo. Nunca incorporar `val_biblioteca`, `val_hospital`, sus preguntas ni sus resultados al entrenamiento o few-shot. La verificación rechaza referencias SQL explícitas a otros esquemas.

| Entrenamiento | Pares | Relaciones principales |
| --- | ---: | --- |
| Diez dominios comerciales | 2,400 | Contacto → cabecera → líneas; catálogo, categorías y pagos parciales |
| Academia | 200 | Áreas, profesores, asignaturas, alumnos, inscripciones y prerrequisitos entre asignaturas |
| Logística | 200 | Rutas con origen/destino, envíos, conductores, vehículos y seguimiento |
| Turismo | 200 | Destinos, hoteles, habitaciones, viajeros, estancias y cargos adicionales |
| Energía | 200 | Regiones, estaciones, sensores, mediciones, alertas y mantenimientos |
| Manufactura | 200 | Fábricas, lotes, controles, inspectores, insumos y consumos |

Todos tienen seis tablas. La auditoría encuentra **seis topologías distintas de claves foráneas**, ignorando los nombres; no se cuenta cambiar solo nombres como diversidad estructural. Hay 66 familias y 3,400 pares; los cambios de parámetros no son nuevas familias. Se conserva la limitación de generación por plantillas y falta demostrar generalización con el modelo.

## Archivos necesarios

| Ruta | Uso |
| --- | --- |
| `esquemas/<id>/schema.sql` | DDL con claves, tipos y comentarios |
| `esquemas/<id>/seed.sql` | Filas sintéticas reproducibles |
| `esquemas/<id>/show_create.sql` | DDL real con comentarios, exportado de MySQL |
| `candidatos/entrenamiento.jsonl` | Entrada completa al filtro de ejecución |
| `entrenamiento/pares.jsonl` | Pares aceptados, con DDL real y marca de validación MySQL |
| `descartes/entrenamiento.jsonl` | Rechazos y motivos; actualmente vacío porque todos pasan |
| `validacion/preguntas_propias.jsonl` | Fuente de cuarenta preguntas recibidas; originales, ajustes y SQL |
| `validacion/PREGUNTAS.md` | Vista legible de las preguntas y referencias revisadas |
| `validacion/pares.jsonl` | Las cuarenta referencias aceptadas con DDL |
| `validacion/referencias_resultados.jsonl` | Resultados completos por referencia |
| `descartes/validacion_propia.jsonl` | Rechazos de validación; actualmente vacío |
| `../resultados/ejecucion_entrenamiento.jsonl` | Resultados y tiempos de todos los pares de entrenamiento |
| `../resultados/reporte_datos.json` | Motor, conteos, descartes, particiones y hashes |
| `../resultados/revision_semantica.json` | Contraste independiente de los 3,440 resultados |

Se eliminaron los borradores IA preliminares y sus resultados, ya reemplazados por las preguntas propias. No se eliminó la evidencia exigida para reproducir y auditar la entrega.

## Preguntas propias

Recibidas por chat el **22 de octubre de 2026**, con autoría declarada por Jorge: Jorge Lopez, preguntas 1–10 y 21–30; Angel Herrarte, 11–20 y 31–40. Se mantienen `pregunta_original` y `nivel_original`. El SQL y las precisiones de redacción están identificados como asistencia de IA. La fecha corresponde al día de recepción; no se afirma verificación independiente de autoría ni revisión humana no realizada.

Distribución: **14 fáciles, 16 medias y 10 difíciles**, peso total **76**. Los niveles 8, 23, 28 y 32 se ajustaron a medios por JOIN/agregación. La distribución sugerida en el plan no era una cuota del enunciado.

Criterios aplicados: libro = título bibliográfico; solo `nombre` en hospital; citas realizadas = estado `atendida`; promedios incluyendo registros con cero; desempates por identificador y mes más temprano. El detalle figura en [PREGUNTAS.md](validacion/PREGUNTAS.md).

Las semillas contienen ahora positivos y negativos para las cuarenta preguntas. En particular, la pregunta 24 debe seleccionar únicamente la cita 77; existen citas en la fecha límite, canceladas y atendidas posteriores que deben excluirse. La pregunta 26 tiene pacientes con más de tres citas atendidas y nombres repetidos; no se deben agrupar pacientes por nombre. También hay usuarios/autores/médicos sin relaciones, NULL y empates de fechas y años.

Para modificar una pregunta, editar `preguntas_propias.jsonl`, ajustar SQL y columnas, y regenerar la evidencia. Los generadores de datos no crean ni reemplazan ese archivo.

## Formato y ejecución

Cada línea de entrenamiento tiene `id`, `esquema_id`, `pregunta`, `sql`, `nivel`, `peso`, `familia`, `procedencia` y `semilla`. Tras certificar se agregan `esquema` (SHOW CREATE TABLE), `validado_mysql` y `filas_resultado`.

Validación agrega autor, fecha, columnas esperadas y si exige orden. Pesos: fácil 1, media 2, difícil 3. Los decimales de resultados se serializan como cadenas para conservar precisión, las fechas en ISO y `tipos_mysql` identifica cada columna. El evaluador de Angel debe comparar resultados, no cadenas SQL, conservar duplicados y aplicar las reglas del enunciado.

Ejecutar desde la raíz siguiendo el README: primero MySQL, después `scripts.validar_datos`, `scripts.revisar_muestra` y `scripts.auditar_datos --exigir-cierre`. El contraste usa cálculos Python sobre filas fuente; no usa el SQL de referencia como oráculo de sí mismo. Cubre las 3,400 consultas de entrenamiento y las cuarenta de validación en las semillas actuales.

La importación habilita scripts administrativos propios; las consultas candidatas usan un usuario temporal SELECT, sin múltiples sentencias, en transacciones READ ONLY y con un límite de tres segundos por consulta. Se exige MySQL 8.4.10 y ONLY_FULL_GROUP_BY; el motor conserva la configuración predeterminada. No conectar el importador a un servidor de uso general.

Los generadores protegen datos existentes. `scripts.generar_datos --reemplazar` y `scripts.preparar_validacion --reemplazar-esquemas` regeneran solo fuentes sintéticas. `scripts.validar_datos --inicializar --recrear` elimina y repuebla únicamente las bases del manifiesto. Después hay que repetir revisión semántica y auditoría: borrar evidencia o modificar sus fuentes invalida el cierre.
