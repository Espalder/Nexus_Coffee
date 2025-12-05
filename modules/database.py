#!/usr/bin/env python3
"""
Módulo de gestión de base de datos para Nexus Café
"""

import mysql.connector
from mysql.connector import Error
import hashlib

class DatabaseManager:
    def __init__(self, db_config):
        """Inicializa el gestor de base de datos con la configuración proporcionada"""
        self.db_config = db_config
        
    def verificar_conexion(self):
        """Verificar conexión a MySQL"""
        try:
            conn = mysql.connector.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config['port']
            )
            conn.close()
            return True
        except Error as e:
            print(f"Error de conexión MySQL: {e}")
            return False
        
    def inicializar_bd(self):
        """Inicializar base de datos MySQL"""
        try:
            conn = mysql.connector.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config['port']
            )
            cursor = conn.cursor()
            
            # Crear base de datos si no existe
            cursor.execute("CREATE DATABASE IF NOT EXISTS nexus_coffee")
            conn.database = 'nexus_coffee'
            
            # Crear tablas
            self.crear_tablas(cursor)
            self.ajustar_schema_productos(cursor)
            self.ajustar_schema_ventas(cursor)
            self.ajustar_schema_configuracion(cursor)
            self.ajustar_triggers(cursor)
            
            # Insertar configuración por defecto si no existe
            self.insertar_configuracion_default(cursor)
            
            conn.commit()
            conn.close()
            return True
            
        except Error as e:
            print(f"Error inicializando BD MySQL: {e}")
            return False
            
    def insertar_configuracion_default(self, cursor):
        """Insertar configuración por defecto"""
        cursor.execute("DESCRIBE configuracion")
        columnas = [c[0] for c in cursor.fetchall()]
        tiene_descripcion = 'descripcion' in columnas
        # Configuración de tema
        cursor.execute("SELECT * FROM configuracion WHERE clave = 'tema_actual'")
        if not cursor.fetchone():
            if tiene_descripcion:
                cursor.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (%s, %s, %s)", 
                              ('tema_actual', 'claro', 'Tema actual de la aplicación'))
            else:
                cursor.execute("INSERT INTO configuracion (clave, valor) VALUES (%s, %s)", 
                              ('tema_actual', 'claro'))
        
        # Configuración de moneda (cambiado a Soles peruanos)
        cursor.execute("SELECT * FROM configuracion WHERE clave = 'moneda'")
        if not cursor.fetchone():
            if tiene_descripcion:
                cursor.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (%s, %s, %s)", 
                              ('moneda', 'S/', 'Símbolo de moneda (Soles peruanos)'))
            else:
                cursor.execute("INSERT INTO configuracion (clave, valor) VALUES (%s, %s)", 
                              ('moneda', 'S/'))
        
        # Configuración de stock mínimo
        cursor.execute("SELECT * FROM configuracion WHERE clave = 'stock_minimo_predeterminado'")
        if not cursor.fetchone():
            if tiene_descripcion:
                cursor.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (%s, %s, %s)", 
                              ('stock_minimo_predeterminado', '10', 'Stock mínimo predeterminado'))
            else:
                cursor.execute("INSERT INTO configuracion (clave, valor) VALUES (%s, %s)", 
                              ('stock_minimo_predeterminado', '10'))
        
        # Configuración de respaldo automático
        cursor.execute("SELECT * FROM configuracion WHERE clave = 'respaldo_automatico'")
        if not cursor.fetchone():
            if tiene_descripcion:
                cursor.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (%s, %s, %s)", 
                              ('respaldo_automatico', 'diario', 'Frecuencia de respaldo automático'))
            else:
                cursor.execute("INSERT INTO configuracion (clave, valor) VALUES (%s, %s)", 
                              ('respaldo_automatico', 'diario'))
        
        # Configuración de información de la cafetería
        cursor.execute("SELECT * FROM configuracion WHERE clave = 'cafeteria_nombre'")
        if not cursor.fetchone():
            if tiene_descripcion:
                cursor.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (%s, %s, %s)", 
                              ('cafeteria_nombre', 'Nexus Coffee', 'Nombre de la cafetería'))
            else:
                cursor.execute("INSERT INTO configuracion (clave, valor) VALUES (%s, %s)", 
                              ('cafeteria_nombre', 'Nexus Coffee'))
        
        cursor.execute("SELECT * FROM configuracion WHERE clave = 'cafeteria_direccion'")
        if not cursor.fetchone():
            if tiene_descripcion:
                cursor.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (%s, %s, %s)", 
                              ('cafeteria_direccion', 'Av. Principal 123, Lima, Perú', 'Dirección de la cafetería'))
            else:
                cursor.execute("INSERT INTO configuracion (clave, valor) VALUES (%s, %s)", 
                              ('cafeteria_direccion', 'Av. Principal 123, Lima, Perú'))
        
        cursor.execute("SELECT * FROM configuracion WHERE clave = 'cafeteria_telefono'")
        if not cursor.fetchone():
            if tiene_descripcion:
                cursor.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (%s, %s, %s)", 
                              ('cafeteria_telefono', '01-2345678', 'Teléfono de la cafetería'))
            else:
                cursor.execute("INSERT INTO configuracion (clave, valor) VALUES (%s, %s)", 
                              ('cafeteria_telefono', '01-2345678'))
        
        cursor.execute("SELECT * FROM configuracion WHERE clave = 'cafeteria_email'")
        if not cursor.fetchone():
            if tiene_descripcion:
                cursor.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (%s, %s, %s)", 
                              ('cafeteria_email', 'info@nexuscafe.com', 'Email de la cafetería'))
            else:
                cursor.execute("INSERT INTO configuracion (clave, valor) VALUES (%s, %s)", 
                              ('cafeteria_email', 'info@nexuscafe.com'))
        
        cursor.execute("SELECT * FROM configuracion WHERE clave = 'cafeteria_ruc'")
        if not cursor.fetchone():
            if tiene_descripcion:
                cursor.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (%s, %s, %s)", 
                              ('cafeteria_ruc', '12345678901', 'RUC de la cafetería'))
            else:
                cursor.execute("INSERT INTO configuracion (clave, valor) VALUES (%s, %s)", 
                              ('cafeteria_ruc', '12345678901'))
        
    def crear_tablas(self, cursor):
        """Crear tablas en MySQL"""
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                rol VARCHAR(20) DEFAULT 'admin',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Tabla de productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                categoria VARCHAR(50) NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                stock INT NOT NULL,
                stock_minimo INT DEFAULT 10,
                descripcion TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_categoria (categoria),
                INDEX idx_nombre (nombre)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Tabla de ventas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente VARCHAR(100) NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_id INT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
                INDEX idx_fecha (fecha),
                INDEX idx_cliente (cliente)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Tabla de detalles de venta
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalles_venta (
                id INT AUTO_INCREMENT PRIMARY KEY,
                venta_id INT NOT NULL,
                producto_id INT NOT NULL,
                cantidad INT NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT,
                INDEX idx_venta (venta_id),
                INDEX idx_producto (producto_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Tabla de clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                telefono VARCHAR(20),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_nombre (nombre),
                INDEX idx_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')

        # Tabla de configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                id INT AUTO_INCREMENT PRIMARY KEY,
                clave VARCHAR(50) UNIQUE NOT NULL,
                valor VARCHAR(255) NOT NULL,
                descripcion TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')

    def ajustar_schema_productos(self, cursor):
        try:
            cursor.execute("DESCRIBE productos")
            columnas = [c[0] for c in cursor.fetchall()]
            if 'categoria' not in columnas:
                cursor.execute("ALTER TABLE productos ADD COLUMN categoria VARCHAR(50)")
            if 'descripcion' not in columnas:
                cursor.execute("ALTER TABLE productos ADD COLUMN descripcion TEXT")
            cursor.execute("DESCRIBE productos")
            detalles = cursor.fetchall()
            nombres = [d[0] for d in detalles]
            if 'categoria_id' in nombres:
                cursor.execute("ALTER TABLE productos MODIFY categoria_id INT NULL DEFAULT NULL")
        except Error as e:
            print(f"Error ajustando schema de productos: {e}")

    def ajustar_schema_ventas(self, cursor):
        try:
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'ventas' 
                AND COLUMN_NAME = 'cliente'
            """)
            tiene_cliente = cursor.fetchone() is not None
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'ventas' 
                AND COLUMN_NAME = 'cliente_id'
            """)
            tiene_cliente_id = cursor.fetchone() is not None
            if tiene_cliente_id and not tiene_cliente:
                cursor.execute("ALTER TABLE ventas ADD COLUMN cliente VARCHAR(255) NULL")
                cursor.execute("""
                    UPDATE ventas v 
                    LEFT JOIN clientes c ON v.cliente_id = c.id 
                    SET v.cliente = COALESCE(c.nombre, 'Cliente General')
                """)
                try:
                    cursor.execute("ALTER TABLE ventas DROP FOREIGN KEY ventas_ibfk_1")
                except Error:
                    pass
                cursor.execute("ALTER TABLE ventas DROP COLUMN cliente_id")
                cursor.execute("ALTER TABLE ventas ADD INDEX idx_cliente (cliente)")
            elif tiene_cliente and tiene_cliente_id:
                try:
                    cursor.execute("ALTER TABLE ventas DROP FOREIGN KEY ventas_ibfk_1")
                except Error:
                    pass
                cursor.execute("ALTER TABLE ventas DROP COLUMN cliente_id")
        except Error as e:
            print(f"Error ajustando schema de ventas: {e}")

    def ajustar_schema_configuracion(self, cursor):
        try:
            cursor.execute("DESCRIBE configuracion")
            columnas = [c[0] for c in cursor.fetchall()]
            if 'descripcion' not in columnas:
                cursor.execute("ALTER TABLE configuracion ADD COLUMN descripcion TEXT")
        except Error as e:
            print(f"Error ajustando schema de configuracion: {e}")

    def ajustar_triggers(self, cursor):
        try:
            cursor.execute("DROP TRIGGER IF EXISTS auditoria_ventas")
            cursor.execute(
                """
                CREATE TRIGGER auditoria_ventas
                AFTER INSERT ON ventas
                FOR EACH ROW
                BEGIN
                    INSERT INTO auditoria (tabla, accion, detalles, usuario_id, fecha)
                    VALUES ('ventas', 'INSERT', 
                            CONCAT('Venta #', NEW.id, ' - Cliente: ', NEW.cliente, ' - Total: S/', NEW.total), 
                            NEW.usuario_id, NOW());
                END
                """
            )
        except Error as e:
            print(f"Error ajustando triggers: {e}")
        
    def crear_admin_default(self):
        """Crear usuario admin por defecto en MySQL"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Verificar si existe admin
            cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
            if not cursor.fetchone():
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute("INSERT INTO usuarios (username, password, nombre, rol) VALUES (%s, %s, %s, %s)",
                              ("admin", password_hash, "Administrador", "admin"))
                conn.commit()
            
            conn.close()
            return True
            
        except Error as e:
            print(f"Error creando admin MySQL: {e}")
            return False
            
    def ejecutar_query(self, query, params=None):
        """Ejecutar una consulta en la base de datos MySQL"""
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                conn.commit()
                result = cursor.lastrowid if query.strip().upper().startswith("INSERT") else cursor.rowcount
            else:
                result = cursor.fetchall()
                
            return result
            
        except Error as e:
            print(f"Error ejecutando query: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
