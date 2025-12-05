#!/usr/bin/env python3
import os
import sys
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.database import DatabaseManager

def main():
    cfg_path = os.path.join(BASE_DIR, 'config_mysql.json')
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    db = DatabaseManager(cfg)
    if not db.verificar_conexion():
        print('CONEXION_FAIL')
        return
    db.inicializar_bd()

    nombre = f"Producto_Prueba_{int(time.time())}"
    q = """
        INSERT INTO productos (nombre, categoria, precio, stock, stock_minimo, descripcion)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    res = db.ejecutar_query(q, (nombre, 'Pruebas', 1.23, 5, 1, 'Inserción de prueba'))
    print('INSERT_RES', res)

    rows = db.ejecutar_query(
        "SELECT id, nombre FROM productos WHERE nombre = %s",
        (nombre,)
    )
    print('SELECT_COUNT', 0 if rows is None else len(rows))
    if rows:
        print('OK_ID', rows[0][0])

if __name__ == '__main__':
    main()
