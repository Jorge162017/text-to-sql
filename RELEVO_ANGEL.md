# Relevo del turno 1 de Jorge al turno 2 de Angel

La implementación de datos quedó revisada técnicamente con asistencia de IA. Jorge autorizó publicar esta implementación en los tres commits acordados; consultar el historial de Git. El plan en `Instrucciones/` permanece fijo.

## Lo que recibe Angel

- **3,400 pares aceptados** en `datos/entrenamiento/pares.jsonl`, con pregunta en español, SQL y DDL real de MySQL incluidos.
- **15 esquemas propios**, seis tablas por esquema y seis topologías distintas. Hay 66 familias: 940 fáciles, 1,400 medios y 1,060 difíciles. Todos se ejecutan en MySQL 8.4.10; cero descartes.
- **40 referencias propias** en `datos/validacion/pares.jsonl`: 20 sobre biblioteca y 20 sobre hospital, con columnas, orden, dificultad y peso. Total de pesos: **76**. Los originales y autores declarados se preservan en `preguntas_propias.jsonl`.
- SQL, datos de prueba, SHOW CREATE TABLE, notebook, procedencia, evidencia completa y pruebas de integridad.
- Revisión automática de los **3,440 resultados** mediante cálculos Python independientes y auditoría de hashes; no se afirma revisión humana no realizada ni desempeño del modelo.

## Comprobación rápida

Desde el repositorio, seguir el README para preparar Python y MySQL. Si las bases aún no existen:

```bash
python -m scripts.validar_datos --inicializar
python -m scripts.revisar_muestra
python -m scripts.auditar_datos --exigir-cierre
python -m unittest discover -s tests -v
```

Si ya existen, omitir `--inicializar`. Si cambian DDL/semillas, reconstruir únicamente el servidor sintético con `--inicializar --recrear`. No editar ni regenerar datos durante la comparación baseline/A/B salvo un fallo documentado que obligue a repetir las mediciones afectadas.

## Alcance del turno de Angel

1. Implementar `solucion.py`, `config.json`, carga compatible con T4 y `generar_sql(esquema, pregunta, ejecutar=None)`. Modelo propuesto: `Qwen/Qwen2.5-Coder-1.5B-Instruct`. Agregar dependencias y licencia del modelo al incorporarlo.
2. Construir el evaluador por ejecución: pesos 1/2/3, filas duplicadas conservadas, orden solo si se exige, números a dos decimales y regla de columna adicional del enunciado. `referencias_resultados.jsonl` es evidencia; las referencias pueden reejecutarse contra la base correspondiente.
3. Ejecutar baseline sin adapter sobre las cuarenta preguntas y guardar EX global, por nivel, errores y tiempos. El denominador esperado de EX es **76**.
4. Registrar hipótesis A **antes** de entrenar, congelar prompt/configuración y entrenar LoRA A. Guardar parámetros entrenables, tiempo, curvas y evaluación. Entregar a Jorge la configuración completa para que la B cambie solo un factor.
5. Verificar T4, determinismo, límites de carga/generación, funcionamiento sin callback y SQL de solo lectura. Crear sus propios commits y entradas reales de bitácora desde su cuenta.

## Datos reservados y límites

No incluir en entrenamiento, few-shot ni síntesis de nuevos pares los archivos o esquemas `val_biblioteca` y `val_hospital`. Las preguntas originales se recibieron con autoría declarada por Jorge; el SQL y las precisiones tienen asistencia de IA.

El conjunto sintético es reproducible, pero el rendimiento real y la generalización todavía son desconocidos. Los diez dominios comerciales comparten estructura; se añadieron cinco grafos distintos para reducir esa limitación. La validación propia usa solo dos esquemas, como mínimo del curso.

## Publicación y accesos

Jorge autorizó los commits y la subida. Se distribuye el turno en tres commits coherentes: entorno; datos de entrenamiento; validación propia y cierre. Confirmar repositorio privado, acceso del docente y de Angel. Esas condiciones externas no se dan por verificadas por la auditoría de datos. No inventar horas humanas, fechas ni aportes anteriores; el requisito histórico de dos semanas no se puede reconstruir retroactivamente.
