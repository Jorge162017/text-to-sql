# Análisis de errores — validación propia

Turno 4, Angel Herrarte, con asistencia de IA. Fuente: `resultados/validacion_propia.csv`, con 200 filas: 5 configuraciones × 40 preguntas. Lo genera `python -m evaluacion.consolidar` a partir de las predicciones guardadas y de la clasificación manual `resultados/clasificacion_errores.json`. Los conteos están en `resultados/analisis_errores.json`. Son resultados sobre la validación propia (2 esquemas, 40 preguntas, peso 76), no sobre el conjunto oculto.

## Regla de clasificación

- **La consulta falla al ejecutarse.** Manda el error de MySQL:
  - 1064, o una construcción no soportada (1235): **sintaxis**.
  - 1054 o 1146: **columna/tabla inexistente**.
  - 1055, 1111 o 1247: **agregación**.
- **La consulta se ejecuta pero el resultado difiere.** Se asigna la primera causa estructural, en este orden:
  1. **JOIN**: tablas o tipo de unión incorrectos.
  2. **Agregación**: conteo, agrupación o selección por grupo.
  3. **Filtro**: condición de más o de menos.
  4. **Resultado distinto**: el resto.
- Las causas secundarias quedan en la columna `causa` del CSV.

## Resultados por configuración

| Configuración | EX | Fácil (14) | Media (32) | Difícil (30) | Biblioteca (37) | Hospital (39) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Base directa | 43/76 = 0.5658 | 14 | 20 | 9 | 21 | 22 |
| **A directa (entrega)** | **53/76 = 0.6974** | **14** | **24** | **15** | **24** | **29** |
| B directa | 49/76 = 0.6447 | 14 | 26 | 9 | 26 | 23 |
| Base con corrección | 48/76 = 0.6316 | 14 | 22 | 12 | 24 | 24 |
| A con corrección | 53/76 = 0.6974 | 14 | 24 | 15 | 24 | 29 |

Por nivel y esquema se muestran los pesos acertados. Por preguntas, A acierta 14/14 fáciles, 12/16 medias y 5/10 difíciles.

## Fallos por categoría (preguntas / peso perdido)

| Configuración | Sintaxis | Columna/tabla | JOIN | Agregación | Filtro | Resultado distinto | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Base directa | 1 / 3 | 3 / 7 | 2 / 4 | 6 / 16 | 1 / 3 | 0 | 13 / 33 |
| **A directa** | 0 | 3 / 8 | **4 / 9** | 2 / 6 | 0 | 0 | **9 / 23** |
| B directa | 0 | 5 / 14 | 4 / 10 | 1 / 3 | 0 | 0 | 10 / 27 |
| Base con corrección | 0 | 3 / 8 | 2 / 4 | 5 / 13 | 1 / 3 | 0 | 11 / 28 |
| A con corrección | 0 | 3 / 8 | 4 / 9 | 2 / 6 | 0 | 0 | 9 / 23 |

## Patrones

1. **El fine-tuning corrige sobre todo la agregación.** La agregación pasa de 6 fallos en el base a 2 en A. El base usa `COUNT(*)` con `LEFT JOIN`, que cuenta 1 en lugar de 0 (`propia_15`, `propia_25`), y arma `GROUP BY` que rompen `ONLY_FULL_GROUP_BY` (`propia_20`, `propia_30`, `propia_40`). A usa `COUNT(col)` y agrupa todas las columnas no agregadas, como en sus datos de entrenamiento. Los errores de sintaxis desaparecen.
2. **El error dominante de A es el JOIN por relaciones indirectas.** En biblioteca, `prestamos` apunta a `ejemplares` y `ejemplares` a `titulos`. A une `prestamos.ejemplar_id = titulos.id` y se salta `ejemplares` (`propia_07`, `propia_17`, `propia_18`). En `propia_20` supone una columna `prestamos.titulo_id` que no existe. Son 4 de sus 9 fallos. El esquema de validación distingue «título» de «ejemplar», y el modelo no siguió esa cadena de llaves foráneas.
3. **Columnas inventadas cuando el dato está en otra tabla.** En `propia_23`, base, A y B piden `medicos.especialidad` en vez de unir `especialidades`. Pasa lo mismo con `cita_id` y `titulo_id` en B (`propia_10`, `propia_30`, `propia_40`). B (r=16) tiene más errores de este tipo: 5 frente a 3 de A. Es consistente con su menor EX en preguntas difíciles (9 frente a 15).
4. **JOIN interno donde se pedía conservar ceros.** En `propia_35` todas las configuraciones usan `JOIN` y un filtro en `WHERE`, cuando hacía falta `LEFT JOIN ... AND estado = 'atendida'`. Así excluyen al médico sin pacientes, y además no cuentan pacientes distintos.
5. **Promedio de conteos (`propia_29`).** Ninguna configuración lo resuelve. A anida `AVG(COUNT(...))`, que MySQL rechaza con el error 1111. Hace falta un CTE de conteos.
6. **La corrección solo ayuda a quien comete errores de ejecución.** En el base recupera `propia_10` y `propia_23` (+5). En A los fallos que quedan son casi todos semánticos: la consulta se ejecuta pero responde otra cosa, y el callback solo detecta errores de MySQL. Por eso no cambia el EX. Las reparaciones de `propia_20` y `propia_30` en A siguen fallando.

## Lectura de los conteos

- Los 23 puntos que A no obtiene se concentran en preguntas difíciles (15 de 30) y en relaciones de varios saltos. Ninguno se debe al formato de salida ni a los límites: no hubo consultas neutras, todas fueron de lectura y la latencia máxima fue de 5.33 s.
- Una sola pregunta puede tener varias causas. La categoría registra la que se corregiría primero; la columna `causa` registra las demás.
- Con 40 preguntas y dos esquemas, una pregunta difícil vale 3/76 ≈ 0.039 de EX. Las diferencias entre configuraciones de una o dos preguntas no deben generalizarse.
