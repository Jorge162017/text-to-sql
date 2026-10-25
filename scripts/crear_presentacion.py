"""Genera presentacion.pdf (12 diapositivas 16:9) a partir de los resultados versionados.

Las cifras se leen de resultados/*.json; el texto interpretativo resume ANALISIS_ERRORES.md
y PREDICCION_EX_OCULTO.md. Requiere Google Chrome para imprimir el HTML a PDF.

    python -m scripts.crear_presentacion
"""
import json
import subprocess
import tempfile
from pathlib import Path

from scripts.comun import ROOT

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
RES = ROOT / 'resultados'


def leer(ruta):
    return json.loads((RES / ruta).read_text(encoding='utf-8'))


def pct(x):
    return f'{x:.4f}'.rstrip('0').rstrip('.') if x is not None else '—'


def barras(filas, maximo=76):
    """filas: (etiqueta, valor, destacado)."""
    html = ''
    for etiqueta, valor, destacado in filas:
        ancho = 100 * valor / maximo
        html += (f'<div class="barra"><span class="et">{etiqueta}</span>'
                 f'<span class="pista"><span class="relleno{" acento" if destacado else ""}" style="width:{ancho:.1f}%"></span></span>'
                 f'<span class="val">{valor}/76 · {valor / maximo:.4f}</span></div>')
    return html


def diapositivas():
    analisis = leer('analisis_errores.json')['analisis']
    auditoria = leer('auditoria_final_t4.json')
    datos = leer('reporte_datos.json')
    ma, mb = leer('entrenamientos/lora_a/metricas.json'), leer('entrenamientos/lora_b/metricas.json')
    inf = {n: leer(f'evaluaciones/{n}/resumen.json') for n in
           ['inferencia_base_directa', 'inferencia_base_correccion', 'inferencia_a_directa', 'inferencia_a_correccion']}
    base, a, b = analisis['base'], analisis['a'], analisis['b']
    nivel = lambda x, n: x['por_nivel'][n]['peso_aciertos']
    preg = lambda x, n: f"{x['por_nivel'][n]['aciertos']}/{x['por_nivel'][n]['preguntas']}"
    ca = auditoria['corridas']['auditoria_final_a']
    contrato = auditoria['contrato']
    lora = ma['config']['lora']
    ent = ma['config']['entrenamiento']
    cats = ['sintaxis', 'columna_tabla_inexistente', 'join', 'agregacion', 'filtro', 'resultado_distinto']
    nombres_cat = ['Sintaxis', 'Columna/tabla inexistente', 'JOIN', 'Agregación', 'Filtro', 'Resultado distinto']

    def fila_cat(x):
        return ''.join(f'<td>{x["categorias"].get(c, 0)}</td>' for c in cats) + f'<td><b>{x["fallos"]}</b></td>'

    s = []
    s.append(('Texto a SQL en español con LoRA', f'''
<p class="sub">Qwen/Qwen2.5-Coder-1.5B-Instruct + adapter LoRA · MySQL 8.4.10 · Colab T4</p>
<p class="autores">Jorge Lopez · Angel Herrarte</p>
<div class="kpis">
  <div class="kpi"><b>{pct(a["ex"])}</b><span>EX con adapter A<br>(validación propia, 53/76)</span></div>
  <div class="kpi"><b>{pct(base["ex"])}</b><span>EX modelo base<br>(mismo prompt, 43/76)</span></div>
  <div class="kpi acento"><b>+{a["ex"] - base["ex"]:.4f}</b><span>aporte del fine-tuning<br>(10/76)</span></div>
</div>
<p class="nota"><b>Objetivo:</b> dado el esquema de una base (SHOW CREATE TABLE con comentarios) y una pregunta en español,
generar una consulta MySQL correcta por ejecución. Las cifras son sobre nuestra validación propia, no sobre la evaluación oculta.</p>'''))

    s.append(('Contrato de la entrega', f'''
<div class="cols">
<div><pre>def generar_sql(esquema: str, pregunta: str,
               ejecutar=None) -&gt; str</pre>
<ul>
<li><code>config.json</code>: modelo base, <code>adapter/</code>, <code>usar_adapter: true</code>, semilla 2026.</li>
<li>Prompt congelado v1; generación <b>greedy</b> (<code>do_sample=False</code>, 320 tokens).</li>
<li>Filtro de solo lectura: una sola sentencia SELECT/WITH; cualquier otra salida se reemplaza por <code>SELECT 1</code>.</li>
<li>Estrategia entregada: <b>directa</b>, 0 de 3 llamadas a <code>ejecutar</code>. Con o sin callback la salida es idéntica.</li>
<li>Revisión del modelo fijada en Hugging Face (<code>2e1fd39</code>).</li>
</ul></div>
<div><table class="t">
<tr><th>Límite (auditoría Colab T4 limpio)</th><th>Medido</th></tr>
<tr><td>Carga ≤ 300 s (<code>import solucion</code>)</td><td>{contrato["tiempo_import_s"]} s</td></tr>
<tr><td>≤ 30 s por pregunta</td><td>máx. {ca["latencia_s"]["max"]} s · media {ca["latencia_s"]["media"]} s</td></tr>
<tr><td>Determinismo (2 corridas)</td><td>40/40 idénticas</td></tr>
<tr><td>Solo lectura</td><td>40/40 SELECT/WITH</td></tr>
<tr><td>Callback</td><td>0 llamadas · mismas salidas</td></tr>
<tr><td>Petición de borrado</td><td><code>SELECT 1</code></td></tr>
</table></div></div>'''))

    s.append(('Datos de entrenamiento y procedencia', f'''
<div class="kpis">
  <div class="kpi"><b>{datos["aceptados_entrenamiento"]:,}</b><span>pares pregunta–SQL aceptados</span></div>
  <div class="kpi"><b>15</b><span>esquemas propios<br>de 6 tablas</span></div>
  <div class="kpi"><b>{datos["familias_plantillas"]}</b><span>familias de plantillas</span></div>
  <div class="kpi"><b>{datos["descartados_entrenamiento"]}</b><span>descartes: todos ejecutan<br>en MySQL 8.4.10</span></div>
</div>
<ul>
<li>Por nivel: {datos["por_nivel"]["facil"]} fáciles · {datos["por_nivel"]["media"]} medias · {datos["por_nivel"]["dificil"]} difíciles. Cubren JOIN, LEFT JOIN con ceros, HAVING, subconsultas, NOT EXISTS, CTE, ventanas y fechas.</li>
<li>Sintéticos, diseñados con asistencia de IA: DDL con comentarios, semillas reproducibles y plantillas en español. No se usaron datasets externos (Spider/BIRD) ni datos personales reales.</li>
<li>Cada SQL se certificó ejecutándolo en MySQL 8.4.10 con <code>ONLY_FULL_GROUP_BY</code> y se contrastó con algoritmos Python independientes. {datos["resultados_vacios"]} pares devuelven un resultado vacío válido.</li>
<li><b>Limitación:</b> hay seis topologías de llaves foráneas y los nombres son siempre en español y completos, así que la diversidad estructural es menor que el número de esquemas.</li>
</ul>'''))

    s.append(('Validación propia y evaluador', f'''
<div class="cols">
<div><ul>
<li>Dos esquemas reservados que no aparecen en entrenamiento: <code>val_biblioteca</code> y <code>val_hospital</code>. La partición es por esquema.</li>
<li>40 preguntas escritas por la pareja, 20 cada integrante.</li>
<li>14 fáciles (peso 1), 16 medias (peso 2) y 10 difíciles (peso 3): <b>peso total 76</b>.</li>
<li>Comprobado: 0 esquemas, preguntas o SQL compartidos con el entrenamiento. Nunca se usaron para entrenar ni como few-shot.</li>
</ul></div>
<div><ul>
<li><b>EX por ejecución</b>, como el enunciado: comparación de resultados como multiconjunto, orden solo si se pide, redondeo a 2 decimales, columnas extra permitidas.</li>
<li>Usuario MySQL temporal con solo <code>SELECT</code>, transacción <code>READ ONLY</code>, 10 s por consulta.</li>
<li>Callback como el del docente: máximo 3 llamadas y 10 filas.</li>
<li>Control con oráculo: las referencias dan <b>76/76</b> en cada sesión.</li>
<li>Resultado por pregunta en <code>resultados/validacion_propia.csv</code>.</li>
</ul></div></div>'''))

    s.append(('Baseline: modelo sin adapter', f'''
<div class="kpis">
  <div class="kpi"><b>{pct(base["ex"])}</b><span>EX ponderada (43/76)</span></div>
  <div class="kpi"><b>{preg(base, "facil")}</b><span>fáciles</span></div>
  <div class="kpi"><b>{preg(base, "media")}</b><span>medias ({nivel(base, "media")}/32 pts)</span></div>
  <div class="kpi"><b>{preg(base, "dificil")}</b><span>difíciles ({nivel(base, "dificil")}/30 pts)</span></div>
</div>
<ul>
<li>Mismo prompt, generación y evaluador que el adapter; solo cambia <code>usar_adapter: false</code>. Determinista 40/40.</li>
<li>El base resuelve bien las preguntas de una tabla y falla en las de varias tablas: {base["fallos"]} fallos, {base["categorias"].get("agregacion", 0)} de ellos de agregación.</li>
<li>Errores típicos: <code>COUNT(*)</code> con <code>LEFT JOIN</code> (cuenta 1 en lugar de 0), <code>GROUP BY</code> rechazado por <code>ONLY_FULL_GROUP_BY</code>, columnas inventadas y una subconsulta con <code>LIMIT</code> que MySQL no admite.</li>
<li>Estos patrones orientaron la hipótesis de LoRA A.</li>
</ul>'''))

    s.append(('Hipótesis previas: dos LoRA que difieren en un factor', f'''
<table class="t ancha">
<tr><th></th><th>LoRA A</th><th>LoRA B</th></tr>
<tr><td>Factor</td><td><b>r = 8</b></td><td><b>r = 16</b> (único cambio; alpha/r pasa de 2 a 1)</td></tr>
<tr><td>Parámetros entrenables</td><td>{ma["parametros_entrenables"]:,} ({ma["porcentaje_entrenable"]} %)</td><td>{mb["parametros_entrenables"]:,} ({mb["porcentaje_entrenable"]} %)</td></tr>
<tr><td>Hipótesis escrita antes de entrenar</td><td>Aprende LEFT JOIN con COUNT(col), ROW_NUMBER por grupo y GROUP BY válido: <b>EX ≥ 0.72</b></td><td>Más capacidad mejora las consultas complejas: <b>EX ≥ 56/76 = 0.7368</b></td></tr>
<tr><td>Resultado</td><td>0.6974: no se cumplió, aunque mejora +0.13</td><td>0.6447: no se cumplió, queda por debajo de A</td></tr>
</table>
<p class="nota">Comunes: alpha {lora["lora_alpha"]}, dropout {lora["lora_dropout"]}, módulos q/k/v/o/gate/up/down · {ent["epocas"]} época · lr {ent["tasa_aprendizaje"]} coseno con {ent["pasos_calentamiento"]} pasos de calentamiento · batch {ent["batch_por_dispositivo"]}×{ent["acumulacion_gradiente"]} · fp16 · pérdida solo sobre el SQL de respuesta · {ma["ejemplos_entrenamiento"]:,} ejemplos de entrenamiento y {ma["ejemplos_dev"]} de dev. Las hipótesis se publicaron en commits anteriores al entrenamiento.</p>'''))

    s.append(('Entrenamiento y curvas de pérdida', f'''
<div class="cols imgs">
<figure><img src="{(RES / 'entrenamientos/lora_a/curvas_loss.png').as_uri()}"><figcaption>A (r=8): {ma["tiempo_entrenamiento_s"]:.0f} s en T4 · {ma["pasos"]} pasos · pico {ma["memoria_pico_gib"]} GiB</figcaption></figure>
<figure><img src="{(RES / 'entrenamientos/lora_b/curvas_loss.png').as_uri()}"><figcaption>B (r=16): {mb["tiempo_entrenamiento_s"]:.0f} s en T4 · {mb["pasos"]} pasos · pico {mb["memoria_pico_gib"]} GiB</figcaption></figure>
</div>
<p class="nota">Pérdida de dev: de {ma["eval_loss_inicial"]:.3f} a {ma["eval_loss_final"]:.4f} (A) y {mb["eval_loss_final"]:.4f} (B). Una pérdida tan baja en un dev de los mismos esquemas sugiere memorización de plantillas: B tiene menor pérdida pero peor EX, así que la pérdida no sirvió para elegir el adapter.</p>'''))

    s.append(('Comparación: base, A y B', f'''
<div class="cols">
<div>{barras([("Base", base["peso_aciertos"], False), ("LoRA A (r=8)", a["peso_aciertos"], True), ("LoRA B (r=16)", b["peso_aciertos"], False)])}</div>
<div><table class="t">
<tr><th>Puntos por nivel</th><th>Base</th><th>A</th><th>B</th></tr>
<tr><td>Fácil (14)</td><td>{nivel(base, "facil")}</td><td>{nivel(a, "facil")}</td><td>{nivel(b, "facil")}</td></tr>
<tr><td>Media (32)</td><td>{nivel(base, "media")}</td><td>{nivel(a, "media")}</td><td>{nivel(b, "media")}</td></tr>
<tr><td>Difícil (30)</td><td>{nivel(base, "dificil")}</td><td><b>{nivel(a, "dificil")}</b></td><td>{nivel(b, "dificil")}</td></tr>
</table></div></div>
<ul>
<li><b>Se entrega A</b> por su mayor EX y menor memoria. B gana en medias pero cae en difíciles: inventa más columnas (5 frente a 3).</li>
<li>Todas las corridas son deterministas. Base y A se reprodujeron 40/40 en la auditoría final desde un Colab limpio.</li>
</ul>'''))

    fila_inf = lambda n, et, des=False: (f'<tr{" class=sel" if des else ""}><td>{et}</td><td>{inf[n]["peso_aciertos"]}/76 · {pct(inf[n]["ex"])}</td>'
                                        f'<td>{inf[n]["latencia_s"]["media"]} s</td><td>{inf[n]["latencia_s"]["max"]} s</td>'
                                        f'<td>{inf[n]["llamadas_ejecutar"]["max_por_pregunta"]}</td></tr>')
    s.append(('Experimento de inferencia: corrección con ejecutar', f'''
<p class="nota"><b>Hipótesis previa:</b> devolver al modelo el error de MySQL recupera al menos una pregunta de A. Control: generación directa. Tratamiento: hasta 3 llamadas y 2 reparaciones, con el mismo primer intento, los mismos pesos y el mismo prompt.</p>
<table class="t ancha">
<tr><th>Configuración</th><th>EX</th><th>Latencia media</th><th>Latencia máx.</th><th>Máx. callbacks</th></tr>
{fila_inf("inferencia_base_directa", "Base · directa")}
{fila_inf("inferencia_base_correccion", "Base · corrección")}
{fila_inf("inferencia_a_directa", "A · directa (entrega)", True)}
{fila_inf("inferencia_a_correccion", "A · corrección")}
</table>
<ul>
<li>La corrección recupera 2 preguntas del base (+5 puntos) y <b>ninguna de A</b>: la hipótesis no se cumple.</li>
<li>Los fallos que quedan en A se ejecutan pero responden otra cosa, y el callback no detecta ese tipo de error. Con el empate se aplica la regla previa: <b>directa</b>, que además es más rápida.</li>
</ul>'''))

    s.append(('Análisis de errores por categoría', f'''
<table class="t ancha">
<tr><th>Fallos (preguntas)</th>{"".join(f"<th>{c}</th>" for c in nombres_cat)}<th>Total</th></tr>
<tr><td>Base</td>{fila_cat(base)}</tr>
<tr class="sel"><td>A (entrega)</td>{fila_cat(a)}</tr>
<tr><td>B</td>{fila_cat(b)}</tr>
</table>
<ul>
<li><b>Lo que corrige el fine-tuning:</b> la agregación pasa de 6 a 2 fallos (COUNT(col) con LEFT JOIN, GROUP BY válido) y desaparecen los errores de sintaxis.</li>
<li><b>Lo que queda en A:</b> relaciones indirectas. Une préstamo con título y se salta <code>ejemplares</code> (propia_07, 17, 18), o inventa <code>medicos.especialidad</code> en lugar de unir <code>especialidades</code> (propia_23).</li>
<li>Ninguna configuración resuelve el promedio de conteos (propia_29) ni conservar médicos con cero pacientes (propia_35).</li>
<li>Regla: si la consulta da error, manda el código MySQL. Si se ejecuta, se asigna la primera causa en el orden JOIN, agregación, filtro, resultado distinto.</li>
</ul>'''))

    s.append(('Predicción de EX en la evaluación oculta', f'''
<div class="kpis">
  <div class="kpi acento"><b>0.60</b><span>EX con adapter<br>rango 0.50 – 0.68</span></div>
  <div class="kpi"><b>0.48</b><span>EX sin adapter<br>rango 0.40 – 0.56</span></div>
  <div class="kpi"><b>+0.12</b><span>mejora esperada<br>rango +0.05 – +0.18</span></div>
</div>
<ul>
<li><b>Punto de partida medido:</b> 0.6974, con un bootstrap del 95 % de 0.54 a 0.86 (40 preguntas, 2 esquemas).</li>
<li><b>Composición:</b> con más preguntas difíciles (peso 3), los aciertos por nivel (100 / 75 / 50 %) dan entre 0.65 y 0.67.</li>
<li><b>Cambio de dominio:</b> las bases ocultas pueden tener nombres en inglés o abreviados y de 5 a 10 tablas, cuando las nuestras tienen 6 y nombres en español. Esto afecta justo al error principal de A, el de JOIN y columnas (7 de 9 fallos).</li>
<li><b>Redacción:</b> nuestras preguntas incluyen aclaraciones, y las fechas casi no se miden en la validación.</li>
<li>Es una estimación, no una medición. No esperamos llegar a 0.70.</li>
</ul>'''))

    s.append(('Reproducibilidad, contribuciones y límites', f'''
<div class="cols">
<div><h3>Reproducibilidad</h3><ul>
<li>Notebooks 01–07 (datos, baseline, LoRA A/B, experimento y auditoría). La auditoría final, en un Colab T4 limpio con solo <code>requirements.txt</code>, reprodujo base y A.</li>
<li>Configuración congelada con hashes. Las corridas no se sobrescriben.</li>
<li>Los resultados de Colab que se comparan se auditaron volviendo a ejecutar sus predicciones en MySQL local; en la auditoría final, 200 predicciones sin ninguna diferencia.</li>
<li>Python 3.13.16 · torch {auditoria["entorno"]["torch"]} · transformers {auditoria["entorno"]["transformers"]} · peft {auditoria["entorno"]["peft"]}.</li>
</ul>
<h3>Límites</h3><ul>
<li>Datos generados por plantillas y validación pequeña (40 preguntas, 2 esquemas).</li>
<li>Ninguna de las tres hipótesis cuantitativas se cumplió. Se reportan tal cual.</li>
</ul></div>
<div><h3>Contribuciones</h3><table class="t">
<tr><th>Turno</th><th>Trabajo</th></tr>
<tr><td>1 · Jorge Lopez</td><td>15 esquemas, 3,400 pares, certificación MySQL, esquemas reservados</td></tr>
<tr><td>2 · Angel Herrarte</td><td>Contrato, evaluador, baseline, hipótesis y entrenamiento de LoRA A</td></tr>
<tr><td>3 · Jorge Lopez</td><td>LoRA B, experimento de corrección, selección final</td></tr>
<tr><td>4 · Angel Herrarte</td><td>Auditoría en Colab limpio, CSV, errores, predicción, entrega</td></tr>
<tr><td>Ambos</td><td>40 preguntas de validación (20 cada uno)</td></tr>
</table>
<p class="nota">Uso de IA declarado: asistencia en diseño de datos, código, revisión y redacción. Detalle en <code>BITACORA.md</code> y <code>CONTRIBUCIONES.md</code>.</p></div>
</div>'''))
    return s


CSS = '''
@page { size: 13.333in 7.5in; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif; color: #1c2430; }
.slide { width: 13.333in; height: 7.5in; padding: 0.55in 0.7in 0.45in; position: relative; page-break-after: always;
         overflow: hidden; background: #ffffff; }
.slide:last-child { page-break-after: auto; }
.slide::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 0.14in; background: #1f6f78; }
h2 { font-size: 30pt; margin: 0 0 0.25in; color: #12343b; letter-spacing: -0.3pt; }
h1 { font-size: 42pt; margin: 0.7in 0 0.15in; color: #12343b; letter-spacing: -0.5pt; }
h3 { font-size: 15pt; margin: 0 0 6pt; color: #1f6f78; }
.num { position: absolute; right: 0.6in; bottom: 0.3in; font-size: 10pt; color: #7a8794; }
.pie { position: absolute; left: 0.7in; bottom: 0.3in; font-size: 10pt; color: #7a8794; }
.sub { font-size: 17pt; color: #44515e; margin: 0 0 6pt; }
.autores { font-size: 15pt; color: #1f6f78; font-weight: 600; margin: 0 0 0.35in; }
ul { margin: 0.1in 0 0; padding-left: 0.25in; font-size: 14.5pt; line-height: 1.38; }
li { margin-bottom: 6pt; }
.nota { font-size: 13pt; color: #44515e; line-height: 1.4; margin: 0.15in 0 0; }
code, pre { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 0.88em; background: #eef3f4; border-radius: 3px; padding: 0 3px; }
pre { font-size: 13pt; padding: 10pt 12pt; margin: 0 0 6pt; line-height: 1.35; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 0.45in; align-items: start; }
.kpis { display: flex; gap: 0.25in; margin: 0.05in 0 0.2in; }
.kpi { flex: 1; border: 1px solid #d5dee2; border-radius: 8px; padding: 12pt 14pt; background: #f7fafb; }
.kpi b { display: block; font-size: 30pt; color: #12343b; letter-spacing: -0.5pt; }
.kpi span { font-size: 12pt; color: #44515e; line-height: 1.3; }
.kpi.acento { background: #1f6f78; border-color: #1f6f78; }
.kpi.acento b, .kpi.acento span { color: #ffffff; }
table.t { border-collapse: collapse; font-size: 13pt; width: 100%; }
table.t th { text-align: left; background: #12343b; color: #fff; padding: 6pt 9pt; font-weight: 600; }
table.t td { padding: 6pt 9pt; border-bottom: 1px solid #d5dee2; vertical-align: top; }
table.t tr.sel td { background: #e3f1f2; font-weight: 600; }
table.ancha th:not(:first-child), table.ancha td:not(:first-child) { text-align: left; }
.barra { display: grid; grid-template-columns: 1.5in 1fr 1.7in; align-items: center; gap: 10pt; margin: 14pt 0; font-size: 14pt; }
.pista { background: #eef3f4; height: 26pt; border-radius: 4px; overflow: hidden; }
.relleno { display: block; height: 100%; background: #9fb6bd; }
.relleno.acento { background: #1f6f78; }
.val { font-variant-numeric: tabular-nums; color: #12343b; font-weight: 600; }
.imgs figure { margin: 0; }
.imgs img { width: 100%; border: 1px solid #d5dee2; border-radius: 6px; }
figcaption { font-size: 12pt; color: #44515e; margin-top: 4pt; }
'''


def main():
    s = diapositivas()
    if len(s) > 12:
        raise SystemExit(f'{len(s)} diapositivas; el máximo es 12')
    partes = []
    for i, (titulo, cuerpo) in enumerate(s, 1):
        encabezado = f'<h1>{titulo}</h1>' if i == 1 else f'<h2>{titulo}</h2>'
        partes.append(f'<section class="slide">{encabezado}{cuerpo}'
                      f'<div class="pie">Proyecto 3 · Texto a SQL</div><div class="num">{i}/{len(s)}</div></section>')
    html = f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(partes)}</body></html>'
    salida = ROOT / 'presentacion.pdf'
    with tempfile.TemporaryDirectory() as tmp:
        pagina = Path(tmp) / 'presentacion.html'
        pagina.write_text(html, encoding='utf-8')
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--allow-file-access-from-files',
                        f'--print-to-pdf={salida}', pagina.as_uri()], check=True, capture_output=True)
    print(f'{salida.relative_to(ROOT)}: {len(s)} diapositivas')


if __name__ == '__main__':
    main()
