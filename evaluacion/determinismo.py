"""Compara dos evaluaciones de la misma configuración: el SQL generado debe ser idéntico.

    python -m evaluacion.determinismo baseline baseline_repeticion
"""
import argparse
from datetime import datetime, timezone

from scripts.comun import ROOT, guardar_json, leer_jsonl


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('primera')
    parser.add_argument('segunda')
    args = parser.parse_args()
    base = ROOT / 'resultados' / 'evaluaciones'
    a = {r['id']: r for r in leer_jsonl(base / args.primera / 'predicciones.jsonl')}
    b = {r['id']: r for r in leer_jsonl(base / args.segunda / 'predicciones.jsonl')}
    if set(a) != set(b):
        raise SystemExit('Las corridas no cubren las mismas preguntas')
    distintas = [i for i in a if a[i]['sql_generado'] != b[i]['sql_generado'] or a[i]['acierto'] != b[i]['acierto']]
    reporte = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'primera': args.primera, 'segunda': args.segunda,
               'preguntas': len(a), 'identicas': len(a) - len(distintas), 'distintas': distintas,
               'determinista': not distintas}
    guardar_json(base / args.segunda / 'determinismo.json', reporte)
    print(f'{reporte["identicas"]}/{len(a)} idénticas' + (f'; distintas: {distintas}' if distintas else ''))
    if distintas:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
