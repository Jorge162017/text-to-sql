# Relevo del turno 3 de Jorge Lopez al turno 4 de Angel Herrarte

Cierre técnico: 23 de octubre de 2026. Preparado con asistencia de IA. El plan fijo en `Instrucciones/PLAN_DE_TRABAJO.md` no se modificó. Jorge confirmó trabajo durante gran parte del 23 de octubre, con pausas y esperas de GPU; la jornada aproximada consta en la bitácora, separada de los tiempos de entrenamiento.

## Entrega vigente

- Modelo: Qwen/Qwen2.5-Coder-1.5B-Instruct, revisión `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- Adapter seleccionado: **A, r=8, en `adapter/`**. Configuración en `config.json`; estrategia de `solucion.generar_sql`: **directa**, cero callbacks, compatible con `ejecutar=None`.
- B, r=16, conservado en `adapters/lora_b/`: 49/76, por debajo de A (53/76). Único hiperparámetro diferente: rango; alpha/r cambia como consecuencia.
- Corrección de errores conservada en `evaluacion/correccion.py` como experimento; no se activa en la entrega: empata con A directa y tarda más.

## Evidencia medida y decisión

| Corrida | Resultado | Evidencia |
| --- | --- | --- |
| Base directa | 43/76, 0.5658 | `resultados/evaluaciones/inferencia_base_directa/` |
| A directa | 53/76, 0.6974 | `resultados/evaluaciones/inferencia_a_directa/` |
| B directa | 49/76, 0.6447 | `resultados/evaluaciones/lora_b/` |
| Base corrección | 48/76, 0.6316 | `resultados/evaluaciones/inferencia_base_correccion/` |
| A corrección | 53/76, 0.6974 | `resultados/evaluaciones/inferencia_a_correccion/` |

Conservar las repeticiones e históricos. Todas las combinaciones del experimento son deterministas en 40/40 SQL y aciertos y cumplen límites medidos T4. A directa carga en 26.44 s, media 1.648 s, máxima 5.463 s. A corrección: media 1.979 s, máxima 11.467 s, máximo dos callbacks. La corrección recuperó dos preguntas del base, ninguna de A; no afirmar que toda consulta ejecutable es correcta. Mejora final frente al base con la misma estrategia directa: **10/76 = 0.1316**.

Auditorías: `resultados/verificacion_correcciones_t4.json`, `resultados/verificacion_lora_b_t4.json` y `resultados/verificacion_inferencia_t4.json`. Las 360 predicciones del último ZIP se reejecutaron en MySQL local; no constituyen nueva generación GPU. Selección consolidada en `resultados/seleccion_final_turno3.json`.

## Reproducción

Notebook `06_inferencia_t4.ipynb`, sesión limpia Colab T4 con secret `GITHUB_TOKEN`: instalación, MySQL 8.4.10 y pruebas incluidas. No repetir sobre carpetas existentes sin revisar; cambiar nombres de corrida para la auditoría final. CLI:

```bash
python -m evaluacion.evaluar --nombre auditoria_final_base --adapter no --inicializar
python -m evaluacion.evaluar --nombre auditoria_final_a --adapter si
python -m evaluacion.evaluar --nombre auditoria_final_a_repeticion --adapter si
python -m evaluacion.determinismo auditoria_final_a auditoria_final_a_repeticion
```

El congelado vigente incluye el nuevo evaluador y módulo experimental. El congelado A/B se preservó en `resultados/configuracion_experimental_ab.json`; las corridas antiguas no se reetiquetan. Los notebooks 04/05 son históricos. No cambiar el prompt, contrato o dependencias sin repetir las mediciones afectadas. B se ejecutó con Python 3.13.16 frente a 3.13.15 de A corregido: diferencia de parche documentada; bibliotecas ML reportan las mismas versiones.

## Trabajo de Angel pendiente

1. Auditoría final desde Colab limpio: dependencias, carga, tiempos, determinismo, contrato con/sin callback, consultas de lectura y exclusión de esquemas. No hace falta entrenar de nuevo.
2. Consolidar `resultados/validacion_propia.csv` con la evidencia de todas las configuraciones y clasificar errores en las categorías del plan; revisar causas de JOIN, filtros y agregación manualmente.
3. Justificar una predicción de EX oculto, distinguiéndola de resultados medidos. No presentar 69.74 % como exactitud oculta conocida.
4. Crear PDF de máximo 12 diapositivas, completar documentación/licencias/uso de IA y registrar horas y contribuciones reales.
5. Comprobar acceso del docente, producir `historial_git.txt` tras los commits, preparar ZIP y PDF para Canvas y hacer la entrega y coevaluaciones según el plan.

No usar los esquemas ni preguntas de validación para entrenamiento o few-shot. Conservar los resultados de hipótesis que no se cumplieron. Hay pérdida dev muy baja y riesgo de memorización de plantillas: no garantiza generalización.
