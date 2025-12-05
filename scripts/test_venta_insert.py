#!/usr/bin/env python3
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.database import DatabaseManager

def main():
    with open(os.path.join(BASE_DIR, 'config_mysql.json'), 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    db = DatabaseManager(cfg)
    if not db.verificar_conexion():
        print('CONEXION_FAIL')
        return
    db.inicializar_bd()

    # Obtener usuario admin id
    admin_rows = db.ejecutar_query("SELECT id FROM usuarios WHERE username=%s", ('admin',)) or []
    user_id = admin_rows[0][0] if admin_rows else None

    # Pick any product
    prod = db.ejecutar_query("SELECT id, precio FROM productos ORDER BY id LIMIT 1")
    if not prod:
        print('NO_PRODUCTOS')
        return
    producto_id, precio = int(prod[0][0]), float(prod[0][1])

    # Insert venta
    venta_id = db.ejecutar_query(
        "INSERT INTO ventas (cliente, total, usuario_id) VALUES (%s, %s, %s)",
        ('Cliente Prueba', precio, user_id)
    )
    print('VENTA_ID', venta_id)
    if not venta_id:
        print('VENTA_FAIL')
        return

    # Insert detalle
    det_res = db.ejecutar_query(
        """
        INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (int(venta_id), producto_id, 1, precio, precio)
    )
    print('DETALLE_RES', det_res)

    # Actualizar stock
    upd_res = db.ejecutar_query("UPDATE productos SET stock = stock - %s WHERE id = %s", (1, producto_id))
    print('UPD_RES', upd_res)

    # Verificar venta
    rows = db.ejecutar_query("SELECT id, total FROM ventas WHERE id=%s", (venta_id,))
    print('VENTA_SELECT', rows)

if __name__ == '__main__':
    main()

