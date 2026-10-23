# Adapter LoRA A

Adapter LoRA entrenado por la pareja sobre `Qwen/Qwen2.5-Coder-1.5B-Instruct` (Apache-2.0) para generar consultas MySQL 8.4.10 a partir de un esquema `SHOW CREATE TABLE` y una pregunta en español. Lo carga `solucion.py` cuando `config.json` tiene `"usar_adapter": true`.

- Configuración: `entrenamiento/lora_a.json`, con r=8, alpha 16, dropout 0.05 y los módulos q, k, v, o, gate, up y down. Una época, LR 2e-4 coseno, lote efectivo 16, fp16 y semilla 2026.
- Datos: 3,230 pares sintéticos propios de 15 esquemas de entrenamiento y 170 de dev. No incluye los esquemas ni las preguntas de validación.
- Métricas y curvas: `resultados/entrenamientos/lora_a/`. Evaluación: `resultados/evaluaciones/lora_a/`.
- Entrenado en Colab con Tesla T4, peft 0.18.1 y transformers 5.20.2.
