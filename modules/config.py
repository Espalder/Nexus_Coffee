#!/usr/bin/env python3
"""
Módulo de configuración para Nexus Café
Contiene la configuración de la aplicación
"""

# Configuración de base de datos MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Cambiar según tu configuración
    'password': 'KV7$LU%9k&tQ#ayU',  # Cambiar según tu configuración
    'database': 'nexus_coffee',
    'port': 3306
}

# Configuración de la aplicación
APP_CONFIG = {
    'titulo': 'Nexus Coffee - Sistema de Gestión',
    'version': '1.0.0',
    'tema_default': 'claro',
    'moneda': 'S/',
    'stock_minimo': 10,
    'respaldo_automatico': 'diario'
}

# Configuración de la cafetería
CAFETERIA_CONFIG = {
    'nombre': 'Nexus Coffee',
    'direccion': 'Av. Principal 123, Lima, Perú',
    'telefono': '01-2345678',
    'email': 'info@nexuscafe.com',
    'ruc': '12345678901'
}

# Configuración de rutas
import os

# Obtener la ruta base del proyecto (donde está el main)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Definir rutas importantes
PATHS = {
    'base_dir': BASE_DIR,
    'pdf_dir': os.path.join(BASE_DIR, 'pdfs_generados')
}

# Crear directorio para PDFs si no existe
if not os.path.exists(PATHS['pdf_dir']):
    os.makedirs(PATHS['pdf_dir'])