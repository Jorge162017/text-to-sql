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

- Autor del registro y ejecución: asistente de IA durante el turno de Angel Herrarte, a su solicitud. Revisada por Angel el 25 de octubre de 2026.
- Trabajo: crear `config.json` con `usar_adapter: false` hasta que exista el adapter, y `solucion.py`. Este carga una sola vez al importar, usa un prompt congelado v1 compartido por base, adapter y entrenamiento, y genera en modo greedy, reemplazando el `generation_config.json` de Qwen que trae muestreo. Extrae una sola consulta y aplica un filtro de solo lectura con respaldo `SELECT 1`. La estrategia es directa, sin llamadas a `ejecutar`.
- Evaluador: `evaluacion/comparar.py` y `evaluacion/evaluar.py` quedan fuera de `scripts/` para no alterar los hashes auditados del turno 1. Reglas: redondeo a 2 decimales, multiconjuntos con duplicados, orden solo cuando se exige y columnas alineadas por valores, con columnas adicionales permitidas. El callback de solo lectura admite 3 llamadas y devuelve 10 filas.
- Resultado: el oráculo con las referencias como predicción da EX = 1.0 (76/76), y las 40 referencias reejecutadas coinciden con la evidencia del turno 1. Hay 46 pruebas aprobadas, 35 de ellas nuevas, incluidos controles negativos contra MySQL: DISTINCT que pierde duplicados, orden alterado y errores 1054/1064. `scripts.auditar_datos --exigir-cierre` sigue aprobando.
- Prueba de humo local, no oficial: en macOS con MPS el modelo base cargó en unos 5–8 s y respondió en 0.5–2.5 s por pregunta, con salidas idénticas con y sin callback. Esa corrida parcial se eliminó; el baseline oficial se medirá en Colab T4.
- Licencia del modelo base: Apache-2.0. Se fijaron transformers 5.20.2, peft 0.21.2 y accelerate 1.15.0; torch se toma de Colab (≥ 2.6).
- Evidencia: `solucion.py`, `config.json`, `evaluacion/`, `tests/test_solucion.py`, `tests/test_evaluador.py`, `tests/test_evaluador_mysql.py` y `resultados/evaluaciones/oraculo/`.
- Pendiente: baseline completo en T4 y congelación de la configuración experimental (commit 2); hipótesis y entrenamiento de LoRA A (commit 3). Tiempo humano no registrado; Angel lo completará.

## 2026-10-22 — Turno 2: baseline sin adapter en Colab T4

- Ejecución: Angel Herrarte corrió `notebooks/02_evaluacion_t4.ipynb` en Google Colab con Tesla T4, según indicó. Resultado de la corrida en UTC: 2026-10-23 00:10. La integración y el análisis los hizo el asistente de IA a su solicitud.
- Entorno: Python 3.13.15, torch 2.11.0+cu130 (el de Colab), transformers 5.20.2 y peft 0.21.2. MySQL 8.4.10 instalado desde el binario oficial con `sql_mode` predeterminado, que incluye ONLY_FULL_GROUP_BY. Modelo `Qwen/Qwen2.5-Coder-1.5B-Instruct`, revisión `2e1fd397ee46e1388853d2af2c993145b0f1098a`, código del commit `72fd3cc`.
- Oráculo en T4: EX = 1.0 (76/76). Las referencias reejecutadas coinciden con la evidencia del turno 1.
- **Baseline sin adapter: EX = 0.5658 (43/76).** Fáciles 14/14 (peso 14/14); medias 10/16 (peso 20/32, EX 0.625); difíciles 3/10 (peso 9/30, EX 0.30). Biblioteca 0.5676 y hospital 0.5641.
- Categorías automáticas: 27 correctas, 5 resultados distintos, 3 columnas o tablas inexistentes, 3 de agregación (ONLY_FULL_GROUP_BY) y 2 errores de ejecución (LIMIT dentro de IN; referencia a una función de grupo).
- Patrones observados: `COUNT(*)` con LEFT JOIN, que cuenta 1 en lugar de 0 (15, 25); INNER JOIN donde se pedían ceros (28, 35); "primero/último por grupo" con GROUP BY en lugar de funciones de ventana (10, 20, 30, 40); columnas inventadas (7, 23); filtros añadidos sin pedirse (18, 40).
- Límites: carga de 47.9 s con descarga del modelo y 12.9 s con caché, frente a un máximo de 5 min. Latencia media de 1.9 s y máxima de 4.9 s, frente a 30 s. Cero llamadas a `ejecutar`.
- Determinismo: una segunda corrida en otro proceso dio 40/40 SQL idénticos (`baseline_repeticion/determinismo.json`).
- `cambios_sin_commit: true` en baseline y repetición se debe a los archivos de resultados que el oráculo generó antes en el mismo checkout de Colab; el oráculo, ejecutado primero, registra `false` en el mismo commit. Los hashes de `resultados/configuracion_experimental.json` coinciden con `solucion.py`, el evaluador y los datos actuales.
- Configuración congelada para A/B: prompt v1 (sha256 `1fb4d982…`), generación greedy con 320 tokens, semilla 2026 y el criterio de evaluación descrito en el README.
- Evidencia: `resultados/evaluaciones/oraculo_t4/`, `baseline/` y `baseline_repeticion/`.
- Pendiente: escribir la hipótesis A **antes** de entrenar, entrenar LoRA A en T4 y evaluarla con el mismo prompt. Tiempo humano no registrado; Angel lo completará.

## 2026-10-22 — Turno 2: hipótesis y configuración de LoRA A (antes de entrenar)

- Autor del registro y preparación: asistente de IA durante el turno de Angel Herrarte, a su solicitud. Revisada por Angel el 25 de octubre de 2026. Esta entrada y `entrenamiento/lora_a.json` se publican **antes** de iniciar el entrenamiento; la fecha del commit sirve como evidencia.
- **Hipótesis A:** con LoRA r=8 sobre todos los módulos lineales de atención y MLP, una época sobre los pares sintéticos y el mismo prompt v1, el modelo aprenderá patrones de MySQL que el baseline falla: LEFT JOIN con COUNT(columna) para conservar ceros, ROW_NUMBER() para el primero o último por grupo, GROUP BY compatible con ONLY_FULL_GROUP_BY y uso exclusivo de columnas del esquema. **Predicción:** la EX de la validación propia sube de 0.5658 (43/76) a al menos 0.72 (mejora de 0.15 o más), sobre todo en medias (20/32) y difíciles (9/30), con las fáciles en 14/14 y la latencia por debajo de 5 s. **Riesgo:** sobreajuste a la redacción y los alias de las plantillas; si baja la EX de fáciles o aparecen columnas inventadas nuevas, se interpretará como pérdida de generalización.
- **Configuración común para A/B** (`entrenamiento/lora_a.json`):
  - LoRA: `lora_alpha=16`, `lora_dropout=0.05`, `bias=none`, módulos `q,k,v,o,gate,up,down_proj`.
  - Entrenamiento: 1 época, AdamW (`adamw_torch`) con LR 2e-4 coseno y 10 pasos de calentamiento, `weight_decay=0`, `max_grad_norm=1.0`. Batch 2 × acumulación 8, equivalente a 16.
  - Precisión y memoria: fp16 con el modelo base en fp16 y los pesos LoRA en fp32; gradient checkpointing activado; `max_longitud=1024` sin truncar.
  - Semilla 2026 (también `data_seed`).
  - Datos: 3,400 pares, de los que se apartan 150 para dev (10 por esquema, estratificado) y quedan 3,250 para entrenar. La pérdida se calcula solo sobre el SQL y `<|im_end|>`.
  - Prompt: el mismo `construir_mensajes` de `solucion.py`.
  - La B debe copiar este archivo y cambiar **solo** `lora.r` (de 8 a 16). `tests/test_entrenamiento.py` comprueba esa regla. Consecuencia del cambio: con `lora_alpha` fijo, la escala alpha/r pasa de 2.0 a 1.0.
- Mediciones previas locales, no oficiales: los ejemplos ocupan como máximo 868 tokens (mediana 805), unos 2.7 M tokens por época. Una prueba de 2 pasos en macOS (MPS, fp32) registró **9,232,384 parámetros entrenables (0.59 %)** y una pérdida dev inicial de alrededor de 0.39. El adapter resultante (37 MB) cargó y se fusionó por `solucion.cargar`.
- Estimación en T4: unos 203 pasos de optimización, 45–75 min. Se ejecutará con `notebooks/03_entrenamiento_t4.ipynb`, que entrena, evalúa con `--adapter si`, repite la evaluación para comprobar determinismo y compara con el baseline.
- Tiempo humano no registrado; Angel lo completará.

## 2026-10-22 — Turno 2: primer intento de LoRA A fallido por torchao en Colab

- Ejecución en Colab T4 por Angel Herrarte; diagnóstico y corrección por el asistente de IA a su solicitud.
- Fallo: al crear la LoRA, peft 0.21.2 lanzó `ImportError: Found an incompatible version of torchao. Found version 0.10.0, but only versions above 0.16.0 are supported`. Colab trae torchao 0.10 preinstalado y peft ≥ 0.19 exige ≥ 0.16 siempre que lo encuentra, aunque no se use. No se entrenó ningún paso, no se generó adapter y la configuración e hipótesis A no cambian.
- Impacto en la entrega: el mismo error habría ocurrido en la evaluación del docente al cargar el adapter, porque instala `requirements.txt` sobre el mismo Colab.
- Corrección: fijar `peft==0.18.1`, que acepta torchao ≥ 0.4. Se reprodujo localmente con torchao 0.10.0: con peft 0.21.2 se obtiene el mismo ImportError; con 0.18.1 el entrenamiento de prueba da la misma pérdida dev (0.377387) y `solucion.cargar` carga y fusiona el adapter. Las 53 pruebas aprueban. El baseline no usa peft, así que su medición sigue siendo válida.
- Siguiente paso: reiniciar el entorno de Colab y volver a ejecutar `notebooks/03_entrenamiento_t4.ipynb` con el commit corregido.

## 2026-10-22 — Turno 2: LoRA A entrenada y evaluada en Colab T4

- Ejecución: Angel Herrarte corrió `notebooks/03_entrenamiento_t4.ipynb` en Colab con Tesla T4 sobre el commit `bc2206d`. El entrenamiento terminó el 2026-10-23 a las 01:48 UTC. La integración y el análisis los hizo el asistente de IA a su solicitud.
- Entorno: Python 3.13.15, torch 2.11.0+cu130, transformers 5.20.2, peft 0.18.1 y modelo con revisión `2e1fd397…`. La configuración `entrenamiento/lora_a.json` no cambió respecto del commit `26b9ab2` (sha256 `3bc9e141…`).
- Entrenamiento: 202 pasos en una época, sin reanudar. **Duró 2,782 s (46.4 min)**, a 1.16 muestras/s, con memoria pico de 6.15 GiB. **9,232,384 parámetros entrenables (0.5945 % de 1,552,946,688).** Pérdida dev: 0.438 al inicio, 0.0258 en el paso 40, 0.0066 en el 80, 0.0020 en el 120 y 0.0006 al final. Pérdida de entrenamiento promedio 0.0348, sin NaN. Curvas en `resultados/entrenamientos/lora_a/curvas_loss.png`.
- **Corrección de la entrada previa:** el dev tiene **170** pares y el entrenamiento **3,230**, no 150 y 3,250. Con `fraccion_dev=0.05` salen 12 por cada esquema comercial (240 pares) y 10 por cada esquema diverso (200 pares). La configuración no cambió; el error estaba solo en mi descripción.
- **Evaluación con el mismo prompt v1: EX = 0.6974 (53/76)**, frente a 0.5658 del baseline: **+0.1316**. Fáciles 14/14 (igual), medias 12/16 con peso 24/32 (+4) y difíciles 5/10 con peso 15/30 (+6). La repetición en otro proceso dio 40/40 SQL idénticos. Carga de 30.5 s; latencia media de 1.70 s y máxima de 5.61 s; cero llamadas a `ejecutar`.
- Respecto del baseline, ganó 9, 15, 25, 28 y 40, todas por conteos con ceros y ROW_NUMBER, y perdió 17. Fallan 7, 10, 17, 18, 20, 23, 29, 30 y 35. Por categoría: 5 resultados distintos, 3 columnas inexistentes y 1 de agregación.
- **Veredicto de la hipótesis A: no se cumple la predicción cuantitativa.** Se predijo una EX de al menos 0.72 (mejora de 0.15 o más) y se obtuvo 0.6974 (+0.1316); faltaron 2 puntos de peso. Se confirma la dirección: mejoran medias y difíciles, se mantienen las fáciles y la latencia media queda por debajo de 5 s, aunque la máxima llegó a 5.6 s. Aprendió LEFT JOIN con COUNT(columna) y ROW_NUMBER().
- **El riesgo declarado sí apareció.** La pérdida dev casi nula refleja que memorizó las plantillas sintéticas. El modelo omite la tabla intermedia `ejemplares` y une `prestamos.ejemplar_id` con `titulos.id` (7, 17, 18), aplica ROW_NUMBER sobre tablas equivocadas (20, 30) y omite el ordenamiento por grupo (10). Esto apunta a la poca diversidad estructural de los datos, no a un fallo del contrato.
- Integración: `adapter/` (37 MB) queda como adapter vigente y `config.json` pasa a `usar_adapter: true`. Con esa configuración por defecto, `import solucion` carga y fusiona el adapter en local. Pasan las 53 pruebas.
- Evidencia: `adapter/`, `resultados/entrenamientos/lora_a/` y `resultados/evaluaciones/lora_a/` y `lora_a_repeticion/`.
- Tiempo humano no registrado; Angel lo completará.

## 2026-10-22 — Cierre del turno 2 y relevo a Jorge

- Autor del registro: asistente de IA durante el turno de Angel Herrarte, a su solicitud. Revisada por Angel el 25 de octubre de 2026.
- Entregables del turno: contrato e inferencia (`6fb3547`), notebook T4 y configuración congelada (`72fd3cc`), baseline con EX 0.5658 (`18bb488`), hipótesis A previa (`26b9ab2`), corrección de dependencias (`bc2206d`) y LoRA A con EX 0.6974 en el commit de cierre.
- Relevo completo en `RELEVO_JORGE.md`: hiperparámetros exactos, prompt congelado, regla de un solo factor, presupuesto de la corrida B y comandos.

## 2026-10-23 — Correcciones locales previas al turno 3

- Autor del registro y ejecución: asistente de IA por solicitud de Jorge Lopez. Sin commits ni subidas de estas correcciones.
- Limpieza: conservar párrafos SQL válidos, CTE, comentarios y literales con líneas vacías; retirar solo prosa reconocible a nivel superior. Pruebas de regresión y MySQL comprueban resultados equivalentes.
- Reproducibilidad: tokenizer y modelo comparten cargadores con el commit de Hugging Face registrado por baseline y A. No cambian el prompt ni la configuración de entrenamiento A; no se reentrenó el adapter.
- Evidencia: conservar congelado histórico de Angel y crear congelado vigente con limpieza v2. Comprobar todos los hashes/configuración al evaluar, en lugar de comparar solo el texto del prompt.
- Preparación: notebook 04 para repetir en T4 baseline/A y determinismo en carpetas nuevas. Esta ejecución en GPU está pendiente; no se inventan nuevas métricas ni se equipara reejecutar SQL guardado con regenerar respuestas del modelo.
- No se han comenzado LoRA B ni el experimento de inferencia. No se imputan horas humanas no registradas.

- Verificación local de las correcciones: suite de 58 pruebas OK con acceso a MySQL; el grupo de tokenización se omite porque transformers/tokenizer no está instalado en este entorno. Cargadores comprobados con dobles de prueba que exigen la revisión exacta de A. Control de referencias en MySQL: 76/76, guardado por separado en `oraculo_correcciones/`. Notebook 04 validado en formato y sintaxis, sin ejecutar GPU.

## 2026-10-23 — Publicación autorizada de correcciones previas a B

- Autor del registro y ejecución: asistente de IA por instrucción de Jorge Lopez de subir las correcciones antes de ejecutar Colab. Publicación desde su identidad Git configurada.
- Incluye limpieza SQL v2, revisión fija del modelo/tokenizer, validación completa del congelado, regresiones y notebook 04. Se comprobó que el congelado está vigente y el control local de MySQL permanece en 76/76. No se modifican las evaluaciones históricas ni el adapter A.
- Pendiente: ejecutar notebook 04 en Colab T4 para regenerar baseline/A y sus repeticiones. Publicar el código no equivale a completar esa evaluación.

## 2026-10-23 — Recepción y verificación de las corridas corregidas de T4

- Autor del registro e integración: asistente de IA durante el turno de Jorge. Jorge entregó `verificacion_correcciones_t4.zip`, con la ejecución del notebook 04 entre las 09:09 y 09:17 de Guatemala según los registros UTC adjuntos. Ese intervalo corresponde a las evaluaciones, no a horas de trabajo humano imputadas.
- Se verificaron las trece entradas del ZIP antes de integrar: rutas esperadas, sin duplicados ni enlaces simbólicos; configuración byte a byte igual a la publicada, hashes, snapshot, limpieza v2, MySQL 8.4.10 y GPU T4. El congelado local se conservó y solo se incorporaron doce archivos nuevos de evaluaciones.
- Baseline corregido: EX 0.5658 (43/76); A corregido: EX 0.6974 (53/76), mejora 0.1316. Oráculo: 76/76. Ambas repeticiones verifican 40/40 SQL y aciertos idénticos. Las cargas y latencias registradas respetan los límites.
- Se reejecutaron las 200 consultas guardadas de las cinco corridas en MySQL local con lector temporal SELECT y transacciones READ ONLY. Los aciertos coinciden sin discrepancias. Esta reejecución verifica la evidencia entregada, no se presenta como otra generación en GPU.
- Evidencia: `resultados/evaluaciones/oraculo_corregido/`, `baseline_corregido/`, `baseline_corregido_repeticion/`, `lora_a_corregido/`, `lora_a_corregido_repeticion/` e informe `resultados/verificacion_correcciones_t4.json` con hash del ZIP y archivos integrados. Los indicadores de checkout modificado en las corridas se conservan; el congelado acredita los hashes de los archivos experimentales.
- Estado: verificación previa a B completa; no se han iniciado entrenamiento B ni experimento de inferencia. Integración local sin commits ni subidas.


## Turno 3 — preparación de LoRA B (23 de octubre de 2026)

Responsable: Jorge Lopez, con asistencia de IA. Se prepararon `entrenamiento/lora_b.json` y `notebooks/05_lora_b_t4.ipynb`; todavía no se ha entrenado B ni medido su resultado. Tiempo activo humano: pendiente de registrar por Jorge.

**Hipótesis previa B:** cambiar únicamente `r=8` a `r=16` podría mejorar consultas complejas. Se predice al menos 56/76 (EX 0.7368), frente a 53/76 de A corregido, conservando 14/14 fáciles y los límites de 300 s de carga y 30 s por pregunta. Se mantienen alpha=16, datos, división, semilla, prompt y todos los demás hiperparámetros. Consecuencias derivadas: parámetros entrenables esperados de 9,232,384 a 18,464,768; escala alpha/r de 2 a 1. Mayor capacidad también puede aumentar memorización; se seleccionará con EX, latencia y memoria medidas, no solo pérdida dev.

El notebook exige hipótesis registrada en Git, T4, congelado vigente y la misma división dev de A; guarda B en otra carpeta, evalúa dos veces con el evaluador congelado, restaura A y descarga `lora_b_t4.zip`. El README del adapter A cambió después de entrenarlo; sus pesos y configuración sí coinciden con los hashes de entrenamiento. Se preserva también el README recibido al restaurar A.

Comprobación local: cinco pruebas de preparación de entrenamiento aprobadas; tokenización pendiente de Colab porque transformers no está instalado localmente. Notebook validado y celdas compiladas sin ejecutar GPU. Pendiente: publicar hipótesis antes de entrenar, ejecutar notebook en T4, verificar ZIP, seleccionar adapter y realizar experimento de inferencia. No se modifica el plan fijo ni se afirma que el turno 3 esté cerrado.


## Turno 3 — LoRA B medida y selección de A (23 de octubre de 2026)

Responsable: Jorge Lopez, con asistencia de IA para preparar el notebook, revisar e integrar el ZIP. Evidencia recibida: `lora_b_t4.zip`, ejecución T4 terminada a las 18:12 UTC (12:12 Guatemala). Tiempo de entrenamiento registrado: 2756.3 s; tiempo activo humano pendiente de registrar por Jorge.

B completa 202 pasos con 3,230 ejemplos train y 170 dev, división y datos idénticos a A, revisión fija y solo r=16 como cambio de hiperparámetro. Parámetros entrenables: 18,464,768; memoria pico: 6.28 GiB; loss dev final: 0.0005404348485171795. EX: 49/76 (0.6447), 30/40 aciertos; repetición idéntica en 40/40 SQL y aciertos. Carga 32.35 s y latencia máxima 4.024 s (repetición: 28.04 s y 3.991 s). Hipótesis de 56/76 rechazada; no se elimina B. Python pasó de 3.13.15 en la evaluación A corregida a 3.13.16 en B; torch, transformers y peft reportan las mismas versiones. Esta diferencia de entorno queda registrada como limitación.

Se selecciona **A**: 53/76 (0.6974), frente a 49/76 de B, y menor memoria de entrenamiento (6.15 frente a 6.28 GiB). B tardó aproximadamente 45.9 min, frente a 46.4 min de A; no se atribuye causalmente esta pequeña variación al rango. La menor loss dev de B no mejora EX. `adapter/` sigue conteniendo A original; B se conserva en `adapters/lora_b/`.

Validación: 14 entradas del ZIP controladas, hashes de los archivos del adapter y configuración comprobados, congelado idéntico y métricas recalculadas desde las predicciones. Se reejecutaron las 80 consultas de B/repetición con un usuario temporal SELECT en MySQL 8.4.10: todos los aciertos y códigos coinciden. Informe: `resultados/verificacion_lora_b_t4.json`. Pendiente del turno 3: experimento controlado de inferencia sobre A, decisión de estrategia y relevo. No se han publicado estos resultados todavía.


## Turno 3 — preparación del experimento de inferencia (23 de octubre de 2026)

Responsable: Jorge Lopez, asistido por IA. Tiempo humano pendiente de registrar. **Hipótesis antes de medir:** reenviar al mismo modelo los errores de ejecución MySQL podría recuperar al menos una pregunta de A y aumentar EX; no se espera resolver automáticamente errores semánticos de consultas ejecutables. Control: directa; tratamiento: corrección de errores. Primer prompt, primera generación, pesos A, datos, semilla y reglas de puntuación iguales. No hay ejemplos de validación ni referencias en el feedback.

Se implementa `evaluacion/correccion.py`: hasta 3 callbacks, hasta 2 reparaciones, sin callback conserva exactamente directa. No usa filas para inferir corrección semántica. Presupuesto interno 29 s, reserva 10.5 s por callback (timeout MySQL del arnés: 10 s), reparaciones entre 2 y 8 s según tiempo restante. max_time de Transformers se revisa entre pasos, por lo que no garantiza un corte duro; la admisión depende de los tiempos reales T4. Ante error de callback, falta de tiempo, repetición o respuesta no válida, devuelve la última consulta de lectura disponible. El contrato de entrega sigue en directa hasta evaluar.

El evaluador incorpora `--estrategia directa|correccion`, guarda trazas y elimina la segunda generación diagnóstica fuera del cronómetro cuando la respuesta era SELECT 1. Se preservó byte a byte el congelado A/B en `resultados/configuracion_experimental_ab.json`; el vigente incluye los hashes del nuevo evaluador y módulo de corrección. No se reetiquetan mediciones históricas: el notebook 06 repite base/A × directa/corrección × dos corridas y un oráculo (360 preguntas en total) con el nuevo congelado. Se elegiría corrección solo si mejora EX de A, cumple los límites y es determinista en las corridas; en empate se conserva directa. La selección provisional no modifica el contrato automáticamente.

Verificación local: 65 pruebas aprobadas, con una clase de tokenización omitida por faltar transformers local; incluye MySQL y siete pruebas de la política de corrección. Notebook 06 validado y celdas compiladas. No se ha ejecutado el experimento en GPU. Pendientes: publicación, ejecución T4, auditoría de `inferencia_t4.zip`, integración de la estrategia elegida y relevo.


## Turno 3 — experimento T4 verificado y cierre técnico (23 de octubre de 2026)

Responsable: Jorge Lopez, con asistencia de IA para auditoría e integración. Tiempo activo humano pendiente de registrar por Jorge. Se recibió `inferencia_t4.zip` con 24 entradas; el congelado coincide byte a byte con el publicado y se integraron 23 archivos nuevos sin reemplazar históricos. Nueve corridas de 40 preguntas: 360 predicciones comprobadas y reejecutadas con SELECT en MySQL local, con aciertos y códigos MySQL idénticos a los reportados. Las cuatro repeticiones tienen 40/40 SQL y aciertos idénticos; ningún exceso de 30 s, 300 s de carga o tres callbacks.

Resultados: base directa 43/76; base corrección 48/76; A directa 53/76; A corrección 53/76. La corrección recupera dos preguntas del base (`propia_10`, `propia_23`) sin perder aciertos. En A modifica SQL de `propia_20` y `propia_30` pero no recupera ni pierde aciertos. La hipótesis de recuperar al menos una pregunta de A no se cumple. A directa: media 1.648 s, máxima 5.463 s; A corrección: media 1.979 s, máxima 11.467 s, 42 callbacks, máximo dos por pregunta. En la repetición A corrección máxima 11.216 s. El tratamiento cumple límites pero no mejora EX: se selecciona **A + directa**, aplicando la regla previa de empate. El contrato ya usa directa, por lo que no se modifica `solucion.py` ni se invalidan sus mediciones.

Selección final: `resultados/seleccion_final_turno3.json`; auditoría: `resultados/verificacion_inferencia_t4.json`; relevo: `RELEVO_ANGEL_TURNO4.md`. `adapter/` conserva A; se conservan B y todas las corridas negativas. La mejora final comparable frente al base directo es 10/76 = 0.1316. No se confunde con comparar A directa frente a base con corrección. El cierre técnico del turno 3 está completo; faltan publicación de esta evidencia y registro humano de horas reales. El turno 4 corresponde a Angel: auditoría limpia final, CSV, análisis de errores, predicción oculta, presentación y entrega.


## Jornada de Jorge y revisión editorial de notebooks — 23 de octubre de 2026

Jorge Lopez: trabajo durante gran parte del día 23 de octubre en ejecución de Colab, revisión de resultados y cierre del turno 3; duración aproximada, con pausas y esperas de GPU. Descripción confirmada por Jorge, sin convertirla en un número de horas exacto. Los tiempos de entrenamiento GPU se conservan por separado en las métricas y no equivalen a tiempo activo humano.

A solicitud de Jorge, se retiraron de los seis notebooks los comentarios conversacionales de soporte y las indicaciones de compartir errores o ZIP, publicar cambios y seguir pasos de la conversación. Las descripciones técnicas, hipótesis, criterios de comparación, código y resultados experimentales se conservan. La revisión editorial se mantiene local, pendiente de publicación.

## Turno 4 — auditoría final de la entrega en Colab T4 limpio (25 de octubre de 2026)

Responsable: Angel Herrarte (ejecución en Colab), con asistencia de IA para preparar el notebook, auditar el ZIP e integrar. Tiempo activo humano: ver el registro de horas al cierre del turno 4. Notebook `notebooks/07_auditoria_final_t4.ipynb`, publicado en `5df3e5d` antes de ejecutar; sesión limpia con Tesla T4, Python 3.13.16, torch 2.11.0+cu130, transformers 5.20.2, peft 0.18.1, instalando solo `requirements.txt`. No se entrenó ni se cambió prompt, generación, adapter ni contrato.

Resultados: integridad del congelado, revisión del modelo, pesos y configuración de A (r=8) correctos; sin esquemas, preguntas ni SQL de validación en entrenamiento; 59 pruebas aprobadas (2 omitidas). Contrato en proceso nuevo, sin carga diferida: `import solucion` con A en 52.94 s; seis preguntas (una por esquema y nivel) con salida idéntica sin callback, con `ejecutar=None` y con callback, 0 llamadas, máximo 2.58 s; esquema vacío, pregunta vacía y petición de borrado devuelven una consulta de lectura sin excepción (la de borrado, `SELECT 1`). Oráculo 76/76. Base 43/76 y A 53/76, ambas con repetición 40/40 idéntica; carga máxima 25.24 s, latencia máxima 5.331 s, 0 callbacks, todas las consultas de lectura. El SQL coincide 40/40 con `inferencia_base_directa` e `inferencia_a_directa` del turno 3.

Verificación local: las 200 predicciones del ZIP se reejecutaron en MySQL 8.4.10 (Docker) y las métricas se recalcularon desde las predicciones: aciertos, categorías y códigos idénticos. No es nueva generación GPU. Evidencia: `resultados/auditoria_final_t4.json`, `resultados/auditoria_final/`, `resultados/evaluaciones/auditoria_final_*` y `resultados/verificacion_auditoria_final_t4.json`. No se encontraron fallos de integración; no hubo que repetir mediciones. Pendientes del turno 4: CSV de validación, análisis de errores, predicción de EX oculto, presentación, documentación y entrega.

## Turno 4 — validación consolidada y análisis de errores (25 de octubre de 2026)

Responsable: Angel Herrarte, con asistencia de IA para la consolidación y la primera clasificación; clasificación revisada por Angel. Tiempo activo humano: ver el registro de horas al cierre del turno 4. `python -m evaluacion.consolidar` genera `resultados/validacion_propia.csv` (200 filas: base, A, B, base con corrección y A con corrección × 40) y `resultados/analisis_errores.json`, a partir de las predicciones guardadas y de la clasificación manual `resultados/clasificacion_errores.json`. Base y A usan la auditoría final; B y las variantes con corrección, las corridas del turno 3. La regla está documentada: si hay error de ejecución manda el código MySQL; si la consulta se ejecuta, la prioridad es JOIN > agregación > filtro > resultado distinto. Los pesos se comprueban contra cada `resumen.json` (`tests/test_consolidar.py`; 70 pruebas aprobadas).

Hallazgos (`resultados/ANALISIS_ERRORES.md`): A falla 9 preguntas (23 de 76 puntos): 4 de JOIN, 3 de columna/tabla inexistente y 2 de agregación. El base falla 13 (33 puntos), sobre todo de agregación (6). El fine-tuning corrige `COUNT(*)` con `LEFT JOIN` y `GROUP BY` incompatibles con `ONLY_FULL_GROUP_BY`; el error dominante que queda son las relaciones indirectas (préstamo → ejemplar → título) y las columnas inventadas en lugar de un JOIN. La corrección con callback solo recupera errores de ejecución del base, no los semánticos de A. Pendientes: predicción de EX oculto, presentación, documentación y entrega.

Predicción de EX oculto (`resultados/PREDICCION_EX_OCULTO.md`): estimación, no medición. Para A: 0.60, con rango de 0.50 a 0.68; para el base, 0.48; mejora esperada de unos +0.12. Parte del 0.6974 medido (bootstrap del 95 %: 0.54–0.86) y se ajusta por la composición por dificultad, los nombres en inglés o abreviados del enunciado, los esquemas de 5 a 10 tablas, la poca cobertura de fechas en la validación y la redacción más explícita de nuestras preguntas. No se usó el conjunto reservado para ajustar nada.

## Turno 4 — presentación, documentación y cierre (25 de octubre de 2026)

Responsable: Angel Herrarte, con asistencia de IA (Claude Code). Se generó `presentacion.pdf` con 12 diapositivas siguiendo el guion del plan. La genera `python -m scripts.crear_presentacion`, que lee las cifras de `resultados/*.json`. El README incluye ahora la tabla de entregables, cómo ejecutar la entrega en Colab T4, la descarga del modelo base con su revisión fija, licencias y uso de IA. Angel revisó y dio por buenas las entradas de su turno 2 y la clasificación de errores. Las tres hipótesis cuantitativas (A ≥ 0.72, B ≥ 0.7368 y la corrección recuperando preguntas de A) no se cumplieron y se reportan tal cual.

**Horas de Angel Herrarte (estimación aproximada):** unas **12 h** en total.

- Turno 1: ~1 h, para redactar sus 20 preguntas de validación.
- Turno 2: ~6 h el 22 de octubre, entre la implementación previa al primer commit (16:20) y el último (20:03, hora de Guatemala), con esperas de GPU.
- Turno 4: ~5 h el 25 de octubre, desde unas 10:30 hasta la entrega.

Las horas se reconstruyeron a partir de las marcas de tiempo de los commits y de las ejecuciones en Colab; no son un registro cronometrado. Los tiempos de GPU (por ejemplo, 2782 s de entrenamiento de A) están en las métricas y no se suman como trabajo humano. **Horas de Jorge Lopez (estimación aproximada, mismo método):** unas **14 h** en total.

- Turno 1: ~7 h entre el 21 y el 22 de octubre. Incluye el plan de trabajo (commit del 21 a las 23:29), la preparación, la revisión e integración de los 15 esquemas y los 3,400 pares, y la redacción de sus 20 preguntas de validación, hasta la publicación del 22 a las 12:23.
- Turno 3: ~7 h el 23 de octubre, entre las correcciones previas al primer commit (08:54) y el cierre (14:35). Incluye el entrenamiento de B, el experimento en Colab y las esperas de GPU, coherente con la jornada que Jorge describió.

Registradas por Angel a partir de las marcas de tiempo de los commits de Jorge y de esta bitácora. Jorge puede corregirlas.
