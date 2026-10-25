# Predicción de EX en la evaluación oculta

Turno 4, Angel Herrarte, con asistencia de IA. Esto es una **estimación**, no una medición: no conocemos las bases ni las preguntas ocultas, y no usamos el conjunto reservado para entrenar ni para ajustar el prompt. Los números medidos vienen de `resultados/analisis_errores.json` y de `resultados/auditoria_final_t4.json`.

## Predicción

| | Estimación puntual | Rango probable |
| --- | ---: | ---: |
| **EX con adapter (A, entrega)** | **0.60** | 0.50 – 0.68 |
| EX sin adapter (base) | 0.48 | 0.40 – 0.56 |
| Mejora del adapter | +0.12 | +0.05 – +0.18 |

Vemos poco probable alcanzar 0.70 en la evaluación oculta y esperamos una mejora algo menor que 0.15.

## Punto de partida medido

- La entrega obtuvo **EX = 0.6974 (53/76)** en la validación propia, y el base 0.5658. Los resultados son deterministas y no se pasó ningún límite de tiempo.
- Acierto de A por nivel: fácil 14/14 (100 %), media 12/16 (75 %), difícil 5/10 (50 %). El base: 14/14, 10/16 y 3/10.
- La incertidumbre por muestra es grande. Un bootstrap de las 40 preguntas (10,000 remuestreos, semilla 2026) da un intervalo del 95 % de **0.54 – 0.86** para A y de **0.00 – 0.28** para la mejora sobre el base.

## Ajustes respecto a la validación

1. **Composición por dificultad (−0.03 a −0.05).** La validación tiene 14 fáciles, 16 medias y 10 difíciles. Aplicamos los aciertos medidos por nivel a otras mezclas posibles de 30 a 40 preguntas:
   - Tercios iguales: 0.667.
   - Con más difíciles (12/14/14): 0.659.
   - Con 10/15/15: 0.647.
   
   Las difíciles pesan 3, así que cada una que se añade baja el EX esperado.
2. **Cambio de dominio en los nombres (−0.03 a −0.06).** El enunciado avisa que los nombres pueden estar en inglés o abreviados. Los 15 esquemas de entrenamiento y los 2 de validación usan nombres completos en español. El error principal de A ya es el de relaciones y columnas: un JOIN saltado o una columna inventada (7 de sus 9 fallos). Es de esperar que empeore con nombres menos descriptivos.
3. **Tamaño de los esquemas (−0.01 a −0.03).** Las bases ocultas tienen de 5 a 10 tablas. Las nuestras tienen 6, así que habrá más caminos de JOIN posibles en los esquemas grandes.
4. **Preguntas difíciles con fechas (incierto).** Solo 2 de nuestras 40 referencias usan funciones de fecha. El entrenamiento sí tiene 160 pares con fechas, pero la validación no mide bien esa habilidad.
5. **Redacción de las preguntas (−0.01 a −0.03).** Nuestras preguntas incluyen aclaraciones como «libro significa título bibliográfico» o «incluye ceros». Si las ocultas son menos explícitas, crecen los errores de filtro y de LEFT JOIN, como en `propia_35`. Además, la validación la escribió el mismo equipo que diseñó los datos de entrenamiento, y la pérdida de validación del entrenamiento fue muy baja. Puede haber cierta memorización de plantillas que favorece a nuestra validación.

Sumando los ajustes 1, 2, 3 y 5, A baja de 0.70 a un rango aproximado de **0.53 – 0.62**. Tomamos **0.60** como estimación central y ampliamos el rango a 0.50 – 0.68 por el ruido de muestreo.

## Mejora sobre el base

- La mejora medida (+0.13) viene sobre todo de la agregación. El base usa `COUNT(*)` con `LEFT JOIN` y arma `GROUP BY` incompatibles con `ONLY_FULL_GROUP_BY`. Estos errores no dependen del dominio, así que deberían repetirse en las bases ocultas.
- Los ajustes 2 y 3 afectan a ambos modelos.
- Por eso esperamos que la mejora se mantenga positiva, aunque cerca de +0.12. En la validación, el bootstrap incluye el 0 en su extremo inferior.

## Qué invalidaría esta estimación

- Si las bases ocultas se parecen mucho a las nuestras (nombres en español y pocas tablas), el resultado debería acercarse a 0.70.
- Si predominan los nombres abreviados en inglés y los JOIN de tres o más tablas, podría quedar por debajo de 0.50.
