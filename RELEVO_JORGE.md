# Relevo del turno 2 de Angel al turno 3 de Jorge

Preparado con asistencia de IA durante el turno de Angel. El plan en `Instrucciones/` sigue fijo; los detalles y la evidencia están en `BITACORA.md` y en el historial de Git.

## Estado recibido

| Corrida | EX | Fácil | Media | Difícil | Evidencia |
| --- | ---: | ---: | ---: | ---: | --- |
| Baseline sin adapter | 0.5658 (43/76) | 14/14 | 20/32 | 9/30 | `resultados/evaluaciones/baseline/` |
| LoRA A (r=8) | **0.6974 (53/76)** | 14/14 | 24/32 | 15/30 | `resultados/evaluaciones/lora_a/` |

Ambas corridas se hicieron en Colab T4, son deterministas (40/40 SQL idénticos al repetir) y usan el mismo prompt v1 (`resultados/configuracion_experimental.json`). LoRA A está en `adapter/` y `config.json` tiene `usar_adapter: true`. La hipótesis A no se cumplió cuantitativamente: se predijo una EX de 0.72 o más.

## Configuración común congelada (no cambiar en B)

`entrenamiento/lora_a.json`:

- **Modelo:** `Qwen/Qwen2.5-Coder-1.5B-Instruct`, revisión `2e1fd397ee46e1388853d2af2c993145b0f1098a`, semilla 2026 (también `data_seed`).
- **LoRA:** `lora_alpha=16`, `lora_dropout=0.05`, `bias=none`, módulos `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj`.
- **Optimización:** 1 época, `adamw_torch`, LR 2e-4 coseno con 10 pasos de calentamiento, `weight_decay=0` y `max_grad_norm=1.0`. Batch 2 × acumulación 8, equivalente a 16.
- **Precisión y memoria:** fp16 con el modelo base en fp16 y la LoRA en fp32; gradient checkpointing sin reentrada; `max_longitud=1024` sin truncar.
- **Datos:** `datos/entrenamiento/pares.jsonl`, `fraccion_dev=0.05` por esquema, con 3,230 pares de entrenamiento y 170 de dev. La pérdida se calcula solo sobre el SQL y `<|im_end|>`.
- **Prompt e inferencia:** `construir_mensajes` de `solucion.py` (v1, sha256 `1fb4d982…`); generación greedy con 320 tokens y estrategia directa.
- **Evaluación:** `python -m evaluacion.evaluar`, con las reglas del README.

## Correcciones previas al turno 3 (23 de octubre)

Se corrigió la limpieza SQL para conservar líneas vacías y se fijó en los cargadores de entrenamiento e inferencia el snapshot de A (`2e1fd397ee46e1388853d2af2c993145b0f1098a`). El prompt v1, pesos de A e hiperparámetros permanecen iguales.

La configuración histórica está preservada en `resultados/configuracion_experimental_angel.json`. El congelado vigente incluye limpieza v2, revisión fija y hashes completos; el evaluador comprueba toda la configuración.

**Verificación T4 completada el 23 de octubre.** Jorge entregó el ZIP producido por `notebooks/04_verificacion_correcciones_t4.ipynb`. Se integraron `baseline_corregido*`, `lora_a_corregido*` y `oraculo_corregido`, sin reentrenar ni sobrescribir A o sus históricos. Baseline corregido: 43/76 (EX 0.5658); A corregido: 53/76 (EX 0.6974), mejora 0.1316. Ambas repeticiones son idénticas en 40/40 consultas. La configuración coincide byte a byte con la publicada; las 200 predicciones también reproducen sus aciertos en el MySQL local. Evidencia: `resultados/verificacion_correcciones_t4.json`. Estas son las corridas de referencia para comparar B; la verificación previa a B ya está completa.

## Corrida B

1. Escribir la hipótesis B en la bitácora **y** en `entrenamiento/lora_b.json` antes de entrenar, y publicarla en Git. Cambiar **solo** `lora.r` de 8 a 16. Además cambian `nombre` y `hipotesis`, y `salida_adapter` debe apuntar a otra carpeta, por ejemplo `adapters/lora_b/`, para no sobrescribir A. `python -m unittest tests.test_entrenamiento` falla si cambia cualquier otro valor.
2. Consecuencia derivada que hay que registrar: con `lora_alpha` fijo, la escala alpha/r baja de 2.0 a 1.0 y los parámetros entrenables se duplican, de unos 9.2 M a unos 18.5 M.
3. Copiar `notebooks/03_entrenamiento_t4.ipynb` y cambiar `lora_a` por `lora_b`. Para evaluar B con `--adapter si`, el adapter tiene que estar en `adapter/`: copiar temporalmente A a otra carpeta, por ejemplo `adapters/lora_a/`, y dejar en `adapter/` el seleccionado al final.
4. **Presupuesto en T4:** A tardó 46.4 min y usó 6.15 GiB de memoria pico; B debería tardar algo más con memoria de sobra. Hay que sumar unos 10 min de evaluación y repetición, y 5 min de preparación.
5. En Colab: reiniciar siempre el entorno antes de ejecutar, usar GPU T4 y el secret `GITHUB_TOKEN`. `requirements.txt` fija `peft==0.18.1`, porque las versiones desde 0.19 fallan con el torchao 0.10 de Colab.

## Observaciones para el experimento de inferencia

- En LoRA A, 4 de los 9 fallos son errores de ejecución: 3 columnas inexistentes y 1 uso inválido de función de grupo. Una corrección con `ejecutar` (máximo 3 llamadas) que reenvíe el mensaje de error podría recuperar parte de ellos.
- Los 5 fallos restantes se ejecutan pero dan otro resultado: uniones que omiten la tabla intermedia `ejemplares` y ROW_NUMBER sin la partición adecuada. Para esos, el callback solo ayudaría si se revisan las filas.
- Si el experimento cambia el prompt, hay que repetir también el baseline con ese prompt (plan, turno 3, punto 4).

## Límites

No usar `val_biblioteca`, `val_hospital`, sus preguntas ni sus resultados para entrenar, para few-shot ni para crear datos. La pérdida dev casi nula indica memorización de plantillas; no estima la generalización a la evaluación oculta.


## Preparación B disponible

Usar `notebooks/05_lora_b_t4.ipynb`, que reutiliza la instalación MySQL verificada del notebook 04. Hipótesis: `entrenamiento/lora_b.json`; debe publicarse antes de entrenar. El ZIP `lora_b_t4.zip` incluirá B y las dos evaluaciones, manteniendo A como adapter vigente hasta revisar la comparación. Tras integrar el ZIP, completar selección y experimento de inferencia antes del relevo a Angel. La preparación del notebook no representa una corrida T4 realizada.
