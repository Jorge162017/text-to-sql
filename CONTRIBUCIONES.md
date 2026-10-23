# Contribuciones

Registrar hechos y evidencia reales. Jorge encargó al asistente completar la revisión técnica de su primer turno. Está realizada con asistencia de IA; no se atribuye una revisión humana no efectuada ni se inventan horas. Jorge autorizó publicar la implementación en tres commits desde su cuenta de Git.

| Tarea | Responsable del turno | Evidencia local | Estado |
| --- | --- | --- | --- |
| Plan y reparto inicial | Jorge Lopez | `Instrucciones/PLAN_DE_TRABAJO.md`, commit `44ec069` | Publicado previamente |
| Entorno reproducible MySQL y formato de datos | Jorge Lopez, con asistencia de IA | `compose.yaml`, `.env.example`, `requirements.txt`, `scripts/comun.py` | Implementado y revisado técnicamente con IA |
| Quince esquemas y generación de 3,400 candidatos | Jorge Lopez, con asistencia de IA | `scripts/generar_datos.py`, `datos/esquemas/train_*/`, `datos/candidatos/entrenamiento.jsonl` | Implementado y revisado técnicamente con IA |
| Certificación SQL y control de particiones | Jorge Lopez, con asistencia de IA | `scripts/validar_datos.py`, `scripts/auditar_datos.py`, `tests/test_integridad_datos.py` | 3,440 resultados contrastados con algoritmos Python independientes; auditoría y pruebas aprobadas |
| Dos esquemas reservados y casos límite de validación | Jorge Lopez, con asistencia de IA | `scripts/preparar_validacion.py`, `datos/esquemas/val_*/` | Semillas reforzadas; borradores IA redundantes eliminados |
| Preguntas propias de validación recibidas por chat | Jorge Lopez (1–10 y 21–30) y Angel Herrarte (11–20 y 31–40), según lo indicado por Jorge | `datos/validacion/preguntas_propias.jsonl`, campo `pregunta_original` | 20 por integrante; Originales preservados; SQL y precisiones revisados con asistencia de IA a solicitud de Jorge |
| Relevo y limpieza del primer turno | Jorge Lopez, con asistencia de IA | `RELEVO_ANGEL.md`, `README.md`, `datos/README.md` | Cierre técnico preparado; publicación autorizada por Jorge; evidencia en el historial de Git |
| Contrato de inferencia y evaluador ponderado | Angel Herrarte, con asistencia de IA | `solucion.py`, `config.json`, `evaluacion/`, `tests/test_solucion.py`, `tests/test_evaluador*.py`, `resultados/evaluaciones/oraculo/` | Implementado; oráculo EX = 1.0 y 46 pruebas aprobadas; revisión de Angel pendiente |
| Baseline sin adapter en Colab T4 | Angel Herrarte (ejecución en Colab), con asistencia de IA en integración y análisis | `notebooks/02_evaluacion_t4.ipynb`, `resultados/evaluaciones/baseline/`, `baseline_repeticion/`, `oraculo_t4/`, `resultados/configuracion_experimental_angel.json` | EX = 0.5658 (43/76); determinismo 40/40; oráculo 76/76 |
| Hipótesis, entrenamiento y evaluación de LoRA A | Angel Herrarte (ejecución en Colab), con asistencia de IA en implementación, integración y análisis | `entrenamiento/`, `notebooks/03_entrenamiento_t4.ipynb`, `adapter/`, `resultados/entrenamientos/lora_a/`, `resultados/evaluaciones/lora_a*/`, commit de la hipótesis `26b9ab2` | EX = 0.6974 (53/76), +0.1316 sobre el baseline; hipótesis cuantitativa (≥ 0.72) no cumplida |
| Relevo al turno 3 | Angel Herrarte, con asistencia de IA | `RELEVO_JORGE.md`, `BITACORA.md` | Entregado |
| LoRA B e inferencia | Jorge Lopez | Se registrará en su turno | No iniciado |
| Auditoría final y entrega | Angel Herrarte | Se registrará en su turno | No iniciado |
| Correcciones previas al turno 3 | Jorge Lopez, con asistencia de IA | `solucion.py`, `entrenamiento/entrenar.py`, `tests/test_solucion.py`, `tests/test_configuracion_experimental.py`, notebook 04 | Código y regresiones comprobados; correcciones publicadas en `23e7d8c`; reevaluación T4 recibida y verificada |
| Verificación de correcciones en T4 previa a B | Jorge Lopez (entrega de ejecución en Colab), con asistencia de IA en revisión e integración | `notebooks/04_verificacion_correcciones_t4.ipynb`, `resultados/evaluaciones/*corregido*/`, `resultados/verificacion_correcciones_t4.json` | 43/76 baseline, 53/76 A; determinismo 40/40; 200 predicciones reproducidas en MySQL; integración local sin nuevos commits |


| Turno 3: preparación local | Responsable | Evidencia | Estado |
| --- | --- | --- | --- |
| Hipótesis B previa y comparación de un factor | Jorge Lopez, asistido por IA | `entrenamiento/lora_b.json`, `BITACORA.md` | Preparado; publicación y entrenamiento pendientes |
| Notebook T4 con preservación de A, repetición y exportación | Jorge Lopez, asistido por IA | `notebooks/05_lora_b_t4.ipynb` | Validado localmente; no ejecutado en T4 |
