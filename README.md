# Proyecto 3 — Text-to-SQL con LoRA

Proyecto de Deep Learning 2026 de la Universidad del Valle: adaptar un modelo de lenguaje pequeño mediante LoRA o QLoRA para generar consultas MySQL a partir de esquemas y preguntas en español.

**Estado:** planificación inicial. Aún no hay implementación, dataset preparado, entrenamientos ni resultados experimentales.

## Documentación

- [Enunciado oficial](Instrucciones/Proyecto_3_Texto_a_SQL.pdf).
- [Plan de trabajo y reparto en cuatro turnos](Instrucciones/PLAN_DE_TRABAJO.md). Referencia fija de organización; los avances se documentarán por separado.

## Objetivo y alcance

Entrenar y comparar dos configuraciones de LoRA sobre un modelo permitido, medirlas contra un baseline sin adapter y evaluar un experimento de inferencia. La calidad se medirá por exactitud ponderada de los resultados de ejecución SQL.

Se requieren al menos 2,000 pares de entrenamiento ejecutables en MySQL 8.4.10, al menos 10 esquemas propios para la generación de datos y una validación propia de 40 preguntas sobre al menos dos esquemas excluidos del entrenamiento.

Modelo propuesto: `Qwen/Qwen2.5-Coder-1.5B-Instruct`. La elección y las dependencias se confirmarán al verificar recursos. La entrega debe funcionar en Google Colab con GPU T4 y MySQL 8.4.10 con configuración predeterminada.

## Interfaz prevista

El futuro archivo `solucion.py` expondrá:

```python
def generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str:
    ...
```

Recibirá DDL con comentarios y una pregunta en español, y devolverá una sola consulta `SELECT` o `WITH ... SELECT`. Debe funcionar con y sin el callback opcional, permitir como máximo tres llamadas a este, generar de forma determinista y respetar los límites de 30 segundos por pregunta y cinco minutos de carga.

`config.json` permitirá activar o desactivar el adapter, usando el mismo prompt para comparar el modelo ajustado con el base. No se utilizarán APIs externas durante la generación de consultas de evaluación.

## Organización del equipo

1. Jorge Lopez: entorno, datos de entrenamiento y validación propia.
2. Angel Herrarte: evaluador, baseline y LoRA A.
3. Jorge Lopez: LoRA B, comparación y experimento de inferencia.
4. Angel Herrarte: auditoría final, análisis de errores, presentación y entrega.

El plan detalla tareas, criterios de cierre y commits propuestos. Ambos registrarán contribuciones auténticas desde sus propias cuentas. Integrantes: Jorge Lopez y Angel Herrarte.

## Ejecución y resultados

Todavía no existen comandos de instalación, entrenamiento o inferencia verificados. Se documentarán durante la implementación, junto con versiones, preparación de MySQL, obtención de datos, carga del modelo y reproducción de resultados en Colab T4.

Los entregables futuros incluyen `solucion.py`, `config.json`, `requirements.txt`, `adapter/`, `datos/`, `notebooks/`, `resultados/validacion_propia.csv`, `presentacion.pdf`, `BITACORA.md`, `CONTRIBUCIONES.md` e `historial_git.txt`.

## Licencias y uso de IA

Las fuentes de datos, licencias del modelo y datasets y condiciones de redistribución se registrarán al seleccionarlos. No se declara una licencia del repositorio por ahora.

Se utilizó asistencia de IA para revisar el enunciado y redactar el plan de trabajo y este README inicial. Durante el desarrollo se documentarán las herramientas empleadas, sus tareas, la generación o traducción de datos y las revisiones realizadas por los integrantes.

## Entrega

Fecha indicada en el enunciado: **25 de octubre de 2026, 23:59**; confirmar zona horaria en Canvas. Repositorio privado compartido con el docente y entrega en Canvas del repositorio comprimido y una presentación PDF de máximo 12 diapositivas. No habrá presentación oral. Cada integrante debe completar su coevaluación individual después de la entrega.
