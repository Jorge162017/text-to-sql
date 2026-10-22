"""Archivos y conexión MySQL compartidos por la etapa de datos."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATOS = ROOT / 'datos'


def guardar_json(ruta, contenido):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(contenido, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def guardar_jsonl(ruta, registros):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in registros), encoding='utf-8')


def leer_jsonl(ruta):
    with ruta.open(encoding='utf-8') as archivo:
        return [json.loads(linea) for linea in archivo if linea.strip()]


def conectar(*, permitir_scripts=False):
    import pymysql
    env = {}
    ruta = ROOT / '.env'
    if ruta.exists():
        for linea in ruta.read_text().splitlines():
            if linea.strip() and not linea.lstrip().startswith('#') and '=' in linea:
                clave, valor = linea.split('=', 1)
                env[clave.strip()] = valor.strip()
    def valor(clave, defecto):
        return os.environ.get(clave, env.get(clave, defecto))
    return pymysql.connect(host=valor('MYSQL_HOST', '127.0.0.1'),
                           port=int(valor('MYSQL_PORT', '3307')),
                           user=valor('MYSQL_USER', 'root'),
                           password=valor('MYSQL_PASSWORD', ''), charset='utf8mb4',
                           client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS if permitir_scripts else 0,
                           autocommit=True, connect_timeout=10, read_timeout=35,
                           write_timeout=35)
