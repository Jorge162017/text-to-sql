# Plan de trabajo — Proyecto 3: Text-to-SQL

Documento de planificación fijo. No usar este archivo como bitácora, checklist de avance ni registro de resultados; no modificarlo durante la implementación. Los avances se registrarán en `BITACORA.md`, las responsabilidades y evidencias en `CONTRIBUCIONES.md` y los resultados en `resultados/`.

Fuente: [enunciado oficial](Proyecto_3_Texto_a_SQL.pdf), páginas 1–3. Plan preparado el 21 de octubre de 2026. Todavía no se inicia la implementación.

## 1. Qué pide el proyecto

Entrenar con LoRA o QLoRA un LLM pequeño que reciba el esquema de una base de datos y una pregunta en español y devuelva una consulta MySQL correcta. El docente probará preguntas y bases desconocidas, y comparará el modelo con y sin adapter.

### Condiciones obligatorias

- Modelo base permitido: `Qwen/Qwen2.5-Coder-1.5B-Instruct` (recomendado), `Qwen/Qwen2.5-Coder-0.5B-Instruct` o `Qwen/Qwen3-1.7B` con razonamiento desactivado.
- Entregar el modelo base mediante su configuración y un adapter LoRA/QLoRA entrenado por la pareja. No utilizar otro modelo ni APIs externas para generar consultas durante la evaluación.
- Motor: **MySQL 8.4.10**, configuración predeterminada, incluido `ONLY_FULL_GROUP_BY`. SQLite no sustituye esta validación.
- Evaluación en Google Colab con GPU T4, instalando `requirements.txt`.
- `solucion.py` debe cargar el modelo de `config.json` y exponer exactamente `generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str`.
- El esquema llega como sentencias `SHOW CREATE TABLE`, incluidos los `COMMENT`. La pregunta está en español.
- Devolver una sola consulta `SELECT` o `WITH ... SELECT`, sin texto explicativo ni consultas que modifiquen datos.
- `ejecutar(sql)` es opcional. Devuelve `ok`, `columnas`, `filas` (hasta 10) y `error`; se permiten como máximo **3 llamadas por pregunta**. La función también debe funcionar cuando sea `None`.
- Máximo **30 segundos por pregunta** y **5 minutos para cargar el modelo**. Generación determinista.
- `config.json` contiene `modelo_base`, `adapter`, `usar_adapter` y `semilla`. Valores iniciales propuestos: modelo recomendado, `"adapter/"`, `true` y `2026`. Con `usar_adapter: false` se utiliza el mismo prompt con el modelo base.

### Trabajo experimental obligatorio

1. Al menos **2,000 pares de entrenamiento** pregunta–SQL aceptados tras ejecutarlos sin error en MySQL 8.4.10. El enunciado permite fuentes públicas como Spider/BIRD adaptadas a MySQL y traducidas al español, y pares generados con un LLM sobre al menos **10 esquemas propios**. Para cubrir el requisito, planificar esos 10 esquemas propios y documentar cualquier fuente adicional. Registrar descartes y motivos. El uso de un LLM para preparar datos debe declararse; no habilita APIs en la inferencia entregada.
2. Validación propia con **al menos 2 esquemas excluidos del entrenamiento** y **40 preguntas en total**, escritas por ustedes, distribuidas entre fácil, media y difícil. Separar por esquema, no por pregunta. Propuesta: dos esquemas de 5–10 tablas y 20 preguntas por esquema, con 12 fáciles, 16 medias y 12 difíciles en total. Esta distribución es una decisión del equipo, no una cuota del enunciado.
3. Baseline sin adapter sobre esa validación.
4. Dos configuraciones de LoRA que difieran en **un solo factor**. Registrar la hipótesis antes de cada entrenamiento, parámetros entrenables, tiempo y curvas de loss.
5. Un experimento de inferencia con comparación controlada.
6. Análisis de errores: sintaxis, columna/tabla inexistente, JOIN, agregación, filtro y resultado distinto.
7. Predicción justificada de la exactitud ponderada en la evaluación oculta.

### Cómo se evalúa

La prueba oculta contiene una o más bases de 5–10 tablas y 30–40 preguntas. Pesos: fácil = 1 (una tabla), media = 2 (JOIN, GROUP BY, HAVING), difícil = 3 (subconsultas, WITH, ventanas, fechas).

`EX = suma de pesos de preguntas acertadas / suma de pesos de todas las preguntas`.

Se compara el **resultado de ejecución**, no el texto SQL. El orden solo cuenta cuando la pregunta lo pide; números redondeados a dos decimales; una columna adicional no penaliza. El evaluador propio debe documentar cómo alinea columnas y conserva duplicados, y cubrir estas reglas.

| Componente | Puntos | Evidencia prevista |
| --- | ---: | --- |
| EX con adapter y mejora frente al base | 40 | Comparación reproducible base/adapter; 30 puntos completos con EX ≥ 0.70 y 10 con mejora absoluta ≥ 0.15 |
| Dataset, baseline y dos LoRA | 25 | Datos ejecutables, descartes, baseline, hipótesis y registros de ambas corridas |
| Validación, inferencia y errores | 20 | Esquemas separados, preguntas propias, experimento y análisis |
| Colaboración | 7 | Commits de ambos, bitácora, contribuciones e historial |
| Presentación y predicción | 8 | PDF de hasta 12 diapositivas con predicción sustentada |

Penalizaciones: modelo no permitido o API externa = 0 en evaluación oculta; contaminación de esquemas = −15; salida no determinista = −10; consultas que modifican la base = −10; sin commits de ambos = 0 en colaboración. Si la entrega falla por un error de la pareja, existe una única corrección en 24 horas con penalización de −10 puntos.

## 2. Acuerdo de colaboración y equilibrio

Orden obligatorio: **Jorge Lopez → Angel Herrarte → Jorge Lopez → Angel Herrarte**. Cada turno representa aproximadamente el **25 % del esfuerzo**, no necesariamente la misma cantidad de archivos o commits. Reservar el mismo bloque de horas activas por turno y registrar horas reales en la bitácora. Los tiempos de GPU y la dificultad pueden variar; la igualdad exacta no se puede garantizar antes de ejecutar.

| Turno | Responsable | Área principal | Alcance |
| --- | --- | --- | --- |
| 1 | Jorge Lopez | Datos | Entorno, entrenamiento validado y validación propia |
| 2 | Angel Herrarte | Entrenamiento | Evaluador, contrato de inferencia, baseline y LoRA A |
| 3 | Jorge Lopez | Entrenamiento e inferencia | LoRA B, comparación y experimento de inferencia |
| 4 | Angel Herrarte | Validación y errores | Auditoría final, análisis, presentación y entrega |

No pasar al siguiente turno sin los entregables de cierre. Cada persona deja comandos, rutas, configuración y pendientes en su última entrada de bitácora. Los resultados de validación sirven para comparar; no convertir sus preguntas ni SQL en ejemplos de entrenamiento o few-shot.

### Reglas de commits y evidencia

- Cada integrante hace sus propios commits desde su propia cuenta. No cambiar autorías ni fechas para aparentar trabajo anterior.
- Hacer **al menos 3 commits sustanciales por turno**: 12 commits de implementación previstos, más los de documentación inicial y cierre que correspondan. Este número es una propuesta del equipo, no un mínimo exigido por el docente.
- Cada commit debe incluir un avance coherente y su evidencia; no dividir cambios vacíos para aumentar el conteo.
- Integrar y subir cada commit revisado al repositorio privado antes del relevo. Evitar commits de credenciales, cachés, entornos o modelos base descargados; prever transferencia de adapters y datos si exceden los límites de GitHub, manteniendo los archivos requeridos en la entrega.
- Crear al menos **8 entradas reales y fechadas** en `BITACORA.md`: dos por turno, con autor, tarea, resultado, tiempo y referencia al commit o artefacto. No inventar resultados ni fechas.
- Mantener `CONTRIBUCIONES.md` con tarea, responsable y evidencia verificable; ambos deben acreditar responsabilidad en datos, entrenamiento o validación/errores.
- Compartir el repositorio privado con el docente desde el inicio del trabajo. La rúbrica exige commits de ambos durante las dos semanas: al 21 de octubre ya no es posible reconstruir ese período. Registrar el trabajo real y consultar al docente si el inicio tardío afecta ese requisito.

## 3. Turno 1 — Jorge Lopez: entorno, datos y validación propia

**Objetivo:** dejar datos confiables y una partición por esquema que permita entrenar y medir sin fugas.

1. Crear la estructura de trabajo, dependencias iniciales y entorno de MySQL 8.4.10. Definir modelo base y formato de ejemplo: identificador, esquema, pregunta en español, SQL, procedencia y nivel cuando aplique.
2. Diseñar al menos 10 esquemas propios de entrenamiento, poblarlos con datos útiles y conservar DDL con comentarios. Preparar pares suficientes para conservar al menos 2,000 después del filtrado; cubrir JOIN, agregaciones, subconsultas, ventanas y fechas. Documentar licencias, traducciones y generación asistida.
3. Automatizar la ejecución de cada SQL contra su esquema MySQL. Guardar aceptados y descartados con su motivo y conteos. Revisar también coherencia pregunta–SQL en una muestra por esquema: ejecutar sin error no garantiza una respuesta correcta.
4. Crear otros dos esquemas independientes, con datos que permitan detectar errores, y escribir manualmente las 40 preguntas y SQL de referencia. Registrar columnas esperadas, nivel, peso y si exigen orden. Confirmar que las referencias se ejecutan y que no hay esquemas compartidos con entrenamiento.
5. Crear el notebook de datos y las primeras entradas reales de bitácora y contribuciones. Dejar identificado el conjunto de entrenamiento y de validación que usarán las siguientes etapas.

**Commits previstos, en orden:**

1. `chore: preparar entorno MySQL y estructura de datos`
2. `feat(datos): construir y validar al menos 2000 pares de entrenamiento`
3. `feat(validacion): agregar 2 esquemas independientes y 40 preguntas propias`

**Cierre verificable:** 2,000 o más pares aceptados, 10 o más esquemas propios de entrenamiento, reporte de descartes, 2 esquemas reservados y 40 referencias ejecutables; notebook y comandos de preparación reproducibles. Entregar a Angel Herrarte rutas, formato y conteos.

## 4. Turno 2 — Angel Herrarte: evaluador, baseline y LoRA A

**Objetivo:** tener una primera entrega ejecutable y una medición base contra la cual comparar el fine-tuning.

1. Implementar `solucion.py`, `config.json` y carga compatible con T4. Separar la carga de la generación por pregunta; soportar el interruptor del adapter y conservar el mismo prompt entre base y adapter. Respetar SQL de solo lectura, determinismo y límites.
2. Implementar el evaluador por ejecución con pesos 1/2/3 y las reglas del enunciado. Guardar SQL generado, estado, tiempo, resultados y acierto por pregunta. Comprobarlo con casos conocidos correctos e incorrectos, incluidos orden, duplicados y redondeo.
3. Ejecutar y guardar baseline completo sin adapter antes de entrenar. Registrar EX global y por dificultad, errores y latencia. Congelar prompt, datos, semilla, presupuesto de generación y criterio de evaluación para la comparación A/B.
4. Escribir la hipótesis A antes de iniciar el entrenamiento. Propuesta: LoRA A con `r=8`, manteniendo una configuración común documentada. Entrenar, guardar adapter A, configuración completa, número de parámetros entrenables, tiempo y curvas de loss. Evaluarlo con el mismo prompt del baseline.
5. Dejar notebook de entrenamiento reutilizable y presupuesto estimado para la corrida B. Registrar dependencias exactas y evidencia de ejecución en T4.

**Commits previstos, en orden:**

1. `feat: implementar contrato de inferencia y evaluador ponderado`
2. `eval: registrar baseline sin adapter y configuracion experimental`
3. `train: entrenar y evaluar LoRA A con hipotesis y curvas`

**Cierre verificable:** baseline y LoRA A medidos sobre las 40 preguntas, contrato funcional, scripts/notebooks reutilizables y registros completos. Entregar a la siguiente etapa los valores exactos de todos los hiperparámetros y el prompt congelado.

## 5. Turno 3 — Jorge Lopez: LoRA B y experimento de inferencia

**Objetivo:** completar la comparación controlada y seleccionar una estrategia de inferencia con evidencia.

1. Registrar la hipótesis B **antes** de entrenar: aumentar el rango de 8 a 16 podría mejorar la representación de consultas complejas con mayor costo de memoria y cómputo. Cambiar únicamente `r`; mantener `lora_alpha`, dropout, módulos objetivo, datos, orden, pasos, optimizador, tasa de aprendizaje, semilla, cuantización, prompt y evaluación iguales. Registrar las consecuencias derivadas del cambio de rango, sin introducir otro hiperparámetro distinto.
2. Entrenar LoRA B; guardar adapter B, configuración, parámetros entrenables, tiempo y curvas. Evaluar A y B con el mismo procedimiento y seleccionar el adapter según EX, latencia y memoria. Si la configuración resulta inviable en T4, documentar el intento y repetir la pareja de experimentos bajo una configuración común viable; no presentar dos corridas con múltiples diferencias como comparación de un solo factor.
3. Hacer un experimento de inferencia controlado sobre el adapter seleccionado. Propuesta: comparar generación directa contra corrección usando `ejecutar`. Mantener el mismo prompt inicial y todas las demás condiciones. No exceder tres llamadas ni 30 segundos; funcionar sin callback. Guardar resultados por pregunta, EX, latencia y número de llamadas.
4. Actualizar el contrato con la estrategia elegida solo si respeta los límites. Si cambia el prompt final, repetir también el baseline sin adapter con ese mismo prompt para que la comparación final sea válida. Mantener claramente separados resultados de A/B y del experimento de inferencia.
5. Colocar el adapter seleccionado en `adapter/`, conservar evidencia y configuraciones de ambas corridas y preparar tabla de comparación base/A/B/experimento. No borrar resultados que no mejoren.

**Commits previstos, en orden:**

1. `train: registrar hipotesis y entrenar LoRA B cambiando solo el rango`
2. `eval: comparar LoRA A y B y seleccionar adapter`
3. `feat(inferencia): evaluar correccion SQL y registrar estrategia final`

**Cierre verificable:** dos corridas comparables con hipótesis previas, tiempos, parámetros y curvas; experimento con control; adapter final y resultados rastreables. Entregar a Angel Herrarte comandos de reproducción, decisiones y limitaciones observadas.

## 6. Turno 4 — Angel Herrarte: auditoría, errores y entrega

**Objetivo:** cerrar la calidad de la entrega y explicar los resultados con evidencia.

1. Probar la entrega desde un entorno limpio de Colab T4 instalando únicamente `requirements.txt`. Cargar adapter y base por separado; verificar tiempos de carga y generación, determinismo, formato SQL y funcionamiento con/sin callback. Validar tope de llamadas, consultas de solo lectura y separación de esquemas. Corregir fallos de integración y repetir solo las mediciones afectadas.
2. Consolidar `resultados/validacion_propia.csv` con identificador, esquema, pregunta, dificultad, peso, referencia, versión/configuración, SQL generado, ejecución, acierto, latencia y categoría de error. Conservar evidencia suficiente para reproducir la comparación sin depender del estado de un notebook.
3. Revisar los fallos y clasificarlos en sintaxis, columna/tabla inexistente, JOIN, agregación, filtro y resultado distinto. Presentar conteos, ejemplos y EX por dificultad; documentar la regla si un fallo tiene varias causas.
4. Estimar y justificar EX oculto a partir de los resultados propios y su composición por dificultad, cambios de dominio y limitaciones. Distinguir la estimación de una medición; no afirmar que se alcanzó un resultado oculto conocido. No usar el conjunto reservado para fabricar ejemplos de entrenamiento.
5. Crear `presentacion.pdf` de **máximo 12 diapositivas**. Guion sugerido: objetivo; contrato; datos/procedencia; validación; baseline; hipótesis A/B; entrenamiento/curvas; comparación; inferencia; errores; predicción; reproducibilidad, contribuciones y límites.
6. Completar README con instrucciones reales, dependencias, descarga/carga del modelo base, licencias, uso de IA y artefactos; cerrar bitácora y tabla de contribuciones. Revisar acceso del docente y que los adapters/datos estén incluidos en los archivos de entrega.
7. Generar `historial_git.txt` con `git log --all --date=iso --stat > historial_git.txt` tras los commits sustanciales. Hacer un commit final de este archivo; su propio commit quedará naturalmente fuera de la captura. Preparar el comprimido del repositorio y el PDF para Canvas, comprobar que abren y subir antes del cierre. Cada uno realiza después su coevaluación individual.

**Commits previstos, en orden:**

1. `fix: verificar entrega reproducible en Colab T4 y limites de inferencia`
2. `eval: consolidar validacion analisis de errores y prediccion de EX`
3. `docs: completar presentacion README bitacora y contribuciones`

Commit de cierre adicional: `docs: agregar historial git para entrega`.

**Cierre verificable:** instalación limpia exitosa, todos los artefactos disponibles, PDF ≤12 diapositivas, al menos ocho entradas auténticas y contribuciones de ambos, comprimido y PDF entregados por Canvas y repositorio privado accesible al docente.

## 7. Estructura objetivo al terminar

Esta es una estructura futura; este plan no implica crear ni ejecutar todavía su contenido.

```text
README.md
solucion.py
config.json
requirements.txt
adapter/                         # Adapter final seleccionado
datos/                           # Entrenamiento, validación, DDL, datos y descartes
notebooks/                       # Datos, entrenamiento y evaluación
resultados/
  validacion_propia.csv
  ...                            # Baseline, A/B, inferencia, curvas y errores
presentacion.pdf
BITACORA.md
CONTRIBUCIONES.md
historial_git.txt
Instrucciones/
  Proyecto_3_Texto_a_SQL.pdf
  PLAN_DE_TRABAJO.md              # Referencia fija; no registrar avances aquí
```

## 8. Calendario propuesto

Entrega oficial: **domingo 25 de octubre de 2026 a las 23:59**. No habrá presentación oral. Medio: repositorio privado en GitHub y, en Canvas, repositorio comprimido más PDF. El enunciado no especifica zona horaria: confirmar el cierre mostrado en Canvas.

| Fecha propuesta | Turno | Meta |
| --- | --- | --- |
| 21 de octubre, cuando acuerden comenzar | 1 — Jorge Lopez | Preparación, datos y validación propia |
| 22 de octubre | 2 — Angel Herrarte | Evaluador, baseline y LoRA A |
| 23 de octubre | 3 — Jorge Lopez | LoRA B e inferencia |
| 24 de octubre | 4 — Angel Herrarte | Auditoría, análisis y documentación |
| 25 de octubre, antes del cierre | Margen de entrega | Resolver bloqueos y comprobar subida; sin experimentos nuevos planeados |

El calendario es ajustado y depende de disponibilidad de GPU y horas de ambos. Antes de empezar, acordar un bloque equivalente de horas por turno y asegurar T4. Si empiezan más tarde, conservar los cuatro turnos y todos los requisitos, usando el margen; no reducir mínimos de datos, validación o experimentos para aparentar cumplimiento.

## 9. Verificación final por requisito

| Requisito | Se construye en | Se comprueba en |
| --- | --- | --- |
| Modelo permitido y MySQL 8.4.10 | 1 y 2 | 4 |
| ≥2,000 pares válidos, ≥10 esquemas propios y descartes | 1 | 4 |
| ≥2 esquemas excluidos y 40 preguntas propias en tres niveles | 1 | 2 y 4 |
| Contrato, config, determinismo y límites | 2 y 3 | 4 |
| Baseline con mismo prompt y evaluación por ejecución | 2; repetir en 3 si cambia prompt | 4 |
| Dos LoRA, un factor, hipótesis previas, tiempos, parámetros y curvas | 2 y 3 | 4 |
| Experimento de inferencia | 3 | 4 |
| Errores por categoría y predicción justificada | 4 | 4 |
| Notebooks y CSV de validación | 1–4 | 4 |
| Commits de ambos, ≥8 entradas y contribuciones | Cada turno | 4 |
| Historial, README, licencias y uso de IA | Cada turno; cierre en 4 | 4 |
| PDF ≤12 diapositivas y entrega en GitHub/Canvas | 4 | 4 |
| Coevaluación individual posterior | Cada integrante | Cada integrante |
