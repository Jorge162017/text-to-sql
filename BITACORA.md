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

- Autor del registro y preparación: asistente de IA durante el turno de Angel Herrarte, a su solicitud. Revisión de Angel: pendiente. Esta entrada y `entrenamiento/lora_a.json` se publican **antes** de iniciar el entrenamiento; la fecha del commit sirve como evidencia.
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
