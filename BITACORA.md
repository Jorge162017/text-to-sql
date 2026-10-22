# Bitácora del proyecto

Fechas expresadas en America/Guatemala, salvo los campos `fecha_utc` de reportes técnicos. Registrar únicamente hechos reales. No imputar horas humanas ni atribuir revisión de Jorge o Angel a tareas ejecutadas por el asistente. Ellos completarán su tiempo y revisión cuando ocurran.

## 2026-10-21 — Preparación de la etapa de datos

- Autor del registro y ejecución: asistente de IA, durante el turno de Jorge Lopez y por su solicitud. Revisión de Jorge: pendiente.
- Trabajo: estructura de datos, Compose con MySQL 8.4.10, dependencia PyMySQL, generación reproducible de diez esquemas comerciales y 2,400 candidatos; dos esquemas reservados y cuarenta propuestas IA separadas.
- Evidencia: `compose.yaml`, `requirements.txt`, `scripts/generar_datos.py`, `scripts/preparar_validacion.py`, `datos/particiones.json` y `datos/esquemas/`.
- Decisión: no crear preguntas con autoría humana ficticia. Jorge confirmó que todavía no tienen preguntas propias. `preguntas_propias.jsonl` queda pendiente de su redacción.
- Tiempo humano: no registrado; Jorge lo completará al revisar. No se generaron commits ni se subieron cambios, conforme a su instrucción.

## 2026-10-21 — Certificación SQL y comprobaciones iniciales

- Autor del registro y ejecución: asistente de IA, durante el turno de Jorge Lopez. Revisión de Jorge: pendiente.
- Trabajo: iniciar Docker, crear las doce bases aisladas y ejecutar los candidatos en MySQL 8.4.10 con modo predeterminado y `ONLY_FULL_GROUP_BY`. Se usó un lector temporal con privilegios SELECT y transacciones de solo lectura.
- Resultado: 2,400 pares aceptados, cero descartes; 640 fáciles, 960 medios y 800 difíciles. Hay 130 resultados vacíos registrados. Los 40 borradores IA también se ejecutan, pero no constituyen validación propia humana.
- Comprobación semántica automática: 70 resultados de siete familias se contrastaron con cálculos Python sobre tablas fuente. No sustituye revisión humana ni cubre los 2,400 pares completos.
- Evidencia: `resultados/reporte_datos.json`, `resultados/ejecucion_entrenamiento.jsonl`, `resultados/revision_semantica.json`, `tests/test_integridad_datos.py` y `notebooks/01_datos.ipynb`. Los reportes guardan tiempos técnicos; no representan horas de trabajo de los integrantes.
- Limitación: los diez dominios de entrenamiento comparten topología y treinta familias de consultas. Pendiente revisar diversidad y redactar/certificar cuarenta preguntas propias antes del relevo a Angel.
- Tiempo humano: pendiente de registrar por los integrantes. Estado: cambios locales sin commit; no se ha iniciado el turno 2.

## 2026-10-22 — Incorporación de preguntas propias recibidas

- Autor del registro e integración: asistente de IA durante el turno de Jorge Lopez. Jorge envió cuarenta preguntas y declaró los autores por grupo: Jorge 1–10 y 21–30, Angel 11–20 y 31–40. No se verificó esa autoría por otra fuente.
- Se conservaron las cuarenta preguntas originales y se prepararon con IA las referencias SQL, columnas, pesos y precisiones semánticas. Jorge aprobó usar únicamente el campo nombre existente en hospital; el resto de los ajustes está documentado para revisión.
- Criterios propuestos: libro como título, promedios incluyendo ceros, estado atendida para consultas realizadas y desempates explícitos. Las preguntas 8, 23, 28 y 32 pasan a medias. Distribución: 14 fáciles, 16 medias, 10 difíciles; suma de pesos 76.
- Resultado: 40/40 consultas ejecutables en MySQL 8.4.10 con ONLY_FULL_GROUP_BY, sin descartes. Las preguntas 24 y 26 producen resultados vacíos con las semillas actuales; se recomienda incorporar casos positivos antes de evaluar el modelo. No se modificaron las semillas ni esquemas.
- Evidencia: `datos/validacion/preguntas_propias.jsonl`, `datos/validacion/PREGUNTAS_PARA_REVISION.md`, `datos/validacion/pares.jsonl`, `datos/validacion/referencias_resultados.jsonl` y `resultados/reporte_datos.json`. El cierre técnico no equivale a aprobación humana ni resuelve la diversidad limitada del entrenamiento.
- Tiempo humano: pendiente de registrar por los integrantes. Cambios locales, sin commits ni subidas; plan fijo intacto.

## 2026-10-22 — Revisión encargada por Jorge y fortalecimiento de datos

- Autor del registro y ejecución: asistente de IA, por solicitud explícita de Jorge Lopez de completar la revisión de su primer turno. No se declara que Jorge haya ejecutado una revisión humana equivalente.
- Trabajo: agregar academia, logística, turismo, energía y manufactura, con 200 pares por dominio. Total: 3,400 candidatos, quince esquemas y 66 familias. La comparación de grafos de FK sin nombres confirma seis topologías distintas.
- Validación: agregar fechas límite, empates, nombres repetidos y positivos/negativos para las preguntas 24 y 26; conservar texto original, autores y reparto de las cuarenta preguntas. No cambió el plan fijo ni se usaron esquemas reservados para generar entrenamiento.
- Limpieza: retirar los borradores IA y sus resultados ya reemplazados; simplificar el generador reservado para que solo regenere DDL/semillas. Renombrar la vista legible a `datos/validacion/PREGUNTAS.md`. Conservar candidatos, aceptados y evidencia porque cumplen funciones diferentes.
- Evidencia: `scripts/dominios_diversos.py`, `scripts/preparar_validacion.py`, `scripts/auditar_datos.py`, `datos/particiones.json` y `tests/`. Tiempo humano no estimado ni imputado.

## 2026-10-22 — Cierre técnico y relevo preparado

- Autor del registro y ejecución: asistente de IA durante el turno de Jorge, a solicitud suya.
- Certificación: 3,400 pares de entrenamiento y cuarenta de validación ejecutables en MySQL 8.4.10 con ONLY_FULL_GROUP_BY; cero descartes. Hay 209 resultados vacíos en entrenamiento y ninguno en las referencias propias.
- Revisión: se reemplazó la muestra de setenta casos por el contraste de todos los 3,440 resultados mediante algoritmos Python sobre tablas fuente. Se conservan duplicados, ceros, desempates y orden cuando se exige. No se atribuye rendimiento del modelo ni revisión humana.
- Auditoría: exige hashes y evidencia de todas las fuentes/resultados, evita cierres sin revisión semántica y detecta consultas que nombran esquemas externos. Once pruebas verifican integridad, pérdida de duplicados, cambios de evidencia y diversidad estructural.
- Documentación: README, datos, notebook y `RELEVO_ANGEL.md` describen el estado actual, reproducción y próximo turno. La privacidad y el acceso del docente no se dan por verificados por pruebas locales.
- Estado: primer turno listo técnicamente para revisión del resultado por Jorge y posterior autorización de commits/subida. Sin commits ni subidas de implementación. Tiempo humano no inventado; deben registrarlo los integrantes si quieren contabilizarlo.

## 2026-10-22 — Publicación autorizada del primer turno

- Autor del registro y ejecución: asistente de IA por instrucción de Jorge Lopez. Jorge aprobó publicar los tres commits propuestos mediante el mensaje «subelo». Se usa su identidad Git configurada; no se atribuyen commits a Angel.
- Antes de publicar se comprobó la auditoría de cierre: 3,400 pares, quince esquemas, seis topologías y cuarenta preguntas propias, con evidencia vigente. `.env`, `.venv/` y cachés están excluidos.
- División aprobada: entorno MySQL y dependencias; datos de entrenamiento validados; validación propia, pruebas, notebook y cierre documental. Los hashes y la subida se comprueban en el historial y en origin/main.
- La publicación de código no confirma por sí misma acceso del docente o de Angel, ni ejecución del modelo en T4. Esas comprobaciones corresponden al relevo y siguientes turnos. No se imputan horas humanas no registradas.

## 2026-10-22 — Turno 2: contrato de inferencia y evaluador ponderado

- Autor del registro y ejecución: asistente de IA durante el turno de Angel Herrarte, a su solicitud. Revisión de Angel: pendiente.
- Trabajo: crear `config.json` con `usar_adapter: false` hasta que exista el adapter, y `solucion.py`. Este carga una sola vez al importar, usa un prompt congelado v1 compartido por base, adapter y entrenamiento, y genera en modo greedy, reemplazando el `generation_config.json` de Qwen que trae muestreo. Extrae una sola consulta y aplica un filtro de solo lectura con respaldo `SELECT 1`. La estrategia es directa, sin llamadas a `ejecutar`.
- Evaluador: `evaluacion/comparar.py` y `evaluacion/evaluar.py` quedan fuera de `scripts/` para no alterar los hashes auditados del turno 1. Reglas: redondeo a 2 decimales, multiconjuntos con duplicados, orden solo cuando se exige y columnas alineadas por valores, con columnas adicionales permitidas. El callback de solo lectura admite 3 llamadas y devuelve 10 filas.
- Resultado: el oráculo con las referencias como predicción da EX = 1.0 (76/76), y las 40 referencias reejecutadas coinciden con la evidencia del turno 1. Hay 46 pruebas aprobadas, 35 de ellas nuevas, incluidos controles negativos contra MySQL: DISTINCT que pierde duplicados, orden alterado y errores 1054/1064. `scripts.auditar_datos --exigir-cierre` sigue aprobando.
- Prueba de humo local, no oficial: en macOS con MPS el modelo base cargó en unos 5–8 s y respondió en 0.5–2.5 s por pregunta, con salidas idénticas con y sin callback. Esa corrida parcial se eliminó; el baseline oficial se medirá en Colab T4.
- Licencia del modelo base: Apache-2.0. Se fijaron transformers 5.20.2, peft 0.21.2 y accelerate 1.15.0; torch se toma de Colab (≥ 2.6).
- Evidencia: `solucion.py`, `config.json`, `evaluacion/`, `tests/test_solucion.py`, `tests/test_evaluador.py`, `tests/test_evaluador_mysql.py` y `resultados/evaluaciones/oraculo/`.
- Pendiente: baseline completo en T4 y congelación de la configuración experimental (commit 2); hipótesis y entrenamiento de LoRA A (commit 3). Tiempo humano no registrado; Angel lo completará.
