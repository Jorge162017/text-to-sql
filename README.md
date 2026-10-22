# Proyecto 3 — Text-to-SQL con LoRA

Deep Learning 2026 · Universidad del Valle · **Jorge Lopez y Angel Herrarte**.

**Estado:** primera parte de Jorge implementada y revisada técnicamente con asistencia de IA. Hay **3,400 pares de entrenamiento**, **15 esquemas propios** y **40 preguntas propias** sobre dos esquemas reservados. Los datos se certifican en MySQL 8.4.10 y se contrastan con algoritmos Python independientes. No se ha iniciado el baseline ni entrenamiento del modelo. Jorge autorizó publicar esta etapa en tres commits; consultar el historial de Git para su evidencia.

## Documentación

- [Enunciado oficial](Instrucciones/Proyecto_3_Texto_a_SQL.pdf) y [plan fijo de trabajo](Instrucciones/PLAN_DE_TRABAJO.md).
- [Datos y procedencia](datos/README.md), [40 preguntas y referencias SQL](datos/validacion/PREGUNTAS.md).
- [Notebook de datos](notebooks/01_datos.ipynb), [relevo a Angel](RELEVO_ANGEL.md).
- [Bitácora](BITACORA.md) y [contribuciones](CONTRIBUCIONES.md).

## Preparar y comprobar los datos

Requisitos: Python 3.10 o superior, Docker y Compose v2. Entorno probado: Python 3.13 en macOS ARM64, imagen oficial `mysql:8.4.10`. El modelo en Colab T4 corresponde a los turnos siguientes.

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

**Limitación:** los datos son sintéticos y usan plantillas. Haber revisado cada resultado en las semillas actuales no garantiza generalización ni certifica el rendimiento en la evaluación oculta. No se ejecutó todavía el modelo.

## Contrato y siguientes turnos

Modelo base propuesto: `Qwen/Qwen2.5-Coder-1.5B-Instruct`. Angel implementará `solucion.py`, `config.json`, el evaluador y las dependencias del modelo, y hará baseline y LoRA A. La interfaz exigida es:

```python
def generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str:
    ...
```

Debe devolver una sola consulta SELECT o WITH ... SELECT, funcionar con/sin callback, admitir como máximo tres llamadas a este, ser determinista, cargar en cinco minutos y responder en treinta segundos. Base y adapter se compararán con el mismo prompt. No se permiten APIs externas al generar consultas durante la evaluación.

Orden del equipo: **Jorge → Angel → Jorge → Angel**, con el alcance detallado en el plan fijo. No entrenar ni construir few-shot con las preguntas o esquemas de validación.

## Licencias y uso de IA

Los esquemas, semillas y candidatos de entrenamiento son originales sintéticos preparados con asistencia de IA, sin datasets externos ni datos personales. Las preguntas originales se recibieron de Jorge con los autores declarados por grupo; el SQL de referencia, precisiones de redacción, scripts y documentación tienen asistencia de IA. Se preservan los originales. La revisión técnica por IA no se presenta como revisión humana ni como horas de trabajo de los integrantes.

No se ha elegido una licencia de redistribución del repositorio. MySQL y las dependencias conservan sus licencias; las dependencias locales están registradas en `requirements-datos.lock.txt`. La licencia y condiciones del modelo base deberán documentarse al incorporarlo en el turno de Angel. El código de datos no invoca APIs externas de generación.

## Entrega del curso

**25 de octubre de 2026, 23:59**, según el enunciado; confirmar zona horaria en Canvas. Se requiere repositorio privado con acceso del docente y entrega en Canvas del repositorio comprimido y PDF de máximo doce diapositivas. No habrá presentación oral. La coevaluación individual es posterior.

La privacidad, invitación del docente y disponibilidad de T4 deben confirmarse al publicar y comenzar el siguiente turno. Faltan los entregables de los turnos 2–4: modelo, entrenamientos, evaluador, experimentos, resultados del modelo, presentación e historial final. No son parte de esta implementación de datos.
