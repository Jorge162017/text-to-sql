# Proyecto 3 — Text-to-SQL con LoRA

Deep Learning 2026 · Universidad del Valle · **Jorge Lopez y Angel Herrarte**.

**Estado:** primera parte de Jorge implementada y revisada técnicamente con asistencia de IA. Hay **3,400 pares de entrenamiento**, **15 esquemas propios** y **40 preguntas propias** sobre dos esquemas reservados. Los datos se certifican en MySQL 8.4.10 y se contrastan con algoritmos Python independientes. Turno 2 (Angel) completado: contrato de inferencia (`solucion.py`, `config.json`) y evaluador por ejecución implementados y probados. Baseline sin adapter en Colab T4: **EX = 0.5658 (43/76)**. LoRA A (r=8): **EX = 0.6974 (53/76)**, +0.1316, determinista; queda en `adapter/` con `usar_adapter: true`. Relevo a Jorge en [`RELEVO_JORGE.md`](RELEVO_JORGE.md). Jorge autorizó publicar esta etapa en tres commits; consultar el historial de Git para su evidencia.

## Documentación

- [Enunciado oficial](Instrucciones/Proyecto_3_Texto_a_SQL.pdf) y [plan fijo de trabajo](Instrucciones/PLAN_DE_TRABAJO.md).
- [Datos y procedencia](datos/README.md), [40 preguntas y referencias SQL](datos/validacion/PREGUNTAS.md).
- [Notebook de datos](notebooks/01_datos.ipynb), [notebook de evaluación en T4](notebooks/02_evaluacion_t4.ipynb), [relevo a Angel](RELEVO_ANGEL.md).
- [Bitácora](BITACORA.md) y [contribuciones](CONTRIBUCIONES.md).

## Preparar y comprobar los datos

Requisitos: Python 3.10 o superior, Docker y Compose v2. Entorno probado: Python 3.13 en macOS ARM64, imagen oficial `mysql:8.4.10`. El contrato también se probó localmente con Python 3.14, torch 2.14.1 (MPS) y transformers 5.20.2. La verificación en Colab T4 es parte del baseline.

Desde un checkout limpio, con Docker funcionando:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
docker compose up -d --wait mysql
python -m scripts.validar_datos --inicializar
python -m scripts.revisar_muestra
python -m scripts.auditar_datos --exigir-cierre
python -m unittest discover -s tests -v
```

El repositorio incluye DDL, semillas, candidatos y preguntas propias. La inicialización crea **17 bases sintéticas** en el contenedor exclusivo del proyecto. Si ya existen, omitir `--inicializar` para repetir solo las consultas. La conexión es local por `127.0.0.1:3307`; `.env` queda fuera de Git. El administrador importa los SQL propios y crea un lector temporal SELECT para certificar candidatos con transacciones READ ONLY.

Si cambian DDL o semillas, `--inicializar --recrear` reconstruye **solo las bases del manifiesto**, perdiendo cambios locales en ellas. Usarlo únicamente sobre el servidor sintético del proyecto. Para un servidor externo de desarrollo, definir `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER` y `MYSQL_PASSWORD`. Se comprueba versión exacta 8.4.10 y `ONLY_FULL_GROUP_BY`; no se modifica el modo SQL predeterminado.

Para regenerar las fuentes, sin reemplazar las preguntas propias:

```bash
python -m scripts.generar_datos --reemplazar
python -m scripts.preparar_validacion --reemplazar-esquemas
```

Después se deben reconstruir las bases y repetir certificación y revisión. Los hashes detectan evidencia desactualizada. Para detener y reanudar el servidor conservando sus datos: `docker compose stop mysql` y `docker compose up -d --wait mysql`.

## Datos y calidad

- Entrenamiento: **3,400 pares**, **66 familias de consultas**, **15 esquemas** y **6 topologías de relaciones distintas**, verificadas comparando los grafos de claves foráneas sin nombres de tablas. Diez dominios comerciales comparten una topología; academia, logística, turismo, energía y manufactura aportan cinco adicionales.
- Distribución: 940 fáciles, 1,400 medios y 1,060 difíciles. Todos se ejecutan sin error; cero descartes. Los 209 resultados vacíos del entrenamiento se registran y pueden ser correctos.
- Validación: **20 preguntas por esquema y 20 por integrante**, con 14 fáciles, 16 medias y 10 difíciles; peso total **76**. Todas tienen resultados no vacíos en las semillas actuales, con contraejemplos para fechas, estados, ceros, empates y nombres repetidos.
- `scripts.revisar_muestra` conserva su nombre histórico, pero ahora contrasta **los 3,440 pares completos** con cálculos Python sobre las tablas fuente. Se conservan duplicados, se exige orden cuando corresponde y se normalizan números a dos decimales.

Evidencia: [certificación SQL](resultados/reporte_datos.json), [revisión semántica](resultados/revision_semantica.json) y [entorno local](resultados/entorno_datos.json). La auditoría exige que los archivos, hashes y referencias estén completos; eliminar evidencia o dejarla obsoleta produce error.

**Limitación:** los datos son sintéticos y usan plantillas. Haber revisado cada resultado en las semillas actuales no garantiza generalización ni certifica el rendimiento en la evaluación oculta. Las métricas del modelo disponibles corresponden a las corridas históricas de Angel.

## Contrato y siguientes turnos

Modelo base: `Qwen/Qwen2.5-Coder-1.5B-Instruct`. La interfaz exigida está en `solucion.py`:

```python
def generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str:
    ...
```

- **Carga:** al importar `solucion` se lee `config.json` y se carga el modelo una sola vez (fp16 en CUDA/T4). Con `"usar_adapter": true` se aplica el adapter de `adapter/` y se fusiona; si falta, falla explícitamente en lugar de usar el base en silencio. `config.json` usa `usar_adapter: true` con el adapter LoRA A de `adapter/`.
- **Prompt congelado (`PROMPT_VERSION = "v1"`):** mensaje de sistema con reglas y mensaje de usuario con el esquema compactado y la pregunta. `compactar_esquema` quita índices simples y opciones físicas (`ENGINE`, `CHARSET`, `COLLATE`) y conserva columnas, PK, UNIQUE, FK y todos los `COMMENT`. Base, adapter y entrenamiento usan la misma función `construir_mensajes`.
- **Generación determinista:** greedy (`do_sample=False`, `num_beams=1`, `repetition_penalty=1.0`), máximo 320 tokens y `max_time=25 s` como red de seguridad. Reemplaza el `generation_config.json` de Qwen, que trae muestreo activado.
- **Salida:** se extrae una sola sentencia (bloque Markdown o texto libre, corte en el primer `;` fuera de literales). Si no es una única consulta `SELECT`/`WITH` de solo lectura (escrituras, `WITH ... DELETE`, `INTO OUTFILE`, `FOR UPDATE`, `SLEEP`...), devuelve `SELECT 1`.
- **Callback:** la estrategia actual es generación directa y no llama a `ejecutar` (0 de 3 llamadas). El experimento de corrección con `ejecutar` corresponde al turno 3.

### Evaluador por ejecución

```bash
python -m evaluacion.evaluar --nombre oraculo --oraculo --inicializar   # control: EX = 1.0 (76/76)
python -m evaluacion.evaluar --nombre baseline --adapter no             # modelo base
python -m evaluacion.evaluar --nombre lora_a --adapter si               # con adapter
```

En Colab T4, [`notebooks/02_evaluacion_t4.ipynb`](notebooks/02_evaluacion_t4.ipynb) instala MySQL 8.4.10 desde el binario oficial (sin Docker), corre el oráculo, el baseline y una repetición, y empaqueta la evidencia. `python -m evaluacion.congelar` escribe `resultados/configuracion_experimental.json` (prompt, generación, semilla, criterio y hashes de datos); cada `resumen.json` indica si su prompt coincide. `python -m evaluacion.determinismo baseline baseline_repeticion` exige SQL idéntico entre dos corridas.

`--inicializar` solo importa las bases de validación que falten. El evaluador reproduce el arnés del enunciado: usuario temporal con `SELECT` sobre los esquemas `val_*`, transacciones `READ ONLY`, `MAX_EXECUTION_TIME` de 10 s y callback `ejecutar` con 10 filas y máximo 3 llamadas. Reejecuta cada referencia y aborta si ya no coincide con `datos/validacion/referencias_resultados.jsonl`. Guarda `resultados/evaluaciones/<nombre>/predicciones.jsonl` (SQL, categoría, latencia y llamadas por pregunta) y `resumen.json` (EX global, por nivel y por esquema, configuración, hash del prompt, entorno y commit).

Reglas de acierto (`evaluacion/comparar.py`): los números se redondean a 2 decimales (half-up) en ambos lados y las fechas se comparan en ISO. El orden solo cuenta con `requiere_orden`; si no, se comparan multiconjuntos, así que los duplicados cuentan. Las columnas se alinean **por valores**, no por alias: cada columna esperada debe corresponder a una columna predicha distinta, y la proyección debe reproducir la referencia fila por fila. Las columnas adicionales no penalizan; las filas de más o de menos sí. Las categorías automáticas son sintaxis, columna/tabla inexistente, agregación, error de ejecución, resultado distinto, formato inválido y límite excedido (más de 30 s o más de 3 llamadas). La clasificación fina en JOIN y filtro corresponde al turno 4.

### Entrenamiento LoRA

```bash
python -m entrenamiento.entrenar --config entrenamiento/lora_a.json            # requiere CUDA (Colab T4)
python -m entrenamiento.entrenar --config entrenamiento/lora_a.json --prueba   # 2 pasos, directorio temporal
```

`entrenamiento/lora_a.json` contiene la hipótesis y todos los hiperparámetros. Una configuración B debe ser una copia que cambie solo `lora.r`; `tests/test_entrenamiento.py` lo verifica. El entrenamiento usa el mismo `construir_mensajes` que la inferencia y calcula la pérdida solo sobre el SQL de respuesta. Aparta un 5 % por esquema como dev para la curva y rechaza esquemas o preguntas de validación. Guarda el adapter en `salida_adapter` y en `resultados/entrenamientos/<nombre>/` las métricas (parámetros entrenables, tiempo, memoria pico, pérdidas), el historial y `curvas_loss.png`. En Colab se ejecuta con [`notebooks/03_entrenamiento_t4.ipynb`](notebooks/03_entrenamiento_t4.ipynb), que además evalúa con `--adapter si`, comprueba determinismo y compara con el baseline.

Orden del equipo: **Jorge → Angel → Jorge → Angel**, con el alcance detallado en el plan fijo. No entrenar ni construir few-shot con las preguntas o esquemas de validación.

## Licencias y uso de IA

Los esquemas, semillas y candidatos de entrenamiento son originales sintéticos preparados con asistencia de IA, sin datasets externos ni datos personales. Las preguntas originales se recibieron de Jorge con los autores declarados por grupo; el SQL de referencia, precisiones de redacción, scripts y documentación tienen asistencia de IA. Se preservan los originales. La revisión técnica por IA no se presenta como revisión humana ni como horas de trabajo de los integrantes.

No se ha elegido una licencia de redistribución del repositorio. MySQL y las dependencias conservan sus licencias; las dependencias locales están registradas en `requirements-datos.lock.txt`. El modelo base `Qwen/Qwen2.5-Coder-1.5B-Instruct` se distribuye con licencia **Apache-2.0** (archivo `LICENSE` del repositorio en Hugging Face). No se incluye en el repositorio: se descarga de Hugging Face al cargar. Las versiones de transformers, peft y accelerate están fijadas en `requirements.txt`; torch se toma del entorno de Colab. peft queda en 0.18.1 porque desde la 0.19 falla con el torchao 0.10 preinstalado en Colab. El código de datos no invoca APIs externas de generación.

## Entrega del curso

**25 de octubre de 2026, 23:59**, según el enunciado; confirmar zona horaria en Canvas. Se requiere repositorio privado con acceso del docente y entrega en Canvas del repositorio comprimido y PDF de máximo doce diapositivas. No habrá presentación oral. La coevaluación individual es posterior.

La privacidad, invitación del docente y disponibilidad de T4 deben confirmarse al publicar y comenzar el siguiente turno. Faltan los entregables de los turnos 2–4: modelo, entrenamientos, evaluador, experimentos, resultados del modelo, presentación e historial final. No son parte de esta implementación de datos.

## Correcciones antes de LoRA B (23 de octubre de 2026)

Se corrigió el corte de SQL por líneas vacías y se fijó la revisión `2e1fd397ee46e1388853d2af2c993145b0f1098a` para tokenizer y modelo, compartida por entrenamiento e inferencia. La revisión coincide con baseline y A originales. `config.json` conserva sus cuatro campos requeridos; no cambian el prompt ni los hiperparámetros de A.

La limpieza se identifica como v2. Se preservó el congelado anterior en `resultados/configuracion_experimental_angel.json`; el vigente incluye revisión, limpieza y hashes de código/datos. El evaluador ahora rechaza configuraciones obsoletas aunque el texto del prompt coincida. Las evaluaciones históricas y los pesos de A no se sobrescribieron.

**Verificación previa a B completada:** se recibió e integró la ejecución de [04_verificacion_correcciones_t4.ipynb](notebooks/04_verificacion_correcciones_t4.ipynb) en T4 con limpieza v2 y el snapshot fijado. Baseline corregido: **0.5658 (43/76)**; A corregido: **0.6974 (53/76)**; mejora **0.1316**. Ambas corridas repiten 40/40 consultas idénticas. Las cinco evaluaciones contienen cuarenta preguntas y reproducen sus aciertos al reejecutar sus 200 predicciones en MySQL 8.4.10. Ninguna carga superó cinco minutos y ninguna generación superó treinta segundos. La configuración adjunta coincide con la publicada. Informe: [verificacion_correcciones_t4.json](resultados/verificacion_correcciones_t4.json).

Para comparar B usar `baseline_corregido` y `lora_a_corregido`; conservar las corridas originales como históricos. No se reentrenó A. La revisión e integración de este ZIP son locales, pendientes de publicación; LoRA B y el experimento de inferencia aún no se iniciaron.


### Turno 3: preparar y ejecutar B

Jorge Lopez tiene preparada la hipótesis B en `entrenamiento/lora_b.json` y el notebook `notebooks/05_lora_b_t4.ipynb`. B cambia solo el rango de 8 a 16. **Preparación local; entrenamiento pendiente.** Publicar la hipótesis y el notebook antes de entrenar; abrir el notebook 05 en una sesión nueva de Colab con GPU T4 y el secret `GITHUB_TOKEN`, ejecutar en orden y descargar `lora_b_t4.zip`. Enviar el ZIP para verificar e integrar pesos, pérdidas, métricas y las dos evaluaciones. El notebook conserva y restaura A. Reservar aproximadamente 60–90 minutos; el tiempo real de B aún no se conoce.

Después se seleccionará A o B usando EX, latencia y memoria; se preparará otra ejecución en Colab para el experimento controlado de inferencia. Todavía no está seleccionado el adapter final ni completado el turno 3. No se debe modificar el congelado para el entrenamiento B.


### Resultado B y adapter seleccionado

B ya fue entrenado en T4 y su ZIP integrado y comprobado. La tabla siguiente corresponde a generación directa con el congelado vigente; las tres configuraciones son deterministas en 40/40 preguntas al repetir.

| Modelo | EX ponderada | Aciertos | Memoria pico de entrenamiento |
| --- | ---: | ---: | ---: |
| Base corregido | 43/76 = 0.5658 | 27/40 | No aplica |
| LoRA A corregido, r=8 | **53/76 = 0.6974** | 31/40 | 6.15 GiB |
| LoRA B, r=16 | 49/76 = 0.6447 | 30/40 | 6.28 GiB |

Se conserva **A en `adapter/`** por mayor EX y menor memoria; B está en `adapters/lora_b/`. Su hipótesis no se cumplió. Evidencia: `resultados/entrenamientos/lora_b/`, `resultados/evaluaciones/lora_b*` y `resultados/verificacion_lora_b_t4.json`. Las 80 predicciones de B y su repetición reprodujeron sus aciertos al reejecutarlas en MySQL local. Las versiones de Python reportadas difieren en un parche entre A corregido y B; las bibliotecas de ML reportan las mismas versiones. **Todavía falta el experimento de inferencia para completar el turno 3**; las instrucciones anteriores de ejecución B quedan como reproducción histórica.


### Ejecutar el experimento de inferencia

`notebooks/06_inferencia_t4.ipynb` prepara la comparación de generación directa frente a reparación de errores MySQL sobre **A**, con control adicional sin adapter y repetición de las cuatro combinaciones. No entrena. Después de publicar estos cambios, abrir en una sesión nueva de Colab T4 con el secret `GITHUB_TOKEN`, ejecutar en orden y descargar `inferencia_t4.zip`. Tiempo estimado: 25–40 minutos, según descargas. Si una celda falla, detenerse y compartir el error; no saltar controles.

Las corridas nuevas se llaman `inferencia_base_directa`, `inferencia_base_correccion`, `inferencia_a_directa`, `inferencia_a_correccion`, sus repeticiones y `inferencia_oraculo`. El congelado A/B histórico está en `resultados/configuracion_experimental_ab.json`; el vigente incluye el experimento. El prompt inicial no cambia; el tratamiento añade SQL previo y error MySQL solo tras un fallo. Máximo tres callbacks y dos reparaciones. Sin callback se conserva directa. Los límites se comprobarán en T4: el timeout del callback es 10 s en nuestro arnés y max_time del modelo no constituye un corte duro.

El contrato `solucion.py` aún usa directa. La propuesta del notebook no selecciona automáticamente la entrega: después de auditar el ZIP se integrará corrección solo si mejora EX y cumple tiempos y determinismo; en empate queda directa. Los notebooks 04/05 corresponden a la configuración histórica A/B y no deben usarse para reemplazar el congelado del experimento.
