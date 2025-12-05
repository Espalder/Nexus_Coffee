#!/usr/bin/env python3
"""
Nexus Cofee - Sistema de Gestión Integral (Versión Modular)
Aplicación completa para la administración de cafetería con estructura modular
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import os
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import json
import hashlib
import mysql.connector
from decimal import Decimal

# Importar módulos personalizados
from modules.database import DatabaseManager
from modules.models import Usuario, Producto, Venta, Cliente, Configuracion
from modules.pdf_generator import PDFGenerator

class NexusCafeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexus Coffee - Sistema de Gestión")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2C3E50")
        
        # Variables de tema
        self.tema_actual = tk.StringVar(value="claro")
        self.usuario_actual = None
        self.reverse_sort = False  # Para ordenamiento
        
        # Configuración de base de datos MySQL
        self.db_config = {
            'host': 'localhost',
            'user': 'root',  # Cambiar según tu configuración
            'password': 'KV7$LU%9k&tQ#ayU',  # Cambiar según tu configuración
            'database': 'nexus_coffee',
            'port': 3306
        }
        
        # Inicializar gestor de base de datos
        self.db_manager = DatabaseManager(self.db_config)
        
        # Intentar conectar a MySQL
        if not self.db_manager.verificar_conexion():
            messagebox.showerror("Error de Base de Datos", 
                               "No se pudo conectar a MySQL. Por favor verifica que MySQL esté ejecutándose y las credenciales sean correctas.")
            self.root.quit()
            return
            
        # Inicializar base de datos
        self.db_manager.inicializar_bd()
        
        # CORREGIDO: Pasar el db_manager en lugar de db_config
        self.models = {
            'usuario': Usuario(self.db_manager),
            'producto': Producto(self.db_manager),
            'venta': Venta(self.db_manager),
            'cliente': Cliente(self.db_manager),
            'configuracion': Configuracion(self.db_manager)
        }
        
        # Inicializar generador de PDF
        self.pdf_generator = PDFGenerator()
        
        # Crear usuario admin por defecto si no existe
        self.crear_usuario_admin_default()
        
        # Mostrar pantalla de login
        self.mostrar_login()
        
        # Iniciar el bucle principal
        self.root.mainloop()
        
    def crear_usuario_admin_default(self):
        """Crea un usuario administrador por defecto si no existe"""
        try:
            # CORREGIDO: Usar el mismo método de hash que en el modelo
            query = "SELECT * FROM usuarios WHERE username = 'admin'"
            users = self.db_manager.ejecutar_query(query)
            
            if not users:
                # Crear usuario admin directamente
                hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
                # CORREGIDO: Eliminar el campo email que no existe en la tabla
                query = "INSERT INTO usuarios (username, password, nombre, rol) VALUES (%s, %s, %s, %s)"
                self.db_manager.ejecutar_query(query, ("admin", hashed_password, "Administrador", "admin"))
                print("Usuario admin creado con éxito")
        except Exception as e:
            print(f"Error al crear usuario admin: {e}")
    
    def mostrar_login(self):
        """Muestra la pantalla de login"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#2C3E50")
        main_frame.pack(fill="both", expand=True)
        
        # Frame de login (centrado)
        login_frame = tk.Frame(main_frame, bg="white", padx=40, pady=40)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        tk.Label(login_frame, text="NEXUS COFFEE", font=("Arial", 24, "bold"), bg="white", fg="#2C3E50").pack(pady=(0, 20))
        
        # Subtítulo
        tk.Label(login_frame, text="Sistema de Gestión", font=("Arial", 14), bg="white", fg="#7F8C8D").pack(pady=(0, 30))
        
        # Usuario
        tk.Label(login_frame, text="Usuario:", font=("Arial", 12), bg="white", fg="#2C3E50").pack(anchor="w")
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12), width=30)
        self.username_entry.pack(pady=(0, 15), ipady=5)
        
        # Contraseña
        tk.Label(login_frame, text="Contraseña:", font=("Arial", 12), bg="white", fg="#2C3E50").pack(anchor="w")
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), width=30, show="•")
        self.password_entry.pack(pady=(0, 25), ipady=5)
        
        # Botón de login
        login_button = tk.Button(login_frame, text="Iniciar Sesión", font=("Arial", 12, "bold"), 
                               bg="#3498DB", fg="white", padx=20, pady=8, bd=0,
                               command=self.validar_login)
        login_button.pack(pady=(0, 15))
        
        # Enlace para recuperar contraseña
        tk.Label(login_frame, text="¿Olvidaste tu contraseña?", font=("Arial", 10), 
               bg="white", fg="#3498DB", cursor="hand2").pack()
        
        # Versión
        tk.Label(login_frame, text="v1.0.0", font=("Arial", 8), bg="white", fg="#95A5A6").pack(pady=(20, 0))
        
        # Enfocar en usuario
        self.username_entry.focus_set()
        
        # Bind Enter solo en el campo de contraseña
        self.password_entry.bind('<Return>', lambda e: self.validar_login())
    
    def validar_login(self):
        """Valida las credenciales de login"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor ingresa usuario y contraseña")
            return
        
        # Validar credenciales
        usuario = self.models['usuario'].autenticar(username, password)
        
        if usuario:
            self.usuario_actual = usuario
            self.mostrar_dashboard()
        else:
            messagebox.showerror("Error", "Credenciales inválidas")
            
    def mostrar_dashboard(self):
        """Muestra el dashboard principal"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Crear menú superior
        self.crear_menu_superior()
        
        # Frame de contenido principal (dividido en panel lateral y contenido)
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True)
        
        # Panel lateral
        self.crear_panel_lateral()
        
        # Frame de contenido
        self.contenido_frame = tk.Frame(self.content_frame, bg="#ECF0F1")
        self.contenido_frame.pack(side="left", fill="both", expand=True)
        
        # Mostrar resumen por defecto
        self.mostrar_resumen()
    
    def crear_menu_superior(self):
        """Crea el menú superior"""
        menu_frame = tk.Frame(self.main_frame, bg="#2C3E50", height=50)
        menu_frame.pack(fill="x")
        
        # Logo/Título
        tk.Label(menu_frame, text="NEXUS COFFEE", font=("Arial", 16, "bold"), 
               bg="#2C3E50", fg="white").pack(side="left", padx=20)
        
        # Frame para botones de la derecha
        botones_frame = tk.Frame(menu_frame, bg="#2C3E50")
        botones_frame.pack(side="right", fill="y")
        
        # Botón de usuario
        if self.usuario_actual:
            # CORREGIDO: Acceder como diccionario en lugar de lista
            nombre = self.usuario_actual['nombre']  # Cambiado de [1] a ['nombre']
            rol = self.usuario_actual['rol']        # Cambiado de [4] a ['rol']
            
            usuario_btn = tk.Menubutton(botones_frame, text=f"{nombre} ({rol})", 
                                     font=("Arial", 10), bg="#2C3E50", fg="white",
                                     activebackground="#34495E", activeforeground="white")
            usuario_btn.pack(side="left", padx=10)
            
            # Menú desplegable
            usuario_menu = tk.Menu(usuario_btn, tearoff=0)
            usuario_btn["menu"] = usuario_menu
            usuario_menu.add_command(label="Mi Perfil")
            usuario_menu.add_command(label="Cambiar Contraseña")
            usuario_menu.add_separator()
            usuario_menu.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)
        
        # Botón de configuración (solo si tiene permisos)
        if self.verificar_permiso('configuracion'):
            config_btn = tk.Button(botones_frame, text="⚙", font=("Arial", 16), 
                                 bg="#2C3E50", fg="white", bd=0,
                                 activebackground="#34495E", activeforeground="white",
                                 command=self.mostrar_configuracion)
            config_btn.pack(side="left", padx=10)
        
        # Botón de ayuda
        help_btn = tk.Button(botones_frame, text="?", font=("Arial", 14, "bold"), 
                           bg="#2C3E50", fg="white", bd=0,
                           activebackground="#34495E", activeforeground="white")
        help_btn.pack(side="left", padx=10)
    
    def verificar_permiso(self, modulo):
        """Verifica si el usuario actual tiene permiso para acceder a un módulo"""
        if not self.usuario_actual:
            return False
        
        rol = self.usuario_actual['rol']
        
        # Definición de permisos por rol
        permisos = {
            'admin': ['resumen', 'ventas', 'inventario', 'clientes', 'reportes', 'configuracion', 'acerca_de'],
            'vendedor': ['resumen', 'ventas', 'clientes', 'reportes'],
            'inventario': ['resumen', 'inventario', 'reportes']
        }
        
        return modulo in permisos.get(rol, [])
    
    def verificar_permiso_accion(self, accion, modulo=None):
        """Verifica si el usuario tiene permiso para realizar una acción específica"""
        if not self.usuario_actual:
            return False
        
        rol = self.usuario_actual['rol']
        
        # Permisos específicos por acción
        permisos_acciones = {
            'crear_producto': ['admin', 'inventario'],
            'editar_producto': ['admin', 'inventario'],
            'eliminar_producto': ['admin', 'inventario'],
            'crear_venta': ['admin', 'vendedor'],
            'editar_venta': ['admin'],
            'eliminar_venta': ['admin'],
            'crear_cliente': ['admin', 'vendedor'],
            'editar_cliente': ['admin', 'vendedor'],
            'eliminar_cliente': ['admin'],
            'ver_proveedores': ['admin', 'inventario'],
            'crear_proveedor': ['admin', 'inventario'],
            'editar_proveedor': ['admin', 'inventario'],
            'eliminar_proveedor': ['admin', 'inventario'],
            'ver_entradas': ['admin', 'inventario'],
            'crear_entrada': ['admin', 'inventario'],
            'editar_entrada': ['admin', 'inventario'],
            'eliminar_entrada': ['admin', 'inventario'],
            'ver_configuracion': ['admin'],
            'editar_configuracion': ['admin']
        }
        
        return rol in permisos_acciones.get(accion, ['admin'])
    
    def crear_panel_lateral(self):
        """Crea el panel lateral de navegación con control de acceso"""
        panel_frame = tk.Frame(self.content_frame, bg="#34495E", width=200)
        panel_frame.pack(side="left", fill="y")
        panel_frame.pack_propagate(False)
        
        # Estilo para botones
        btn_style = {
            "font": ("Arial", 12),
            "bg": "#34495E",
            "fg": "white",
            "bd": 0,
            "anchor": "w",
            "padx": 20,
            "pady": 10,
            "width": 20,
            "activebackground": "#2C3E50",
            "activeforeground": "white"
        }
        
        # Botones de navegación con control de acceso
        botones = [
            ("Resumen", "resumen", self.mostrar_resumen),
            ("Ventas", "ventas", self.mostrar_ventas),
            ("Inventario", "inventario", self.mostrar_inventario),
            ("Clientes", "clientes", self.mostrar_clientes),
            ("Reportes", "reportes", self.mostrar_reportes),
            ("Configuración", "configuracion", self.mostrar_configuracion),
            ("Acerca de", "acerca_de", self.mostrar_acerca_de)
        ]
        
        for texto, modulo, comando in botones:
            if self.verificar_permiso(modulo):
                tk.Button(panel_frame, text=texto, command=comando, **btn_style).pack(fill="x")
        
        # Separador
        tk.Frame(panel_frame, bg="#2C3E50", height=1).pack(fill="x", pady=10)
        
        # Botón de cerrar sesión (siempre disponible)
        tk.Button(panel_frame, text="Cerrar Sesión", command=self.cerrar_sesion, **btn_style).pack(fill="x")
        
    def mostrar_resumen(self):
        """Muestra la pantalla de resumen"""
        # Limpiar frame de contenido
        for widget in self.contenido_frame.winfo_children():
            widget.destroy()
        
        # Título
        titulo_frame = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        titulo_frame.pack(fill="x")
        
        # CORREGIDO: Acceder como diccionario en lugar de lista
        tk.Label(titulo_frame, text=f"Bienvenido, {self.usuario_actual['nombre']}", 
               font=("Arial", 18, "bold"), bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        # Frame de contenido
        contenido = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        contenido.pack(fill="both", expand=True)
        
        # Obtener datos para el resumen
        fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        ventas_hoy = self.models['venta'].obtener_ventas_por_periodo(fecha_hoy, fecha_hoy)
        total_ventas_hoy = sum(venta[2] for venta in ventas_hoy) if ventas_hoy else 0
        
        # CORREGIDO: Usar el método correcto
        productos_bajo_stock = self.models['producto'].obtener_stock_bajo()
        
        # Tarjetas de resumen
        cards_frame = tk.Frame(contenido, bg="#ECF0F1")
        cards_frame.pack(fill="x", pady=10)
        
        # Configurar grid
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.columnconfigure(2, weight=1)
        
        # Tarjeta de ventas del día
        card_ventas = tk.Frame(cards_frame, bg="white", padx=15, pady=15, relief="solid", bd=1)
        card_ventas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        tk.Label(card_ventas, text="Ventas del Día", font=("Arial", 12, "bold"), bg="white", fg="#2C3E50").pack(anchor="w")
        tk.Label(card_ventas, text=f"S/ {total_ventas_hoy:.2f}", font=("Arial", 20, "bold"), bg="white", fg="#27AE60").pack(anchor="w", pady=5)
        tk.Label(card_ventas, text=f"Total de {len(ventas_hoy) if ventas_hoy else 0} ventas", font=("Arial", 10), bg="white", fg="#7F8C8D").pack(anchor="w")
        
        # Tarjeta de productos
        card_productos = tk.Frame(cards_frame, bg="white", padx=15, pady=15, relief="solid", bd=1)
        card_productos.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        productos_total = self.models['producto'].obtener_todos()
        
        tk.Label(card_productos, text="Productos", font=("Arial", 12, "bold"), bg="white", fg="#2C3E50").pack(anchor="w")
        tk.Label(card_productos, text=f"{len(productos_total) if productos_total else 0}", font=("Arial", 20, "bold"), bg="white", fg="#3498DB").pack(anchor="w", pady=5)
        tk.Label(card_productos, text=f"{len(productos_bajo_stock) if productos_bajo_stock else 0} con bajo stock", font=("Arial", 10), bg="white", fg="#7F8C8D").pack(anchor="w")
        
        # Tarjeta de clientes
        card_clientes = tk.Frame(cards_frame, bg="white", padx=15, pady=15, relief="solid", bd=1)
        card_clientes.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        clientes_total = self.models['cliente'].obtener_todos()
        
        tk.Label(card_clientes, text="Clientes", font=("Arial", 12, "bold"), bg="white", fg="#2C3E50").pack(anchor="w")
        tk.Label(card_clientes, text=f"{len(clientes_total) if clientes_total else 0}", font=("Arial", 20, "bold"), bg="white", fg="#9B59B6").pack(anchor="w", pady=5)
        tk.Label(card_clientes, text="Registrados", font=("Arial", 10), bg="white", fg="#7F8C8D").pack(anchor="w")
        
        # Gráfico de ventas
        grafico_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        grafico_frame.pack(fill="x", pady=10)
        
        tk.Label(grafico_frame, text="Ventas de los últimos 7 días", font=("Arial", 12, "bold"), bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        # Crear gráfico
        try:
            ventas_semana = self.models['venta'].obtener_total_ventas_por_dia(7)
            
            if ventas_semana:
                fig, ax = plt.subplots(figsize=(8, 3))
                
                fechas = [venta[0].strftime("%d/%m") for venta in ventas_semana]
                montos = [float(venta[1]) for venta in ventas_semana]
                
                ax.bar(fechas, montos, color="#3498DB")
                ax.set_ylabel("Monto (S/)")
                ax.set_title("Ventas por día")
                
                # Mostrar gráfico en tkinter
                canvas = FigureCanvasTkAgg(fig, master=grafico_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            else:
                tk.Label(grafico_frame, text="No hay datos de ventas para mostrar", font=("Arial", 10), bg="white", fg="#7F8C8D").pack(pady=20)
        except Exception as e:
            tk.Label(grafico_frame, text=f"Error al generar gráfico: {e}", font=("Arial", 10), bg="white", fg="#E74C3C").pack(pady=20)
        
        # Productos con bajo stock
        stock_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        stock_frame.pack(fill="x", pady=10)
        
        tk.Label(stock_frame, text="Productos con Bajo Stock", font=("Arial", 12, "bold"), bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        if productos_bajo_stock:
            # Crear tabla
            tabla_frame = tk.Frame(stock_frame, bg="white")
            tabla_frame.pack(fill="x")
            
            # Encabezados
            tk.Label(tabla_frame, text="ID", width=5, font=("Arial", 10, "bold"), bg="#ECF0F1", fg="#2C3E50").grid(row=0, column=0, padx=2, pady=2, sticky="w")
            tk.Label(tabla_frame, text="Producto", width=20, font=("Arial", 10, "bold"), bg="#ECF0F1", fg="#2C3E50").grid(row=0, column=1, padx=2, pady=2, sticky="w")
            tk.Label(tabla_frame, text="Stock Actual", width=10, font=("Arial", 10, "bold"), bg="#ECF0F1", fg="#2C3E50").grid(row=0, column=2, padx=2, pady=2, sticky="w")
            tk.Label(tabla_frame, text="Stock Mínimo", width=10, font=("Arial", 10, "bold"), bg="#ECF0F1", fg="#2C3E50").grid(row=0, column=3, padx=2, pady=2, sticky="w")
            
            # Datos
            for i, producto in enumerate(productos_bajo_stock[:5]):  # Mostrar solo los primeros 5
                tk.Label(tabla_frame, text=producto[0], font=("Arial", 10), bg="white").grid(row=i+1, column=0, padx=2, pady=2, sticky="w")
                tk.Label(tabla_frame, text=producto[1], font=("Arial", 10), bg="white").grid(row=i+1, column=1, padx=2, pady=2, sticky="w")
                tk.Label(tabla_frame, text=producto[4], font=("Arial", 10), bg="white", fg="#E74C3C" if producto[4] <= producto[5] else "black").grid(row=i+1, column=2, padx=2, pady=2, sticky="w")
                tk.Label(tabla_frame, text=producto[5], font=("Arial", 10), bg="white").grid(row=i+1, column=3, padx=2, pady=2, sticky="w")
            
            if len(productos_bajo_stock) > 5:
                tk.Label(stock_frame, text=f"... y {len(productos_bajo_stock) - 5} productos más", font=("Arial", 9), bg="white", fg="#7F8C8D").pack(anchor="e", pady=(5, 0))
        else:
            tk.Label(stock_frame, text="No hay productos con bajo stock", font=("Arial", 10), bg="white", fg="#7F8C8D").pack(pady=10)
        
        # Productos más vendidos
        top_productos_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        top_productos_frame.pack(fill="x", pady=10)
        
        tk.Label(top_productos_frame, text="Productos Más Vendidos", font=("Arial", 12, "bold"), bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        try:
            top_productos = self.models['venta'].obtener_productos_mas_vendidos(5)
            
            if top_productos:
                # Crear tabla
                tabla_frame = tk.Frame(top_productos_frame, bg="white")
                tabla_frame.pack(fill="x")
                
                # Encabezados
                tk.Label(tabla_frame, text="Producto", width=25, font=("Arial", 10, "bold"), bg="#ECF0F1", fg="#2C3E50").grid(row=0, column=0, padx=2, pady=2, sticky="w")
                tk.Label(tabla_frame, text="Cantidad", width=10, font=("Arial", 10, "bold"), bg="#ECF0F1", fg="#2C3E50").grid(row=0, column=1, padx=2, pady=2, sticky="w")
                tk.Label(tabla_frame, text="Total Vendido", width=15, font=("Arial", 10, "bold"), bg="#ECF0F1", fg="#2C3E50").grid(row=0, column=2, padx=2, pady=2, sticky="w")
                
                # Datos
                for i, producto in enumerate(top_productos):
                    tk.Label(tabla_frame, text=producto[0], font=("Arial", 10), bg="white").grid(row=i+1, column=0, padx=2, pady=2, sticky="w")
                    tk.Label(tabla_frame, text=producto[1], font=("Arial", 10), bg="white").grid(row=i+1, column=1, padx=2, pady=2, sticky="w")
                    tk.Label(tabla_frame, text=f"S/ {float(producto[2]):.2f}", font=("Arial", 10), bg="white").grid(row=i+1, column=2, padx=2, pady=2, sticky="w")
            else:
                tk.Label(top_productos_frame, text="No hay datos de ventas para mostrar", font=("Arial", 10), bg="white", fg="#7F8C8D").pack(pady=10)
        except Exception as e:
            tk.Label(top_productos_frame, text=f"Error al obtener productos más vendidos: {e}", font=("Arial", 10), bg="white", fg="#E74C3C").pack(pady=10)
    
    def mostrar_ventas(self):
        """Muestra la pantalla de ventas"""
        # Verificar permisos de acceso
        if not self.verificar_permiso('ventas'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para acceder a ventas")
            return
            
        # Limpiar frame de contenido
        for widget in self.contenido_frame.winfo_children():
            widget.destroy()
        
        # Título
        titulo_frame = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        titulo_frame.pack(fill="x")
        
        tk.Label(titulo_frame, text="Gestión de Ventas", font=("Arial", 18, "bold"), 
               bg="#ECF0F1", fg="#2C3E50").pack(side="left", anchor="w")
        
        # Botones de acción con control de permisos
        if self.verificar_permiso_accion('crear_venta'):
            btn_nueva_venta = tk.Button(titulo_frame, text="Nueva Venta", font=("Arial", 10, "bold"),
                                      bg="#27AE60", fg="white", padx=10, pady=5,
                                      command=self.crear_nueva_venta)
            btn_nueva_venta.pack(side="right", padx=5)
        
        # Frame de contenido
        contenido = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        contenido.pack(fill="both", expand=True)
        
        # Frame de búsqueda y filtros
        busqueda_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        busqueda_frame.pack(fill="x", pady=10)
        
        # Etiqueta de búsqueda
        tk.Label(busqueda_frame, text="Buscar ventas:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Campo de búsqueda
        busqueda_entry = tk.Entry(busqueda_frame, font=("Arial", 10), width=30)
        busqueda_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Botón de búsqueda
        btn_buscar = tk.Button(busqueda_frame, text="Buscar", font=("Arial", 10),
                             bg="#3498DB", fg="white", padx=10)
        btn_buscar.grid(row=0, column=2, padx=5, pady=5)
        
        # Filtros de fecha
        tk.Label(busqueda_frame, text="Desde:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        desde_entry = tk.Entry(busqueda_frame, font=("Arial", 10), width=12)
        desde_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        desde_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(busqueda_frame, text="Hasta:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        hasta_entry = tk.Entry(busqueda_frame, font=("Arial", 10), width=12)
        hasta_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        hasta_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        
        btn_filtrar = tk.Button(busqueda_frame, text="Filtrar", font=("Arial", 10),
                              bg="#3498DB", fg="white", padx=10)
        btn_filtrar.grid(row=1, column=4, padx=5, pady=5)
        
        # Tabla de ventas
        tabla_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        tabla_frame.pack(fill="both", expand=True, pady=10)
        
        # Obtener ventas
        ventas = self.models['venta'].obtener_todas()
        
        # Crear tabla con ordenación y multi-selección
        self.tabla_ventas = ttk.Treeview(
            tabla_frame,
            columns=("id", "fecha", "cliente", "total"),
            show="headings",
            selectmode="extended",
        )
        self.tabla_ventas.pack(fill="both", expand=True)
        
        # Configurar columnas con ordenación al hacer clic
        self.tabla_ventas.heading("id", text="ID", command=lambda: self.ordenar_columna(self.tabla_ventas, "id", False))
        self.tabla_ventas.heading("fecha", text="Fecha", command=lambda: self.ordenar_columna(self.tabla_ventas, "fecha", False))
        self.tabla_ventas.heading("cliente", text="Cliente", command=lambda: self.ordenar_columna(self.tabla_ventas, "cliente", False))
        self.tabla_ventas.heading("total", text="Total", command=lambda: self.ordenar_columna(self.tabla_ventas, "total", False))
        
        self.tabla_ventas.column("id", width=50)
        self.tabla_ventas.column("fecha", width=150)
        self.tabla_ventas.column("cliente", width=200)
        self.tabla_ventas.column("total", width=100)
        
        # Insertar datos
        if ventas:
            for venta in ventas:
                if len(venta) >= 4:
                    # venta = (id, cliente, total, fecha)
                    fecha_val = venta[3]
                    fecha_formateada = fecha_val.strftime("%Y-%m-%d %H:%M") if isinstance(fecha_val, datetime.datetime) else str(fecha_val)
                    self.tabla_ventas.insert("", "end", values=(
                        venta[0],              # ID
                        fecha_formateada,      # Fecha
                        venta[1],              # Cliente
                        f"S/ {float(venta[2]):.2f}"  # Total
                    ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla_ventas.yview)
        self.tabla_ventas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Frame de botones de acción con control de permisos
        acciones_frame = tk.Frame(contenido, bg="#ECF0F1")
        acciones_frame.pack(fill="x", pady=10)
        
        btn_ver = tk.Button(acciones_frame, text="Ver Detalles", font=("Arial", 10),
                          bg="#3498DB", fg="white", padx=10, pady=5,
                          command=self.ver_detalles_venta)
        btn_ver.pack(side="left", padx=5)
        
        btn_imprimir = tk.Button(acciones_frame, text="Imprimir", font=("Arial", 10),
                               bg="#2C3E50", fg="white", padx=10, pady=5,
                               command=self.imprimir_venta)
        btn_imprimir.pack(side="left", padx=5)
        
        btn_exportar = tk.Button(acciones_frame, text="Exportar", font=("Arial", 10),
                               bg="#2C3E50", fg="white", padx=10, pady=5,
                               command=self.exportar_ventas)
        btn_exportar.pack(side="left", padx=5)
        
        if self.verificar_permiso_accion('eliminar_venta'):
            btn_eliminar = tk.Button(acciones_frame, text="Eliminar", font=("Arial", 10),
                                   bg="#E74C3C", fg="white", padx=10, pady=5,
                                   command=self.eliminar_venta)
            btn_eliminar.pack(side="right", padx=5)
    
    def crear_nueva_venta(self):
        """Crea una nueva venta"""
        # Verificar permisos
        if not self.verificar_permiso_accion('crear_venta'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para crear ventas")
            return
        # Crear ventana para nueva venta
        venta_window = tk.Toplevel(self.root)
        venta_window.title("Nueva Venta")
        venta_window.geometry("800x600")
        venta_window.configure(bg="#ECF0F1")
        
        # Frame principal
        main_frame = tk.Frame(venta_window, bg="#ECF0F1", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Información de la venta
        info_frame = tk.Frame(main_frame, bg="white", padx=15, pady=15, relief="solid", bd=1)
        info_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(info_frame, text="Información de la Venta", font=("Arial", 12, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        # Cliente
        cliente_frame = tk.Frame(info_frame, bg="white")
        cliente_frame.pack(fill="x", pady=5)
        
        tk.Label(cliente_frame, text="Cliente:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50", width=15, anchor="w").pack(side="left", padx=5)
        
        cliente_entry = tk.Entry(cliente_frame, font=("Arial", 10))
        cliente_entry.pack(side="left", padx=5, fill="x", expand=True)
        cliente_entry.insert(0, "Cliente General")
        
        # Fecha y hora
        fecha_frame = tk.Frame(info_frame, bg="white")
        fecha_frame.pack(fill="x", pady=5)
        
        tk.Label(fecha_frame, text="Fecha:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50", width=15, anchor="w").pack(side="left", padx=5)
        
        fecha_label = tk.Label(fecha_frame, text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                             font=("Arial", 10), bg="white")
        fecha_label.pack(side="left", padx=5)
        
        # Productos
        productos_frame = tk.Frame(main_frame, bg="white", padx=15, pady=15, relief="solid", bd=1)
        productos_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        tk.Label(productos_frame, text="Productos", font=("Arial", 12, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        # Tabla de productos
        tabla_productos = ttk.Treeview(productos_frame, columns=("id", "nombre", "precio", "cantidad", "subtotal"), show="headings")
        tabla_productos.pack(fill="both", expand=True)
        
        # Configurar columnas
        tabla_productos.heading("id", text="ID")
        tabla_productos.heading("nombre", text="Nombre")
        tabla_productos.heading("precio", text="Precio")
        tabla_productos.heading("cantidad", text="Cantidad")
        tabla_productos.heading("subtotal", text="Subtotal")
        
        tabla_productos.column("id", width=50)
        tabla_productos.column("nombre", width=200)
        tabla_productos.column("precio", width=100)
        tabla_productos.column("cantidad", width=100)
        tabla_productos.column("subtotal", width=100)
        
        # Frame de añadir productos
        add_frame = tk.Frame(productos_frame, bg="white")
        add_frame.pack(fill="x", pady=10)
        
        # Selección de producto
        tk.Label(add_frame, text="Producto:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Obtener productos
        productos = self.models['producto'].obtener_todos()
        nombres_productos = [p[1] for p in productos] if productos else []
        
        producto_var = tk.StringVar()
        producto_combo = ttk.Combobox(add_frame, textvariable=producto_var, values=nombres_productos, 
                                    font=("Arial", 10), width=30, state="readonly")
        producto_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Cantidad
        tk.Label(add_frame, text="Cantidad:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        cantidad_entry = tk.Entry(add_frame, font=("Arial", 10), width=10)
        cantidad_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        cantidad_entry.insert(0, "1")

        # Campo para quitar cantidad
        tk.Label(add_frame, text="Quitar:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").grid(row=1, column=3, padx=5, pady=5, sticky="w")
        quitar_entry = tk.Entry(add_frame, font=("Arial", 10), width=10)
        quitar_entry.grid(row=1, column=4, padx=5, pady=5, sticky="w")
        quitar_entry.insert(0, "1")

        # Helpers
        def _recalcular_total():
            try:
                total = 0.0
                for item_id in tabla_productos.get_children():
                    vals = tabla_productos.item(item_id)['values']
                    try:
                        total += float(vals[4])
                    except Exception:
                        pass
                self.total_label.config(text=f"S/ {total:.2f}")
            except Exception:
                pass
        
        # Botón añadir con acumulación
        def _añadir_producto():
            try:
                nombre_elegido = producto_var.get()
                if not nombre_elegido:
                    messagebox.showwarning("Advertencia", "Seleccione un producto")
                    return

                # Buscar producto por nombre
                prod = next((p for p in productos if len(p) > 1 and str(p[1]) == str(nombre_elegido)), None)
                if not prod:
                    messagebox.showerror("Error", "Producto no encontrado")
                    return

                try:
                    cantidad = int(float(cantidad_entry.get().replace(',', '.')))
                except Exception:
                    messagebox.showerror("Error", "Cantidad inválida")
                    return

                if cantidad <= 0:
                    messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                    return

                # Estructura esperada del producto: (id, nombre, categoria, precio, stock, stock_minimo)
                precio = prod[3] if len(prod) > 3 else 0
                stock_disp = prod[4] if len(prod) > 4 else 0

                try:
                    precio_num = float(precio) if not isinstance(precio, str) else float(precio.replace(',', '.'))
                except Exception:
                    precio_num = 0.0

                try:
                    stock_num = int(float(stock_disp)) if not isinstance(stock_disp, str) else int(float(stock_disp.replace(',', '.')))
                except Exception:
                    stock_num = 0

                # Verificar si ya existe el producto en la tabla
                existente_id = None
                cantidad_existente = 0
                for item_id in tabla_productos.get_children():
                    vals = tabla_productos.item(item_id)['values']
                    if int(vals[0]) == int(prod[0]):
                        existente_id = item_id
                        try:
                            cantidad_existente = int(float(vals[3]))
                        except Exception:
                            cantidad_existente = 0
                        break

                nueva_cantidad = cantidad_existente + cantidad
                if nueva_cantidad > stock_num:
                    messagebox.showwarning("Stock insuficiente", f"Stock disponible: {stock_num}")
                    return

                if existente_id is not None:
                    # Actualizar fila existente
                    nuevo_subtotal = precio_num * nueva_cantidad
                    tabla_productos.item(existente_id, values=(prod[0], prod[1], precio_num, nueva_cantidad, nuevo_subtotal))
                else:
                    # Insertar nueva fila
                    subtotal = precio_num * cantidad
                    tabla_productos.insert("", "end", values=(prod[0], prod[1], precio_num, cantidad, subtotal))

                _recalcular_total()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo añadir el producto: {e}")

        btn_añadir = tk.Button(add_frame, text="Añadir Producto", font=("Arial", 10, "bold"),
                               bg="#3498DB", fg="white", padx=10, pady=5, command=_añadir_producto)
        btn_añadir.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Botones para quitar/eliminar
        def _quitar_cantidad():
            sel = tabla_productos.selection()
            if not sel:
                messagebox.showwarning("Advertencia", "Seleccione un producto en la tabla")
                return
            try:
                quitar = int(float(quitar_entry.get().replace(',', '.')))
            except Exception:
                messagebox.showerror("Error", "Cantidad a quitar inválida")
                return
            if quitar <= 0:
                messagebox.showerror("Error", "La cantidad a quitar debe ser mayor a 0")
                return
            vals = tabla_productos.item(sel[0])['values']
            try:
                cantidad_actual = int(float(vals[3]))
            except Exception:
                cantidad_actual = 0
            if quitar >= cantidad_actual:
                tabla_productos.delete(sel[0])
            else:
                nueva = cantidad_actual - quitar
                precio_num = float(vals[2])
                subtotal = precio_num * nueva
                tabla_productos.item(sel[0], values=(vals[0], vals[1], precio_num, nueva, subtotal))
            _recalcular_total()

        def _eliminar_producto():
            sel = tabla_productos.selection()
            if not sel:
                messagebox.showwarning("Advertencia", "Seleccione un producto en la tabla")
                return
            tabla_productos.delete(sel[0])
            _recalcular_total()

        btn_quitar = tk.Button(add_frame, text="Quitar Cantidad", font=("Arial", 10, "bold"),
                               bg="#F39C12", fg="white", padx=10, pady=5, command=_quitar_cantidad)
        btn_quitar.grid(row=1, column=5, padx=5, pady=5, sticky="w")
        
        btn_eliminar = tk.Button(add_frame, text="Eliminar Producto", font=("Arial", 10, "bold"),
                                 bg="#E74C3C", fg="white", padx=10, pady=5, command=_eliminar_producto)
        btn_eliminar.grid(row=1, column=6, padx=5, pady=5, sticky="w")
        
        # Total
        total_frame = tk.Frame(main_frame, bg="white", padx=15, pady=15, relief="solid", bd=1)
        total_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(total_frame, text="Total", font=("Arial", 12, "bold"), 
               bg="white", fg="#2C3E50").pack(side="left", padx=5)
        
        self.total_label = tk.Label(total_frame, text="S/ 0.00", font=("Arial", 14, "bold"), 
                                  bg="white", fg="#27AE60")
        self.total_label.pack(side="right", padx=5)
        
        # Frame de botones
        botones_frame = tk.Frame(main_frame, bg="#ECF0F1")
        botones_frame.pack(fill="x", pady=10)
        
        # Botón cancelar
        btn_cancelar = tk.Button(botones_frame, text="Cancelar", font=("Arial", 10, "bold"),
                                bg="#95A5A6", fg="white", padx=15, pady=5,
                                command=venta_window.destroy)
        btn_cancelar.pack(side="right", padx=5)
        
        # Botón guardar
        btn_guardar = tk.Button(botones_frame, text="Guardar Venta", font=("Arial", 10, "bold"),
                               bg="#27AE60", fg="white", padx=15, pady=5,
                               command=lambda: self.guardar_venta(venta_window, cliente_entry.get(), tabla_productos))
        btn_guardar.pack(side="right", padx=5)
    
    def guardar_venta(self, ventana, cliente, tabla_productos):
        """Guarda una venta en la base de datos"""
        try:
            # Obtener productos de la tabla
            items = tabla_productos.get_children()
            
            if not items:
                messagebox.showerror("Error", "No hay productos en la venta")
                return
            
            # Calcular total y obtener detalles
            detalles = []
            total = 0
            
            for item in items:
                values = tabla_productos.item(item)['values']
                producto_id = values[0]
                cantidad = values[3]
                subtotal = float(values[4])
                total += subtotal
                
                detalles.append({
                    'producto_id': int(values[0]),
                    'cantidad': int(values[3]),
                    'precio': float(values[2]),
                    'subtotal': float(values[4])
                })
            
            # Insertar venta
            query = "INSERT INTO ventas (cliente, total, usuario_id) VALUES (%s, %s, %s)"
            venta_id = self.db_manager.ejecutar_query(query, (cliente, total, self.usuario_actual['id']))
            
            if venta_id:
                # Insertar detalles de venta
                for detalle in detalles:
                    query = """
                        INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    self.db_manager.ejecutar_query(query, (
                        venta_id,
                        detalle['producto_id'],
                        detalle['cantidad'],
                        detalle['precio'],
                        detalle['subtotal']
                    ))
                    
                    # Actualizar stock
                    query = "UPDATE productos SET stock = stock - %s WHERE id = %s"
                    self.db_manager.ejecutar_query(query, (detalle['cantidad'], detalle['producto_id']))
                
                # Registrar cliente si no existe y refrescar la tabla si está abierta
                try:
                    nombre_cliente = (cliente or "").strip()
                    if nombre_cliente and nombre_cliente.lower() != "cliente general":
                        existe = self.db_manager.ejecutar_query(
                            "SELECT id FROM clientes WHERE nombre = %s LIMIT 1",
                            (nombre_cliente,)
                        )
                        if existe is not None and len(existe) == 0:
                            self.db_manager.ejecutar_query(
                                "INSERT INTO clientes (nombre, email, telefono) VALUES (%s, %s, %s)",
                                (nombre_cliente, None, None)
                            )
                        # Refrescar tabla de clientes si está visible
                        if hasattr(self, 'tabla_clientes') and self.tabla_clientes.winfo_exists():
                            try:
                                for item in self.tabla_clientes.get_children():
                                    self.tabla_clientes.delete(item)
                                clientes_ref = self.models['cliente'].obtener_todos()
                                if clientes_ref:
                                    for c in clientes_ref:
                                        self.tabla_clientes.insert("", "end", values=(
                                            c[0],
                                            c[1],
                                            c[2] if c[2] else "",
                                            c[3] if c[3] else ""
                                        ))
                            except Exception:
                                pass
                except Exception:
                    pass
                
                messagebox.showinfo("Éxito", "Venta guardada correctamente")
                ventana.destroy()
                self.mostrar_ventas()
            else:
                messagebox.showerror("Error", "No se pudo guardar la venta")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar venta: {str(e)}")
    
    def ver_detalles_venta(self):
        """Muestra los detalles de una venta seleccionada"""
        seleccion = self.tabla_ventas.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione una venta")
            return
        
        item = self.tabla_ventas.item(seleccion[0])
        venta_id = item['values'][0]
        
        # Crear ventana de detalles
        detalles_window = tk.Toplevel(self.root)
        detalles_window.title("Detalles de Venta")
        detalles_window.geometry("700x500")
        detalles_window.configure(bg="#ECF0F1")
        
        # Frame principal
        main_frame = tk.Frame(detalles_window, bg="#ECF0F1", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Información de la venta
        info_frame = tk.Frame(main_frame, bg="white", padx=15, pady=15, relief="solid", bd=1)
        info_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(info_frame, text="Información de la Venta", font=("Arial", 12, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        # Obtener información de la venta
        query = "SELECT * FROM ventas WHERE id = %s"
        venta = self.db_manager.ejecutar_query(query, (venta_id,))
        
        if venta:
            venta = venta[0]
            
            # Mostrar información
            info_grid = tk.Frame(info_frame, bg="white")
            info_grid.pack(fill="x", pady=5)
            
            tk.Label(info_grid, text="ID:", font=("Arial", 10, "bold"), 
                   bg="white", fg="#2C3E50", width=15, anchor="w").grid(row=0, column=0, padx=5, pady=2, sticky="w")
            tk.Label(info_grid, text=str(venta[0]), font=("Arial", 10), 
                   bg="white").grid(row=0, column=1, padx=5, pady=2, sticky="w")
            
            tk.Label(info_grid, text="Cliente:", font=("Arial", 10, "bold"), 
                   bg="white", fg="#2C3E50", width=15, anchor="w").grid(row=1, column=0, padx=5, pady=2, sticky="w")
            tk.Label(info_grid, text=venta[1], font=("Arial", 10), 
                   bg="white").grid(row=1, column=1, padx=5, pady=2, sticky="w")
            
            tk.Label(info_grid, text="Fecha:", font=("Arial", 10, "bold"), 
                   bg="white", fg="#2C3E50", width=15, anchor="w").grid(row=2, column=0, padx=5, pady=2, sticky="w")
            fecha_formateada = venta[3].strftime("%Y-%m-%d %H:%M:%S") if isinstance(venta[3], datetime.datetime) else str(venta[3])
            tk.Label(info_grid, text=fecha_formateada, font=("Arial", 10), 
                   bg="white").grid(row=2, column=1, padx=5, pady=2, sticky="w")
            
            tk.Label(info_grid, text="Total:", font=("Arial", 10, "bold"), 
                   bg="white", fg="#2C3E50", width=15, anchor="w").grid(row=3, column=0, padx=5, pady=2, sticky="w")
            tk.Label(info_grid, text=f"S/ {venta[2]:.2f}", font=("Arial", 10, "bold"), 
                   bg="white", fg="#27AE60").grid(row=3, column=1, padx=5, pady=2, sticky="w")
        
        # Detalles de productos
        detalles_frame = tk.Frame(main_frame, bg="white", padx=15, pady=15, relief="solid", bd=1)
        detalles_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        tk.Label(detalles_frame, text="Productos", font=("Arial", 12, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        # Obtener detalles de la venta
        query = """
            SELECT dv.id, p.nombre, p.precio, dv.cantidad, dv.subtotal
            FROM detalles_venta dv
            JOIN productos p ON dv.producto_id = p.id
            WHERE dv.venta_id = %s
        """
        detalles = self.db_manager.ejecutar_query(query, (venta_id,))
        
        # Tabla de detalles
        tabla_detalles = ttk.Treeview(detalles_frame, columns=("id", "nombre", "precio", "cantidad", "subtotal"), show="headings")
        tabla_detalles.pack(fill="both", expand=True)
        
        # Configurar columnas
        tabla_detalles.heading("id", text="ID")
        tabla_detalles.heading("nombre", text="Nombre")
        tabla_detalles.heading("precio", text="Precio")
        tabla_detalles.heading("cantidad", text="Cantidad")
        tabla_detalles.heading("subtotal", text="Subtotal")
        
        tabla_detalles.column("id", width=50)
        tabla_detalles.column("nombre", width=200)
        tabla_detalles.column("precio", width=100)
        tabla_detalles.column("cantidad", width=100)
        tabla_detalles.column("subtotal", width=100)
        
        # Insertar datos
        if detalles:
            for detalle in detalles:
                tabla_detalles.insert("", "end", values=(
                    detalle[0],  # ID
                    detalle[1],  # Nombre
                    f"S/ {detalle[2]:.2f}",  # Precio
                    detalle[3],  # Cantidad
                    f"S/ {detalle[4]:.2f}"  # Subtotal
                ))
        
        # Frame de botones
        botones_frame = tk.Frame(main_frame, bg="#ECF0F1")
        botones_frame.pack(fill="x", pady=10)
        
        # Botón cerrar
        btn_cerrar = tk.Button(botones_frame, text="Cerrar", font=("Arial", 10, "bold"),
                              bg="#3498DB", fg="white", padx=15, pady=5,
                              command=detalles_window.destroy)
        btn_cerrar.pack(side="right", padx=5)
    
    def imprimir_venta(self):
        """Imprime una venta seleccionada"""
        messagebox.showinfo("Información", "Función de impresión no implementada aún")
    
    def exportar_ventas(self):
        """Exporta las ventas a un archivo"""
        try:
            # Obtener ventas
            ventas = self.models['venta'].obtener_todas()
            
            if not ventas:
                messagebox.showinfo("Información", "No hay ventas para exportar")
                return
            
            # Seleccionar archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Exportar Ventas"
            )
            
            if not filename:
                return
            
            # Exportar a CSV
            import csv
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Escribir encabezados
                writer.writerow(['ID', 'Cliente', 'Total', 'Fecha'])
                
                # Escribir datos
                for venta in ventas:
                    fecha_formateada = venta[1].strftime("%Y-%m-%d %H:%M:%S") if isinstance(venta[1], datetime.datetime) else str(venta[1])
                    writer.writerow([
                        venta[0],  # ID
                        venta[2],  # Cliente
                        venta[3],  # Total
                        fecha_formateada  # Fecha
                    ])
            
            messagebox.showinfo("Éxito", f"Ventas exportadas correctamente a {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar ventas: {str(e)}")
    
    def eliminar_venta(self):
        """Elimina una venta seleccionada"""
        # Verificar permisos
        if not self.verificar_permiso_accion('eliminar_venta'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para eliminar ventas")
            return
            
        seleccion = self.tabla_ventas.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione una venta")
            return
        
        item = self.tabla_ventas.item(seleccion[0])
        venta_id = item['values'][0]
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar esta venta? Esta acción no se puede deshacer."):
            try:
                # Eliminar detalles de venta
                query = "DELETE FROM detalles_venta WHERE venta_id = %s"
                self.db_manager.ejecutar_query(query, (venta_id,))
                
                # Eliminar venta
                query = "DELETE FROM ventas WHERE id = %s"
                self.db_manager.ejecutar_query(query, (venta_id,))
                
                messagebox.showinfo("Éxito", "Venta eliminada correctamente")
                self.mostrar_ventas()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar venta: {str(e)}")
    
    def mostrar_inventario(self):
        """Muestra la pantalla de inventario"""
        # Verificar permisos de acceso
        if not self.verificar_permiso('inventario'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para acceder al inventario")
            return
            
        # Limpiar frame de contenido
        for widget in self.contenido_frame.winfo_children():
            widget.destroy()
        
        # Título
        titulo_frame = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        titulo_frame.pack(fill="x")
        
        tk.Label(titulo_frame, text="Gestión de Inventario", font=("Arial", 18, "bold"), 
               bg="#ECF0F1", fg="#2C3E50").pack(side="left", anchor="w")
        
        # Botones de acción con control de permisos
        if self.verificar_permiso_accion('crear_producto'):
            btn_nuevo = tk.Button(titulo_frame, text="Nuevo Producto", font=("Arial", 10, "bold"),
                                bg="#27AE60", fg="white", padx=10, pady=5,
                                command=self.crear_nuevo_producto)
            btn_nuevo.pack(side="right", padx=5)
        
        # Frame de contenido
        contenido = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        contenido.pack(fill="both", expand=True)
        
        # Frame de búsqueda
        busqueda_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        busqueda_frame.pack(fill="x", pady=10)
        
        # Etiqueta de búsqueda
        tk.Label(busqueda_frame, text="Buscar productos:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").pack(side="left", padx=5)
        
        # Campo de búsqueda
        self.busqueda_producto_entry = tk.Entry(busqueda_frame, font=("Arial", 10), width=30)
        self.busqueda_producto_entry.pack(side="left", padx=5)
        
        # Botón de búsqueda
        btn_buscar = tk.Button(busqueda_frame, text="Buscar", font=("Arial", 10),
                             bg="#3498DB", fg="white", padx=10,
                             command=self.buscar_productos)
        btn_buscar.pack(side="left", padx=5)
        
        # Filtro de categoría
        tk.Label(busqueda_frame, text="Categoría:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").pack(side="left", padx=(20, 5))
        
        # Obtener categorías
        query = "SELECT DISTINCT categoria FROM productos"
        categorias_result = self.db_manager.ejecutar_query(query)
        categorias = ["Todas"] + [cat[0] for cat in categorias_result] if categorias_result else ["Todas"]
        
        self.categoria_var = tk.StringVar(value=categorias[0])
        categoria_menu = ttk.Combobox(busqueda_frame, textvariable=self.categoria_var, values=categorias, 
                                    font=("Arial", 10), width=15, state="readonly")
        categoria_menu.pack(side="left", padx=5)
        
        # Botón de filtrar
        btn_filtrar = tk.Button(busqueda_frame, text="Filtrar", font=("Arial", 10),
                              bg="#3498DB", fg="white", padx=10,
                              command=self.filtrar_productos)
        btn_filtrar.pack(side="left", padx=5)
        
        # Tabla de productos
        tabla_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        tabla_frame.pack(fill="both", expand=True, pady=10)
        
        # Obtener productos
        productos = self.models['producto'].obtener_todos()
        
        # Crear tabla con ordenación y multi-selección
        self.tabla_productos = ttk.Treeview(
            tabla_frame,
            columns=("id", "nombre", "categoria", "precio", "stock", "stock_min"),
            show="headings",
            selectmode="extended",
        )
        self.tabla_productos.pack(fill="both", expand=True)
        
        # Configurar columnas con ordenación al hacer clic
        self.tabla_productos.heading("id", text="ID", command=lambda: self.ordenar_columna(self.tabla_productos, "id", False))
        self.tabla_productos.heading("nombre", text="Nombre", command=lambda: self.ordenar_columna(self.tabla_productos, "nombre", False))
        self.tabla_productos.heading("categoria", text="Categoría", command=lambda: self.ordenar_columna(self.tabla_productos, "categoria", False))
        self.tabla_productos.heading("precio", text="Precio", command=lambda: self.ordenar_columna(self.tabla_productos, "precio", False))
        self.tabla_productos.heading("stock", text="Stock", command=lambda: self.ordenar_columna(self.tabla_productos, "stock", False))
        self.tabla_productos.heading("stock_min", text="Stock Mín.", command=lambda: self.ordenar_columna(self.tabla_productos, "stock_min", False))
        
        self.tabla_productos.column("id", width=50)
        self.tabla_productos.column("nombre", width=200)
        self.tabla_productos.column("categoria", width=100)
        self.tabla_productos.column("precio", width=100)
        self.tabla_productos.column("stock", width=80)
        self.tabla_productos.column("stock_min", width=80)
        
        # Insertar datos
        if productos:
            for producto in productos:
                # Colorear según stock
                tags = ("stock_bajo",) if producto[4] <= producto[5] else ("",)
                
                self.tabla_productos.insert("", "end", values=(
                    producto[0],  # ID
                    producto[1],  # Nombre
                    producto[2],  # Categoría
                    f"S/ {producto[3]:.2f}",  # Precio
                    producto[4],  # Stock
                    producto[5]   # Stock Mínimo
                ), tags=tags)
            
            # Configurar colores
            self.tabla_productos.tag_configure("stock_bajo", background="#FADBD8", foreground="#E74C3C")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Frame de botones de acción con control de permisos
        acciones_frame = tk.Frame(contenido, bg="#ECF0F1")
        acciones_frame.pack(fill="x", pady=10)
        
        if self.verificar_permiso_accion('editar_producto'):
            btn_editar = tk.Button(acciones_frame, text="Editar", font=("Arial", 10),
                                 bg="#3498DB", fg="white", padx=10, pady=5,
                                 command=self.editar_producto)
            btn_editar.pack(side="left", padx=5)
        
        if self.verificar_permiso_accion('eliminar_producto'):
            btn_eliminar = tk.Button(acciones_frame, text="Eliminar", font=("Arial", 10),
                                   bg="#E74C3C", fg="white", padx=10, pady=5,
                                   command=self.eliminar_producto)
            btn_eliminar.pack(side="left", padx=5)
        
        if self.verificar_permiso_accion('editar_producto'):
            btn_ajustar = tk.Button(acciones_frame, text="Ajustar Stock", font=("Arial", 10),
                                  bg="#2C3E50", fg="white", padx=10, pady=5,
                                  command=self.ajustar_stock)
            btn_ajustar.pack(side="left", padx=5)
        
        btn_exportar = tk.Button(acciones_frame, text="Exportar", font=("Arial", 10),
                               bg="#2C3E50", fg="white", padx=10, pady=5,
                               command=self.exportar_productos)
        btn_exportar.pack(side="right", padx=5)
    
    def crear_nuevo_producto(self):
        """Crea un nuevo producto"""
        # Verificar permisos
        if not self.verificar_permiso_accion('crear_producto'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para crear productos")
            return
        # Crear ventana para nuevo producto
        producto_window = tk.Toplevel(self.root)
        producto_window.title("Nuevo Producto")
        producto_window.geometry("500x500")
        producto_window.configure(bg="#ECF0F1")
        
        # Frame principal
        main_frame = tk.Frame(producto_window, bg="#ECF0F1", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Campos del formulario
        campos = [
            ("Nombre:", "entry_nombre"),
            ("Categoría:", "entry_categoria"),
            ("Precio (S/):", "entry_precio"),
            ("Stock:", "entry_stock"),
            ("Stock Mínimo:", "entry_stock_minimo"),
            ("Descripción:", "entry_descripcion")
        ]
        
        entries = {}
        
        for i, (label, nombre) in enumerate(campos):
            tk.Label(main_frame, text=label, bg="#ECF0F1", font=("Arial", 12)).pack(pady=(10, 5), anchor="w")
            
            if nombre == "entry_categoria":
                # Obtener categorías existentes
                query = "SELECT DISTINCT categoria FROM productos"
                categorias_result = self.db_manager.ejecutar_query(query)
                categorias = [cat[0] for cat in categorias_result] if categorias_result else []
                
                entry = ttk.Combobox(main_frame, values=categorias, font=("Arial", 12))
                entry.pack(pady=(0, 10), padx=20, fill="x")
            elif nombre == "entry_descripcion":
                entry = tk.Text(main_frame, height=4, font=("Arial", 12))
                entry.pack(pady=(0, 10), padx=20, fill="x")
            else:
                entry = tk.Entry(main_frame, font=("Arial", 12))
                entry.pack(pady=(0, 10), padx=20, fill="x")
                
            entries[nombre] = entry
        
        # Frame de botones
        botones_frame = tk.Frame(producto_window, bg="#ECF0F1")
        botones_frame.pack(side="bottom", fill="x", pady=10, padx=10)
        
        # Función para guardar producto
        def guardar_producto():
            try:
                nombre = entries["entry_nombre"].get()
                categoria = entries["entry_categoria"].get()
                precio = float(entries["entry_precio"].get())
                stock = int(entries["entry_stock"].get())
                stock_minimo = int(entries["entry_stock_minimo"].get())
                descripcion = entries["entry_descripcion"].get("1.0", tk.END).strip()
                
                if not all([nombre, categoria, precio, stock]):
                    messagebox.showerror("Error", "Por favor complete los campos obligatorios")
                    return
                
                query = """
                    INSERT INTO productos (nombre, categoria, precio, stock, stock_minimo, descripcion)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                resultado = self.db_manager.ejecutar_query(query, (nombre, categoria, precio, stock, stock_minimo, descripcion))
                if not resultado:
                    messagebox.showerror("Error", "No se pudo guardar el producto en la base de datos")
                    return
                messagebox.showinfo("Éxito", "Producto agregado correctamente")
                producto_window.destroy()
                self.mostrar_inventario()
                
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese valores válidos")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar producto: {str(e)}")
        
        # Botones
        btn_guardar = tk.Button(botones_frame, text="✓ GUARDAR", command=guardar_producto,
                               bg="#27AE60", fg="white", font=("Arial", 12, "bold"),
                               height=2, cursor="hand2")
        btn_guardar.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        btn_cancelar = tk.Button(botones_frame, text="✗ CANCELAR", command=producto_window.destroy,
                               bg="#E74C3C", fg="white", font=("Arial", 12, "bold"),
                               height=2, cursor="hand2")
        btn_cancelar.pack(side="left", padx=5, pady=5, expand=True, fill="x")
    
    def editar_producto(self):
        """Edita un producto seleccionado"""
        # Verificar permisos
        if not self.verificar_permiso_accion('editar_producto'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para editar productos")
            return
            
        seleccion = self.tabla_productos.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto")
            return
        
        item = self.tabla_productos.item(seleccion[0])
        producto_data = item['values']
        
        # Crear ventana para editar producto
        producto_window = tk.Toplevel(self.root)
        producto_window.title("Editar Producto")
        producto_window.geometry("500x500")
        producto_window.configure(bg="#ECF0F1")
        
        # Frame principal
        main_frame = tk.Frame(producto_window, bg="#ECF0F1", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Campos del formulario
        campos = [
            ("Nombre:", "entry_nombre"),
            ("Categoría:", "entry_categoria"),
            ("Precio (S/):", "entry_precio"),
            ("Stock:", "entry_stock"),
            ("Stock Mínimo:", "entry_stock_minimo"),
            ("Descripción:", "entry_descripcion")
        ]
        
        entries = {}
        
        for i, (label, nombre) in enumerate(campos):
            tk.Label(main_frame, text=label, bg="#ECF0F1", font=("Arial", 12)).pack(pady=(10, 5), anchor="w")
            
            if nombre == "entry_categoria":
                # Obtener categorías existentes
                query = "SELECT DISTINCT categoria FROM productos"
                categorias_result = self.db_manager.ejecutar_query(query)
                categorias = [cat[0] for cat in categorias_result] if categorias_result else []
                
                entry = ttk.Combobox(main_frame, values=categorias, font=("Arial", 12))
                entry.pack(pady=(0, 10), padx=20, fill="x")
            elif nombre == "entry_descripcion":
                entry = tk.Text(main_frame, height=4, font=("Arial", 12))
                entry.pack(pady=(0, 10), padx=20, fill="x")
            else:
                entry = tk.Entry(main_frame, font=("Arial", 12))
                entry.pack(pady=(0, 10), padx=20, fill="x")
                
            entries[nombre] = entry
        
        # Llenar campos con datos actuales
        entries["entry_nombre"].insert(0, producto_data[1])
        entries["entry_categoria"].set(producto_data[2])
        entries["entry_precio"].insert(0, str(producto_data[3].replace("S/ ", "")))
        entries["entry_stock"].insert(0, str(producto_data[4]))
        entries["entry_stock_minimo"].insert(0, str(producto_data[5]))
        
        # Obtener descripción actual
        query = "SELECT descripcion FROM productos WHERE id = %s"
        resultado = self.db_manager.ejecutar_query(query, (producto_data[0],))
        if resultado and resultado[0][0]:
            entries["entry_descripcion"].insert("1.0", resultado[0][0])
        
        # Frame de botones
        botones_frame = tk.Frame(producto_window, bg="#ECF0F1")
        botones_frame.pack(side="bottom", fill="x", pady=10, padx=10)
        
        # Función para actualizar producto
        def actualizar_producto():
            try:
                nombre = entries["entry_nombre"].get()
                categoria = entries["entry_categoria"].get()
                precio = float(entries["entry_precio"].get())
                stock = int(entries["entry_stock"].get())
                stock_minimo = int(entries["entry_stock_minimo"].get())
                descripcion = entries["entry_descripcion"].get("1.0", tk.END).strip()
                
                if not all([nombre, categoria, precio, stock]):
                    messagebox.showerror("Error", "Por favor complete los campos obligatorios")
                    return
                
                query = """
                    UPDATE productos 
                    SET nombre=%s, categoria=%s, precio=%s, stock=%s, stock_minimo=%s, descripcion=%s
                    WHERE id=%s
                """
                self.db_manager.ejecutar_query(query, (nombre, categoria, precio, stock, stock_minimo, descripcion, producto_data[0]))
                
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                producto_window.destroy()
                self.mostrar_inventario()
                
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese valores válidos")
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar producto: {str(e)}")
        
        # Botones
        btn_actualizar = tk.Button(botones_frame, text="✓ ACTUALIZAR", command=actualizar_producto,
                                  bg="#3498DB", fg="white", font=("Arial", 12, "bold"),
                                  height=2, cursor="hand2")
        btn_actualizar.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        btn_cancelar = tk.Button(botones_frame, text="✗ CANCELAR", command=producto_window.destroy,
                               bg="#E74C3C", fg="white", font=("Arial", 12, "bold"),
                               height=2, cursor="hand2")
        btn_cancelar.pack(side="left", padx=5, pady=5, expand=True, fill="x")
    
    def eliminar_producto(self):
        """Elimina un producto seleccionado"""
        # Verificar permisos
        if not self.verificar_permiso_accion('eliminar_producto'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para eliminar productos")
            return
            
        seleccion = self.tabla_productos.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto")
            return
        
        item = self.tabla_productos.item(seleccion[0])
        producto_data = item['values']
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", f"¿Está seguro que desea eliminar el producto {producto_data[1]}?"):
            try:
                query = "DELETE FROM productos WHERE id=%s"
                self.db_manager.ejecutar_query(query, (producto_data[0],))
                
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                self.mostrar_inventario()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar producto: {str(e)}")
    
    def ajustar_stock(self):
        """Ajusta el stock de un producto seleccionado"""
        # Verificar permisos
        if not self.verificar_permiso_accion('editar_producto'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para ajustar stock")
            return
            
        seleccion = self.tabla_productos.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto")
            return
        
        item = self.tabla_productos.item(seleccion[0])
        producto_data = item['values']
        
        # Crear ventana para ajustar stock
        stock_window = tk.Toplevel(self.root)
        stock_window.title("Ajustar Stock")
        stock_window.geometry("400x250")
        stock_window.configure(bg="#ECF0F1")
        
        # Frame principal
        main_frame = tk.Frame(stock_window, bg="#ECF0F1", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Información del producto
        tk.Label(main_frame, text=f"Producto: {producto_data[1]}", 
                font=("Arial", 12, "bold"), bg="#ECF0F1", fg="#2C3E50").pack(pady=(0, 20), anchor="w")
        
        # Stock actual
        tk.Label(main_frame, text=f"Stock Actual: {producto_data[4]}", 
                font=("Arial", 12), bg="#ECF0F1", fg="#2C3E50").pack(pady=(0, 10), anchor="w")
        
        # Campo para nuevo stock
        tk.Label(main_frame, text="Nuevo Stock:", font=("Arial", 12), bg="#ECF0F1", fg="#2C3E50").pack(pady=(10, 5), anchor="w")
        entry_stock = tk.Entry(main_frame, font=("Arial", 12))
        entry_stock.pack(pady=(0, 10), padx=20, fill="x")
        entry_stock.insert(0, str(producto_data[4]))
        
        # Frame de botones
        botones_frame = tk.Frame(stock_window, bg="#ECF0F1")
        botones_frame.pack(side="bottom", fill="x", pady=10, padx=10)
        
        # Función para actualizar stock
        def guardar_stock():
            try:
                nuevo_stock = int(entry_stock.get())
                
                if nuevo_stock < 0:
                    messagebox.showerror("Error", "El stock no puede ser negativo")
                    return
                
                query = "UPDATE productos SET stock=%s WHERE id=%s"
                self.db_manager.ejecutar_query(query, (nuevo_stock, producto_data[0]))
                
                messagebox.showinfo("Éxito", "Stock actualizado correctamente")
                stock_window.destroy()
                self.mostrar_inventario()
                
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese un valor numérico válido")
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar stock: {str(e)}")
        
        # Botones
        btn_guardar = tk.Button(botones_frame, text="✓ GUARDAR", command=guardar_stock,
                               bg="#27AE60", fg="white", font=("Arial", 12, "bold"),
                               height=2, cursor="hand2")
        btn_guardar.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        btn_cancelar = tk.Button(botones_frame, text="✗ CANCELAR", command=stock_window.destroy,
                               bg="#E74C3C", fg="white", font=("Arial", 12, "bold"),
                               height=2, cursor="hand2")
        btn_cancelar.pack(side="left", padx=5, pady=5, expand=True, fill="x")
    
    def buscar_productos(self):
        """Busca productos por nombre"""
        texto_busqueda = self.busqueda_producto_entry.get().strip()
        
        if not texto_busqueda:
            self.mostrar_inventario()
            return
        
        # Limpiar tabla
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
        
        try:
            query = "SELECT id, nombre, categoria, precio, stock, stock_minimo FROM productos WHERE nombre LIKE %s ORDER BY nombre"
            productos = self.db_manager.ejecutar_query(query, (f"%{texto_busqueda}%",))
            
            if productos:
                # Agregar productos a la tabla
                for producto in productos:
                    # Colorear según stock
                    tags = ("stock_bajo",) if producto[4] <= producto[5] else ("",)
                    
                    self.tabla_productos.insert("", "end", values=(
                        producto[0],  # ID
                        producto[1],  # Nombre
                        producto[2],  # Categoría
                        f"S/ {producto[3]:.2f}",  # Precio
                        producto[4],  # Stock
                        producto[5]   # Stock Mínimo
                    ), tags=tags)
                
                # Configurar colores
                self.tabla_productos.tag_configure("stock_bajo", background="#FADBD8", foreground="#E74C3C")
            else:
                messagebox.showinfo("Información", "No se encontraron productos con ese nombre")
        
        except Exception as e:
            print(f"Error buscando productos: {e}")
    
    def filtrar_productos(self):
        """Filtra productos por categoría"""
        categoria = self.categoria_var.get()
        
        # Limpiar tabla
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
        
        try:
            if categoria == "Todas":
                query = "SELECT id, nombre, categoria, precio, stock, stock_minimo FROM productos ORDER BY nombre"
                productos = self.db_manager.ejecutar_query(query)
            else:
                query = "SELECT id, nombre, categoria, precio, stock, stock_minimo FROM productos WHERE categoria = %s ORDER BY nombre"
                productos = self.db_manager.ejecutar_query(query, (categoria,))
            
            if productos:
                # Agregar productos a la tabla
                for producto in productos:
                    # Colorear según stock
                    tags = ("stock_bajo",) if producto[4] <= producto[5] else ("",)
                    
                    self.tabla_productos.insert("", "end", values=(
                        producto[0],  # ID
                        producto[1],  # Nombre
                        producto[2],  # Categoría
                        f"S/ {producto[3]:.2f}",  # Precio
                        producto[4],  # Stock
                        producto[5]   # Stock Mínimo
                    ), tags=tags)
                
                # Configurar colores
                self.tabla_productos.tag_configure("stock_bajo", background="#FADBD8", foreground="#E74C3C")
            else:
                messagebox.showinfo("Información", f"No se encontraron productos en la categoría {categoria}")
        
        except Exception as e:
            print(f"Error filtrando productos: {e}")
    
    def exportar_productos(self):
        """Exporta los productos a un archivo"""
        try:
            # Obtener productos
            productos = self.models['producto'].obtener_todos()
            
            if not productos:
                messagebox.showinfo("Información", "No hay productos para exportar")
                return
            
            # Seleccionar archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Exportar Productos"
            )
            
            if not filename:
                return
            
            # Exportar a CSV
            import csv
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Escribir encabezados
                writer.writerow(['ID', 'Nombre', 'Categoría', 'Precio', 'Stock', 'Stock Mínimo'])
                
                # Escribir datos
                for producto in productos:
                    writer.writerow([
                        producto[0],  # ID
                        producto[1],  # Nombre
                        producto[2],  # Categoría
                        producto[3],  # Precio
                        producto[4],  # Stock
                        producto[5]   # Stock Mínimo
                    ])
            
            messagebox.showinfo("Éxito", f"Productos exportados correctamente a {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar productos: {str(e)}")
    
    def mostrar_clientes(self):
        """Muestra la pantalla de clientes"""
        # Verificar permisos de acceso
        if not self.verificar_permiso('clientes'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para acceder a clientes")
            return
            
        # Limpiar frame de contenido
        for widget in self.contenido_frame.winfo_children():
            widget.destroy()
        
        # Título
        titulo_frame = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        titulo_frame.pack(fill="x")
        
        tk.Label(titulo_frame, text="Gestión de Clientes", font=("Arial", 18, "bold"), 
               bg="#ECF0F1", fg="#2C3E50").pack(side="left", anchor="w")
        
        # Botones de acción con control de permisos
        if self.verificar_permiso_accion('crear_cliente'):
            btn_nuevo = tk.Button(titulo_frame, text="Nuevo Cliente", font=("Arial", 10, "bold"),
                                bg="#27AE60", fg="white", padx=10, pady=5,
                                command=self.crear_nuevo_cliente)
            btn_nuevo.pack(side="right", padx=5)
        
        # Frame de contenido
        contenido = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        contenido.pack(fill="both", expand=True)
        
        # Frame de búsqueda
        busqueda_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        busqueda_frame.pack(fill="x", pady=10)
        
        # Etiqueta de búsqueda
        tk.Label(busqueda_frame, text="Buscar clientes:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").pack(side="left", padx=5)
        
        # Campo de búsqueda
        self.busqueda_cliente_entry = tk.Entry(busqueda_frame, font=("Arial", 10), width=30)
        self.busqueda_cliente_entry.pack(side="left", padx=5)
        
        # Botón de búsqueda
        btn_buscar = tk.Button(busqueda_frame, text="Buscar", font=("Arial", 10),
                             bg="#3498DB", fg="white", padx=10,
                             command=self.buscar_clientes)
        btn_buscar.pack(side="left", padx=5)
        
        # Tabla de clientes
        tabla_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        tabla_frame.pack(fill="both", expand=True, pady=10)
        
        # Obtener clientes
        clientes = self.models['cliente'].obtener_todos()
        
        # Crear tabla con ordenación y multi-selección
        self.tabla_clientes = ttk.Treeview(
            tabla_frame,
            columns=("id", "nombre", "email", "telefono"),
            show="headings",
            selectmode="extended",
        )
        self.tabla_clientes.pack(fill="both", expand=True)
        
        # Configurar columnas con ordenación al hacer clic
        self.tabla_clientes.heading("id", text="ID", command=lambda: self.ordenar_columna(self.tabla_clientes, "id", False))
        self.tabla_clientes.heading("nombre", text="Nombre", command=lambda: self.ordenar_columna(self.tabla_clientes, "nombre", False))
        self.tabla_clientes.heading("email", text="Email", command=lambda: self.ordenar_columna(self.tabla_clientes, "email", False))
        self.tabla_clientes.heading("telefono", text="Teléfono", command=lambda: self.ordenar_columna(self.tabla_clientes, "telefono", False))
        
        self.tabla_clientes.column("id", width=50)
        self.tabla_clientes.column("nombre", width=200)
        self.tabla_clientes.column("email", width=200)
        self.tabla_clientes.column("telefono", width=100)
        
        # Insertar datos
        if clientes:
            for cliente in clientes:
                self.tabla_clientes.insert("", "end", values=(
                    cliente[0],  # ID
                    cliente[1],  # Nombre
                    cliente[2] if cliente[2] else "",  # Email
                    cliente[3] if cliente[3] else ""   # Teléfono
                ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla_clientes.yview)
        self.tabla_clientes.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Frame de botones de acción
        acciones_frame = tk.Frame(contenido, bg="#ECF0F1")
        acciones_frame.pack(fill="x", pady=10)
        
        if self.verificar_permiso_accion('editar_cliente'):
            btn_editar = tk.Button(acciones_frame, text="Editar", font=("Arial", 10),
                                 bg="#3498DB", fg="white", padx=10, pady=5,
                                 command=self.editar_cliente)
            btn_editar.pack(side="left", padx=5)
        
        if self.verificar_permiso_accion('eliminar_cliente'):
            btn_eliminar = tk.Button(acciones_frame, text="Eliminar", font=("Arial", 10),
                                   bg="#E74C3C", fg="white", padx=10, pady=5,
                                   command=self.eliminar_cliente)
            btn_eliminar.pack(side="left", padx=5)
        
        btn_exportar = tk.Button(acciones_frame, text="Exportar", font=("Arial", 10),
                               bg="#2C3E50", fg="white", padx=10, pady=5,
                               command=self.exportar_clientes)
        btn_exportar.pack(side="right", padx=5)
    
    def crear_nuevo_cliente(self):
        """Crea un nuevo cliente"""
        # Verificar permisos
        if not self.verificar_permiso_accion('crear_cliente'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para crear clientes")
            return
            
        # Crear ventana para nuevo cliente
        cliente_window = tk.Toplevel(self.root)
        cliente_window.title("Nuevo Cliente")
        cliente_window.geometry("400x350")
        cliente_window.configure(bg="#ECF0F1")
        
        # Frame principal
        main_frame = tk.Frame(cliente_window, bg="#ECF0F1", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Campos del formulario
        campos = [
            ("Nombre:", "entry_nombre"),
            ("Email:", "entry_email"),
            ("Teléfono:", "entry_telefono")
        ]
        
        entries = {}
        
        for i, (label, nombre) in enumerate(campos):
            tk.Label(main_frame, text=label, bg="#ECF0F1", font=("Arial", 12)).pack(pady=(10, 5), anchor="w")
            
            entry = tk.Entry(main_frame, font=("Arial", 12))
            entry.pack(pady=(0, 10), padx=20, fill="x")
            
            entries[nombre] = entry
        
        # Frame de botones
        botones_frame = tk.Frame(cliente_window, bg="#ECF0F1")
        botones_frame.pack(side="bottom", fill="x", pady=10, padx=10)
        
        # Función para guardar cliente
        def guardar_cliente():
            try:
                nombre = entries["entry_nombre"].get()
                email = entries["entry_email"].get()
                telefono = entries["entry_telefono"].get()
                
                if not nombre:
                    messagebox.showerror("Error", "Por favor complete el campo nombre")
                    return
                
                query = """
                    INSERT INTO clientes (nombre, email, telefono)
                    VALUES (%s, %s, %s)
                """
                self.db_manager.ejecutar_query(query, (nombre, email, telefono))
                
                messagebox.showinfo("Éxito", "Cliente agregado correctamente")
                cliente_window.destroy()
                self.mostrar_clientes()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar cliente: {str(e)}")
        
        # Botones
        btn_guardar = tk.Button(botones_frame, text="✓ GUARDAR", command=guardar_cliente,
                               bg="#27AE60", fg="white", font=("Arial", 12, "bold"),
                               height=2, cursor="hand2")
        btn_guardar.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        btn_cancelar = tk.Button(botones_frame, text="✗ CANCELAR", command=cliente_window.destroy,
                               bg="#E74C3C", fg="white", font=("Arial", 12, "bold"),
                               height=2, cursor="hand2")
        btn_cancelar.pack(side="left", padx=5, pady=5, expand=True, fill="x")
    
    def editar_cliente(self):
        """Edita un cliente seleccionado"""
        # Verificar permisos
        if not self.verificar_permiso_accion('editar_cliente'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para editar clientes")
            return
            
        seleccion = self.tabla_clientes.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente")
            return
        
        item = self.tabla_clientes.item(seleccion[0])
        cliente_data = item['values']
        
        # Crear ventana para editar cliente
        cliente_window = tk.Toplevel(self.root)
        cliente_window.title("Editar Cliente")
        cliente_window.geometry("400x350")
        cliente_window.configure(bg="#ECF0F1")
        
        # Frame principal
        main_frame = tk.Frame(cliente_window, bg="#ECF0F1", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Campos del formulario
        campos = [
            ("Nombre:", "entry_nombre"),
            ("Email:", "entry_email"),
            ("Teléfono:", "entry_telefono")
        ]
        
        entries = {}
        
        for i, (label, nombre) in enumerate(campos):
            tk.Label(main_frame, text=label, bg="#ECF0F1", font=("Arial", 12)).pack(pady=(10, 5), anchor="w")
            
            entry = tk.Entry(main_frame, font=("Arial", 12))
            if i < len(cliente_data) - 1:  # -1 porque no incluimos el ID
                entry.insert(0, str(cliente_data[i+1]))
            entry.pack(pady=(0, 10), padx=20, fill="x")
            
            entries[nombre] = entry
        
        # Frame de botones
        botones_frame = tk.Frame(cliente_window, bg="#ECF0F1")
        botones_frame.pack(side="bottom", fill="x", pady=10, padx=10)
        
        # Función para actualizar cliente
        def actualizar_cliente():
            try:
                nombre = entries["entry_nombre"].get()
                email = entries["entry_email"].get()
                telefono = entries["entry_telefono"].get()
                
                if not nombre:
                    messagebox.showerror("Error", "Por favor complete el campo nombre")
                    return
                
                query = """
                    UPDATE clientes 
                    SET nombre=%s, email=%s, telefono=%s
                    WHERE id=%s
                """
                self.db_manager.ejecutar_query(query, (nombre, email, telefono, cliente_data[0]))
                
                messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                cliente_window.destroy()
                self.mostrar_clientes()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar cliente: {str(e)}")
        
        # Botones
        btn_actualizar = tk.Button(botones_frame, text="✓ ACTUALIZAR", command=actualizar_cliente,
                                  bg="#3498DB", fg="white", font=("Arial", 12, "bold"),
                                  height=2, cursor="hand2")
        btn_actualizar.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        btn_cancelar = tk.Button(botones_frame, text="✗ CANCELAR", command=cliente_window.destroy,
                               bg="#E74C3C", fg="white", font=("Arial", 12, "bold"),
                               height=2, cursor="hand2")
        btn_cancelar.pack(side="left", padx=5, pady=5, expand=True, fill="x")
    
    def eliminar_cliente(self):
        """Elimina un cliente seleccionado"""
        # Verificar permisos
        if not self.verificar_permiso_accion('eliminar_cliente'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para eliminar clientes")
            return
            
        seleccion = self.tabla_clientes.selection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente")
            return
        
        item = self.tabla_clientes.item(seleccion[0])
        cliente_data = item['values']
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", f"¿Está seguro que desea eliminar al cliente {cliente_data[1]}?"):
            try:
                query = "DELETE FROM clientes WHERE id=%s"
                self.db_manager.ejecutar_query(query, (cliente_data[0],))
                
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                self.mostrar_clientes()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar cliente: {str(e)}")
    
    def buscar_clientes(self):
        """Busca clientes por nombre"""
        texto_busqueda = self.busqueda_cliente_entry.get().strip()
        
        if not texto_busqueda:
            self.mostrar_clientes()
            return
        
        # Limpiar tabla
        for item in self.tabla_clientes.get_children():
            self.tabla_clientes.delete(item)
        
        try:
            query = "SELECT id, nombre, email, telefono FROM clientes WHERE nombre LIKE %s ORDER BY nombre"
            clientes = self.db_manager.ejecutar_query(query, (f"%{texto_busqueda}%",))
            
            if clientes:
                # Agregar clientes a la tabla
                for cliente in clientes:
                    self.tabla_clientes.insert("", "end", values=(
                        cliente[0],  # ID
                        cliente[1],  # Nombre
                        cliente[2] if cliente[2] else "",  # Email
                        cliente[3] if cliente[3] else ""   # Teléfono
                    ))
            else:
                messagebox.showinfo("Información", "No se encontraron clientes con ese nombre")
        
        except Exception as e:
            print(f"Error buscando clientes: {e}")
    
    def exportar_clientes(self):
        """Exporta los clientes a un archivo"""
        try:
            # Obtener clientes
            clientes = self.models['cliente'].obtener_todos()
            
            if not clientes:
                messagebox.showinfo("Información", "No hay clientes para exportar")
                return
            
            # Seleccionar archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Exportar Clientes"
            )
            
            if not filename:
                return
            
            # Exportar a CSV
            import csv
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Escribir encabezados
                writer.writerow(['ID', 'Nombre', 'Email', 'Teléfono'])
                
                # Escribir datos
                for cliente in clientes:
                    writer.writerow([
                        cliente[0],  # ID
                        cliente[1],  # Nombre
                        cliente[2] if cliente[2] else "",  # Email
                        cliente[3] if cliente[3] else ""   # Teléfono
                    ])
            
            messagebox.showinfo("Éxito", f"Clientes exportados correctamente a {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar clientes: {str(e)}")
    
    def mostrar_reportes(self):
        """Muestra la pantalla de reportes"""
        # Verificar permisos de acceso
        if not self.verificar_permiso('reportes'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para acceder a los reportes")
            return
            
        # Limpiar frame de contenido
        for widget in self.contenido_frame.winfo_children():
            widget.destroy()
        
        # Título
        titulo_frame = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        titulo_frame.pack(fill="x")
        
        tk.Label(titulo_frame, text="Reportes del Sistema", font=("Arial", 18, "bold"), 
               bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        # Frame de contenido
        contenido = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        contenido.pack(fill="both", expand=True)
        
        # Panel lateral de controles (vertical)
        control_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1, width=300)
        control_frame.pack(side="left", fill="y", pady=10)
        control_frame.pack_propagate(False)
        
        tk.Label(control_frame, text="Seleccione el tipo de reporte:", font=("Arial", 12, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        # Botones de reportes (vertical)
        btn_style = {"font": ("Arial", 11), "bg": "#3498DB", "fg": "white", 
                    "padx": 12, "pady": 8, "relief": "flat"}
        
        tk.Button(control_frame, text="Ventas Diarias", 
                  command=lambda: self.seleccionar_tipo_reporte("diario"), **btn_style).pack(fill="x", pady=5)
        tk.Button(control_frame, text="Ventas Mensuales", 
                  command=lambda: self.seleccionar_tipo_reporte("mensual"), **btn_style).pack(fill="x", pady=5)
        tk.Button(control_frame, text="Productos Más Vendidos", 
                  command=lambda: self.seleccionar_tipo_reporte("productos"), **btn_style).pack(fill="x", pady=5)
        tk.Button(control_frame, text="Inventario Actual", 
                  command=lambda: self.seleccionar_tipo_reporte("inventario"), **btn_style).pack(fill="x", pady=5)
        tk.Button(control_frame, text="Clientes Frecuentes", 
                  command=lambda: self.seleccionar_tipo_reporte("clientes"), **btn_style).pack(fill="x", pady=5)
        
        # Configuración de reportes
        tk.Label(control_frame, text="Configuración del Reporte:", font=("Arial", 12, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w", pady=(15, 10))
        
        # Rango de fechas (vertical)
        fechas_frame = tk.Frame(control_frame, bg="white")
        fechas_frame.pack(fill="x", pady=5)
        tk.Label(fechas_frame, text="Desde:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w")
        self.desde_entry = tk.Entry(fechas_frame, font=("Arial", 10), width=14)
        self.desde_entry.pack(fill="x", padx=5)
        self.desde_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        tk.Label(fechas_frame, text="Hasta:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w", pady=(8, 0))
        self.hasta_entry = tk.Entry(fechas_frame, font=("Arial", 10), width=14)
        self.hasta_entry.pack(fill="x", padx=5)
        self.hasta_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        
        # Formato de salida
        formato_frame = tk.Frame(control_frame, bg="white")
        formato_frame.pack(fill="x", pady=10)
        tk.Label(formato_frame, text="Formato de salida:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w")
        formatos = ["PDF", "Excel", "CSV"]
        self.formato_var = tk.StringVar(value=formatos[0])
        formato_menu = ttk.Combobox(formato_frame, textvariable=self.formato_var, values=formatos, 
                                  font=("Arial", 10), state="readonly")
        formato_menu.pack(fill="x", padx=5)
        
        # Opciones de vista previa
        opciones_preview_frame = tk.Frame(control_frame, bg="white")
        opciones_preview_frame.pack(fill="x", pady=6)
        self.mostrar_graficos_var = tk.BooleanVar(value=False)
        tk.Checkbutton(opciones_preview_frame, text="Mostrar gráficos",
                       variable=self.mostrar_graficos_var, bg="white").pack(anchor="w", padx=5)
        
        # Botones de acción (ahora en una sola fila para ahorrar altura)
        acciones_frame = tk.Frame(control_frame, bg="white")
        acciones_frame.pack(fill="x", pady=10)
        btn_vista = tk.Button(acciones_frame, text="Vista Previa", font=("Arial", 10),
                              bg="#3498DB", fg="white", padx=12, pady=6,
                              command=self.mostrar_vista_previa)
        btn_vista.pack(side="left", expand=True, fill="x", padx=(0,5))
        btn_generar = tk.Button(acciones_frame, text="Generar Reporte", font=("Arial", 10, "bold"),
                                bg="#27AE60", fg="white", padx=12, pady=6,
                                command=self.generar_reporte)
        btn_generar.pack(side="left", expand=True, fill="x", padx=(5,0))
        
        # Contenedor de vista previa con scroll
        preview_outer = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        preview_outer.pack(side="left", fill="both", expand=True, pady=10, padx=10)
        
        self.preview_canvas = tk.Canvas(preview_outer, bg="white")
        preview_scrollbar = ttk.Scrollbar(preview_outer, orient="vertical", command=self.preview_canvas.yview)
        self.preview_frame = tk.Frame(self.preview_canvas, bg="white")
        
        self.preview_frame.bind("<Configure>", lambda e: self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all")))
        self.preview_window = self.preview_canvas.create_window((0, 0), window=self.preview_frame, anchor="nw")
        # Ajustar ancho del contenido y redimensionar gráficos según el canvas
        self.preview_canvas.bind("<Configure>", lambda e: (self.preview_canvas.itemconfigure(self.preview_window, width=e.width), getattr(self, "_ajustar_graficos_ancho", lambda *_: None)(e.width)))
        self.preview_canvas.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_canvas.pack(side="left", fill="both", expand=True)
        preview_scrollbar.pack(side="right", fill="y")
        
        # Frame para gráficos dentro de la vista previa
        self.graficos_frame = tk.Frame(self.preview_frame, bg="white")
        
        # Variables para almacenar el tipo de reporte seleccionado
        self.tipo_reporte_actual = None
    
    def mostrar_configuracion(self):
        """Muestra la pantalla de configuración"""
        # Verificar permisos de acceso
        if not self.verificar_permiso('configuracion'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para acceder a la configuración")
            return
            
        # Limpiar frame de contenido
        for widget in self.contenido_frame.winfo_children():
            widget.destroy()
        
        # Título
        titulo_frame = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        titulo_frame.pack(fill="x")
        
        tk.Label(titulo_frame, text="Configuración del Sistema", font=("Arial", 18, "bold"), 
               bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        # Frame de contenido
        contenido = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        contenido.pack(fill="both", expand=True)
        
        # Obtener configuración actual
        config = self.models['configuracion'].obtener_configuracion()
        
        # Configuración general
        general_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        general_frame.pack(fill="x", pady=10)
        
        tk.Label(general_frame, text="Configuración General", font=("Arial", 12, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        # Nombre del negocio
        nombre_frame = tk.Frame(general_frame, bg="white")
        nombre_frame.pack(fill="x", pady=5)
        
        tk.Label(nombre_frame, text="Nombre del Negocio:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50", width=20, anchor="w").pack(side="left", padx=5)
        
        nombre_entry = tk.Entry(nombre_frame, font=("Arial", 10), width=40)
        nombre_entry.pack(side="left", padx=5, fill="x", expand=True)
        if config and 'cafeteria_nombre' in config:
            nombre_entry.insert(0, config['cafeteria_nombre'])
        
        # Dirección
        direccion_frame = tk.Frame(general_frame, bg="white")
        direccion_frame.pack(fill="x", pady=5)
        
        tk.Label(direccion_frame, text="Dirección:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50", width=20, anchor="w").pack(side="left", padx=5)
        
        direccion_entry = tk.Entry(direccion_frame, font=("Arial", 10), width=40)
        direccion_entry.pack(side="left", padx=5, fill="x", expand=True)
        if config and 'cafeteria_direccion' in config:
            direccion_entry.insert(0, config['cafeteria_direccion'])
        
        # Teléfono
        telefono_frame = tk.Frame(general_frame, bg="white")
        telefono_frame.pack(fill="x", pady=5)
        
        tk.Label(telefono_frame, text="Teléfono:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50", width=20, anchor="w").pack(side="left", padx=5)
        
        telefono_entry = tk.Entry(telefono_frame, font=("Arial", 10), width=20)
        telefono_entry.pack(side="left", padx=5)
        if config and 'cafeteria_telefono' in config:
            telefono_entry.insert(0, config['cafeteria_telefono'])
        
        # Email
        email_frame = tk.Frame(general_frame, bg="white")
        email_frame.pack(fill="x", pady=5)
        
        tk.Label(email_frame, text="Email:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50", width=20, anchor="w").pack(side="left", padx=5)
        
        email_entry = tk.Entry(email_frame, font=("Arial", 10), width=30)
        email_entry.pack(side="left", padx=5)
        if config and 'cafeteria_email' in config:
            email_entry.insert(0, config['cafeteria_email'])
        
        # Configuración de impuestos
        impuestos_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        impuestos_frame.pack(fill="x", pady=10)
        
        tk.Label(impuestos_frame, text="Configuración de Impuestos", font=("Arial", 12, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        # IGV
        igv_frame = tk.Frame(impuestos_frame, bg="white")
        igv_frame.pack(fill="x", pady=5)
        
        tk.Label(igv_frame, text="IGV (%):", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50", width=20, anchor="w").pack(side="left", padx=5)
        
        igv_entry = tk.Entry(igv_frame, font=("Arial", 10), width=10)
        igv_entry.pack(side="left", padx=5)
        if config and 'igv' in config:
            igv_entry.insert(0, config['igv'])
        else:
            igv_entry.insert(0, "18")
        
        # Configuración de copias de seguridad
        backup_frame = tk.Frame(contenido, bg="white", padx=15, pady=15, relief="solid", bd=1)
        backup_frame.pack(fill="x", pady=10)
        
        tk.Label(backup_frame, text="Copias de Seguridad", font=("Arial", 12, "bold"), 
               bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        # Ruta de backup
        ruta_frame = tk.Frame(backup_frame, bg="white")
        ruta_frame.pack(fill="x", pady=5)
        
        tk.Label(ruta_frame, text="Ruta de Backup:", font=("Arial", 10, "bold"), 
               bg="white", fg="#2C3E50", width=20, anchor="w").pack(side="left", padx=5)
        
        ruta_entry = tk.Entry(ruta_frame, font=("Arial", 10), width=40)
        ruta_entry.pack(side="left", padx=5, fill="x", expand=True)
        if config and 'ruta_backup' in config:
            ruta_entry.insert(0, config['ruta_backup'])
        else:
            ruta_entry.insert(0, "./backups/")
        
        btn_examinar = tk.Button(ruta_frame, text="Examinar", font=("Arial", 9),
                               bg="#3498DB", fg="white", padx=5)
        btn_examinar.pack(side="left", padx=5)
        
        # Botones de acción
        btn_frame = tk.Frame(backup_frame, bg="white")
        btn_frame.pack(fill="x", pady=10)
        
        # Solo mostrar botones de backup/restaurar si tiene permisos
        if self.verificar_permiso_accion('configurar_sistema'):
            btn_backup = tk.Button(btn_frame, text="Realizar Backup Ahora", font=("Arial", 10),
                                 bg="#3498DB", fg="white", padx=10, pady=5)
            btn_backup.pack(side="left", padx=5)
            
            btn_restaurar = tk.Button(btn_frame, text="Restaurar Backup", font=("Arial", 10),
                                    bg="#E74C3C", fg="white", padx=10, pady=5)
            btn_restaurar.pack(side="left", padx=5)
        
        # Botones de guardar
        acciones_frame = tk.Frame(contenido, bg="#ECF0F1")
        acciones_frame.pack(fill="x", pady=10)
        
        # Solo mostrar botón guardar si tiene permisos
        if self.verificar_permiso_accion('configurar_sistema'):
            btn_guardar = tk.Button(acciones_frame, text="Guardar Configuración", font=("Arial", 10, "bold"),
                                  bg="#27AE60", fg="white", padx=15, pady=5)
            btn_guardar.pack(side="right", padx=5)
        
        btn_cancelar = tk.Button(acciones_frame, text="Cancelar", font=("Arial", 10),
                               bg="#7F8C8D", fg="white", padx=15, pady=5)
        btn_cancelar.pack(side="right", padx=5)
    
    def mostrar_acerca_de(self):
        """Muestra la pantalla de acerca de"""
        # Verificar permisos de acceso
        if not self.verificar_permiso('acerca_de'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para acceder a esta sección")
            return
            
        # Limpiar frame de contenido
        for widget in self.contenido_frame.winfo_children():
            widget.destroy()
        
        # Título
        titulo_frame = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        titulo_frame.pack(fill="x")
        
        tk.Label(titulo_frame, text="Acerca de Nexus Coffee", font=("Arial", 18, "bold"), 
               bg="#ECF0F1", fg="#2C3E50").pack(anchor="w")
        
        # Frame de contenido
        contenido = tk.Frame(self.contenido_frame, bg="#ECF0F1", padx=20, pady=10)
        contenido.pack(fill="both", expand=True)
        
        # Información del sistema
        info_frame = tk.Frame(contenido, bg="white", padx=20, pady=20, relief="solid", bd=1)
        info_frame.pack(fill="both", expand=True, pady=10)
        
        # Logo
        try:
            logo_img = Image.open("./resources/logo.png")
            logo_img = logo_img.resize((150, 150), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            
            logo_label = tk.Label(info_frame, image=logo_photo, bg="white")
            logo_label.image = logo_photo  # Mantener una referencia
            logo_label.pack(pady=20)
        except:
            # Si no hay logo, mostrar un texto
            tk.Label(info_frame, text="NEXUS COFFEE", font=("Arial", 24, "bold"), 
                   bg="white", fg="#2C3E50").pack(pady=20)
        
        # Versión
        tk.Label(info_frame, text="Versión 1.0.0", font=("Arial", 12), 
               bg="white", fg="#7F8C8D").pack(pady=5)
        
        # Descripción
        tk.Label(info_frame, text="Sistema de Gestión Integral para Cafeterías", 
               font=("Arial", 12), bg="white", fg="#2C3E50").pack(pady=5)
        
        # Derechos
        tk.Label(info_frame, text="© 2023 Nexus Coffee. Todos los derechos reservados.", 
               font=("Arial", 10), bg="white", fg="#7F8C8D").pack(pady=20)
        
        # Frame de botones
        botones_frame = tk.Frame(contenido, bg="#ECF0F1")
        botones_frame.pack(fill="x", pady=10)
        
        # Botón de cerrar
        btn_cerrar = tk.Button(botones_frame, text="Cerrar", font=("Arial", 10),
                             bg="#3498DB", fg="white", padx=15, pady=5,
                             command=lambda: self.mostrar_resumen())
        btn_cerrar.pack(side="right", padx=5)
    
    def cerrar_sesion(self):
        """Cierra la sesión actual y muestra el login"""
        self.usuario_actual = None
        self.mostrar_login()
    
    def seleccionar_tipo_reporte(self, tipo):
        """Selecciona el tipo de reporte y ajusta las fechas automáticamente"""
        self.tipo_reporte_actual = tipo

        # Ajustar fechas según el tipo de reporte
        hoy = datetime.datetime.now()

        try:
            desde_widget_ok = hasattr(self, "desde_entry") and self.desde_entry.winfo_exists()
            hasta_widget_ok = hasattr(self, "hasta_entry") and self.hasta_entry.winfo_exists()

            if tipo == "diario":
                fecha_actual = hoy.strftime("%Y-%m-%d")
                if desde_widget_ok:
                    self.desde_entry.delete(0, tk.END)
                    self.desde_entry.insert(0, fecha_actual)
                if hasta_widget_ok:
                    self.hasta_entry.delete(0, tk.END)
                    self.hasta_entry.insert(0, fecha_actual)

            elif tipo == "mensual":
                primer_dia = hoy.replace(day=1).strftime("%Y-%m-%d")
                if desde_widget_ok:
                    self.desde_entry.delete(0, tk.END)
                    self.desde_entry.insert(0, primer_dia)
                if hasta_widget_ok:
                    self.hasta_entry.delete(0, tk.END)
                    self.hasta_entry.insert(0, hoy.strftime("%Y-%m-%d"))
        except Exception:
            # Si algo falla al manipular los widgets, continuamos sin bloquear la vista previa
            pass

        # Mostrar vista previa automáticamente
        self.mostrar_vista_previa()
    
    def mostrar_vista_previa(self):
        """Muestra una vista previa del reporte seleccionado"""
        if not self.tipo_reporte_actual:
            messagebox.showinfo("Información", "Por favor seleccione un tipo de reporte primero")
            return
        
        # Limpiar el frame de vista previa
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        # La vista previa se muestra dentro del Canvas con scroll; no requiere pack explícito
        
        # Crear un frame para la tabla de datos
        tabla_frame = tk.Frame(self.preview_frame, bg="white")
        tabla_frame.pack(fill="both", expand=True, pady=5)
        
        # Crear un frame para los gráficos (se empaqueta solo si se muestran)
        self.graficos_frame = tk.Frame(self.preview_frame, bg="white")
        # Reiniciar lista de canvases de gráficos
        self._graficos_canvases = []
        
        try:
            # Obtener datos según el tipo de reporte
            if self.tipo_reporte_actual in ["diario", "mensual"]:
                desde = self.desde_entry.get()
                hasta = self.hasta_entry.get()
                datos = self.models['venta'].obtener_ventas_por_periodo(desde, hasta)
                
                if not datos:
                    tk.Label(tabla_frame, text="No hay datos para mostrar en el período seleccionado", 
                           font=("Arial", 12), bg="white", fg="#E74C3C").pack(pady=20)
                    return
                
                # Crear tabla de ventas
                self.crear_tabla_ventas(tabla_frame, datos)
                
                # Crear gráfico de ventas (opcional)
                if hasattr(self, 'mostrar_graficos_var') and self.mostrar_graficos_var.get():
                    self.crear_grafico_ventas(datos)
                
            elif self.tipo_reporte_actual == "productos":
                datos = self.models['venta'].obtener_productos_mas_vendidos()
                
                if not datos:
                    tk.Label(tabla_frame, text="No hay datos de productos vendidos", 
                           font=("Arial", 12), bg="white", fg="#E74C3C").pack(pady=20)
                    return
                
                # Crear tabla de productos más vendidos
                self.crear_tabla_productos(tabla_frame, datos)
                
                # Crear gráfico de productos más vendidos (opcional)
                if hasattr(self, 'mostrar_graficos_var') and self.mostrar_graficos_var.get():
                    self.crear_grafico_productos(datos)
                
            elif self.tipo_reporte_actual == "inventario":
                datos = self.models['producto'].obtener_todos()
                
                if not datos:
                    tk.Label(tabla_frame, text="No hay productos en el inventario", 
                           font=("Arial", 12), bg="white", fg="#E74C3C").pack(pady=20)
                    return
                
                # Crear tabla de inventario
                self.crear_tabla_inventario(tabla_frame, datos)
                
                # Crear gráfico de inventario (opcional)
                if hasattr(self, 'mostrar_graficos_var') and self.mostrar_graficos_var.get():
                    self.crear_grafico_inventario(datos)
                
            elif self.tipo_reporte_actual == "clientes":
                datos = self.models['cliente'].obtener_clientes_frecuentes()
                
                if not datos:
                    tk.Label(tabla_frame, text="No hay datos de clientes frecuentes", 
                           font=("Arial", 12), bg="white", fg="#E74C3C").pack(pady=20)
                    return
                
                # Crear tabla de clientes
                self.crear_tabla_clientes(tabla_frame, datos)
                
                # Crear gráfico de clientes (opcional)
                if hasattr(self, 'mostrar_graficos_var') and self.mostrar_graficos_var.get():
                    self.crear_grafico_clientes(datos)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar vista previa: {str(e)}")
    
    def generar_reporte(self):
        """Genera un reporte según el tipo seleccionado y el formato elegido"""
        # Verificar permisos
        if not self.verificar_permiso_accion('generar_reportes'):
            messagebox.showerror("Acceso Denegado", "No tiene permisos para generar reportes")
            return
            
        if not self.tipo_reporte_actual:
            messagebox.showinfo("Información", "Por favor seleccione un tipo de reporte primero")
            return
        
        formato = self.formato_var.get()
        
        try:
            # Obtener datos según el tipo de reporte
            if self.tipo_reporte_actual in ["diario", "mensual"]:
                desde = self.desde_entry.get()
                hasta = self.hasta_entry.get()
                datos = self.models['venta'].obtener_ventas_por_periodo(desde, hasta)
                
                if not datos:
                    messagebox.showinfo("Información", "No hay ventas en el período seleccionado")
                    return
                
                if formato == "PDF":
                    self.exportar_pdf_ventas(datos)
                elif formato == "Excel":
                    self.exportar_excel_ventas(datos)
                elif formato == "CSV":
                    self.exportar_csv_ventas(datos)
                
            elif self.tipo_reporte_actual == "productos":
                datos = self.models['venta'].obtener_productos_mas_vendidos()
                
                if not datos:
                    messagebox.showinfo("Información", "No hay datos de productos vendidos")
                    return
                
                if formato == "PDF":
                    self.exportar_pdf_productos(datos)
                elif formato == "Excel":
                    self.exportar_excel_productos(datos)
                elif formato == "CSV":
                    self.exportar_csv_productos(datos)
                
            elif self.tipo_reporte_actual == "inventario":
                datos = self.models['producto'].obtener_todos()
                
                if not datos:
                    messagebox.showinfo("Información", "No hay productos en el inventario")
                    return
                
                if formato == "PDF":
                    self.exportar_pdf_inventario(datos)
                elif formato == "Excel":
                    self.exportar_excel_inventario(datos)
                elif formato == "CSV":
                    self.exportar_csv_inventario(datos)
                
            elif self.tipo_reporte_actual == "clientes":
                datos = self.models['cliente'].obtener_clientes_frecuentes()
                
                if not datos:
                    messagebox.showinfo("Información", "No hay datos de clientes frecuentes")
                    return
                
                if formato == "PDF":
                    self.exportar_pdf_clientes(datos)
                elif formato == "Excel":
                    self.exportar_excel_clientes(datos)
                elif formato == "CSV":
                    self.exportar_csv_clientes(datos)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def generar_reporte_ventas(self, tipo):
        """Método legacy para mantener compatibilidad"""
        self.seleccionar_tipo_reporte(tipo)
        self.generar_reporte()
    
    def generar_reporte_inventario(self):
        """Método legacy para mantener compatibilidad"""
        self.seleccionar_tipo_reporte("inventario")
        self.generar_reporte()
    
    def generar_reporte_productos_mas_vendidos(self):
        """Método legacy para mantener compatibilidad"""
        self.seleccionar_tipo_reporte("productos")
        self.generar_reporte()
    
    def generar_reporte_clientes(self):
        """Método legacy para mantener compatibilidad"""
        self.seleccionar_tipo_reporte("clientes")
        self.generar_reporte()
        
    def ordenar_columna(self, treeview, col, reverse):
        """Función para ordenar una columna del Treeview al hacer clic en el encabezado."""
        try:
            # Extraer datos para la ordenación, manejando formatos de moneda, fechas y números
            def get_key(item):
                value = treeview.set(item, col)
                # Primero, intentar convertir a número (incluye enteros y flotantes)
                try:
                    # Limpiar el valor de cualquier formato de moneda
                    cleaned_value = str(value).replace('S/', '').replace(',', '').strip()
                    return float(cleaned_value)
                except (ValueError, TypeError):
                    # Si falla, intentar convertir a fecha
                    try:
                        return datetime.datetime.strptime(str(value), "%Y-%m-%d %H:%M")
                    except (ValueError, TypeError):
                        # Si falla, tratar como texto
                        return str(value).lower()

            l = [(get_key(k), k) for k in treeview.get_children('')]
            l.sort(key=lambda t: t[0], reverse=reverse)

            # Reorganizar los items en el treeview
            for index, (val, k) in enumerate(l):
                treeview.move(k, '', index)

            # Actualizar el comando del encabezado para el próximo clic (invertir orden)
            treeview.heading(col, command=lambda: self.ordenar_columna(treeview, col, not reverse))
        except Exception as e:
            # Fallback a ordenación de texto simple si todo falla
            try:
                l = [(treeview.set(k, col), k) for k in treeview.get_children('')]
                l.sort(reverse=reverse)
                for index, (val, k) in enumerate(l):
                    treeview.move(k, '', index)
                treeview.heading(col, command=lambda: self.ordenar_columna(treeview, col, not reverse))
            except Exception as final_e:
                print(f"Error fatal al ordenar columna {col}: {final_e}")

    def crear_tabla_ventas(self, parent_frame, datos):
        """Crea una tabla interactiva con los datos de ventas usando Treeview."""
        tabla_container = tk.Frame(parent_frame, bg="white")
        tabla_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        columnas = ("id", "fecha", "cliente", "total", "estado")
        tabla = ttk.Treeview(tabla_container, columns=columnas, show="headings", selectmode="extended")
        
        # Encabezados y configuración de ordenamiento
        encabezados = {"id": "ID", "fecha": "Fecha", "cliente": "Cliente", "total": "Total", "estado": "Estado"}
        for col, texto in encabezados.items():
            tabla.heading(col, text=texto, command=lambda c=col: self.ordenar_columna(tabla, c, False))
            
        # Ancho de columnas
        tabla.column("id", width=50, anchor="center")
        tabla.column("fecha", width=150, anchor="center")
        tabla.column("cliente", width=200, anchor="w")
        tabla.column("total", width=100, anchor="e")
        tabla.column("estado", width=100, anchor="center")
        
        # Insertar datos
        for venta in datos:
            fecha_txt = venta[3].strftime("%Y-%m-%d %H:%M") if hasattr(venta[3], 'strftime') else str(venta[3])
            total_txt = f"S/ {float(venta[2]):.2f}"
            fila = (venta[0], fecha_txt, venta[1], total_txt, "Completada")
            tabla.insert("", "end", values=fila)
            
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_container, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)
        
        return tabla_container

    def crear_tabla_productos(self, parent_frame, datos):
        """Crea una tabla interactiva de productos más vendidos usando Treeview."""
        tabla_container = tk.Frame(parent_frame, bg="white")
        tabla_container.pack(fill="both", expand=True, padx=5, pady=5)

        columnas = ("nombre", "cantidad", "total")
        tabla = ttk.Treeview(tabla_container, columns=columnas, show="headings", selectmode="extended")

        encabezados = {"nombre": "Producto", "cantidad": "Cantidad Vendida", "total": "Total Ventas"}
        for col, texto in encabezados.items():
            tabla.heading(col, text=texto, command=lambda c=col: self.ordenar_columna(tabla, c, False))

        tabla.column("nombre", width=200, anchor="w")
        tabla.column("cantidad", width=120, anchor="center")
        tabla.column("total", width=120, anchor="e")

        for producto in datos:
            total_txt = f"S/ {float(producto[2]):.2f}"
            fila = (producto[0], int(producto[1]), total_txt)
            tabla.insert("", "end", values=fila)
            
        scrollbar = ttk.Scrollbar(tabla_container, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)

        return tabla_container

    def crear_tabla_inventario(self, parent_frame, datos):
        """Crea una tabla interactiva de inventario usando Treeview."""
        tabla_container = tk.Frame(parent_frame, bg="white")
        tabla_container.pack(fill="both", expand=True, padx=5, pady=5)

        columnas = ("id", "nombre", "categoria", "precio", "stock", "stock_min")
        tabla = ttk.Treeview(tabla_container, columns=columnas, show="headings", selectmode="extended")

        encabezados = {"id": "ID", "nombre": "Producto", "categoria": "Categoría", "precio": "Precio", "stock": "Stock", "stock_min": "Stock Mínimo"}
        for col, texto in encabezados.items():
            tabla.heading(col, text=texto, command=lambda c=col: self.ordenar_columna(tabla, c, False))

        tabla.column("id", width=50, anchor="center")
        tabla.column("nombre", width=200, anchor="w")
        tabla.column("categoria", width=120, anchor="w")
        tabla.column("precio", width=100, anchor="e")
        tabla.column("stock", width=80, anchor="center")
        tabla.column("stock_min", width=100, anchor="center")

        tabla.tag_configure("stock_bajo", background="#FADBD8", foreground="#E74C3C")

        for p in datos:
            tags = ("stock_bajo",) if p[4] <= p[5] else ()
            precio_txt = f"S/ {float(p[3]):.2f}"
            fila = (p[0], p[1], p[2], precio_txt, p[4], p[5])
            tabla.insert("", "end", values=fila, tags=tags)
            
        scrollbar = ttk.Scrollbar(tabla_container, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)

        return tabla_container

    def crear_tabla_clientes(self, parent_frame, datos):
        """Crea una tabla interactiva de clientes frecuentes usando Treeview."""
        tabla_container = tk.Frame(parent_frame, bg="white")
        tabla_container.pack(fill="both", expand=True, padx=5, pady=5)

        columnas = ("id", "nombre", "compras", "total")
        tabla = ttk.Treeview(tabla_container, columns=columnas, show="headings", selectmode="extended")

        encabezados = {"id": "ID", "nombre": "Cliente", "compras": "Compras", "total": "Total Gastado"}
        for col, texto in encabezados.items():
            tabla.heading(col, text=texto, command=lambda c=col: self.ordenar_columna(tabla, c, False))

        tabla.column("id", width=50, anchor="center")
        tabla.column("nombre", width=200, anchor="w")
        tabla.column("compras", width=100, anchor="center")
        tabla.column("total", width=120, anchor="e")

        for cliente in datos:
            total_txt = f"S/ {float(cliente[5]):.2f}"
            # (id, nombre, email, telefono, compras, total) -> cliente[0], cliente[1], cliente[4], cliente[5]
            fila = (cliente[0], cliente[1], cliente[4], total_txt)
            tabla.insert("", "end", values=fila)

        scrollbar = ttk.Scrollbar(tabla_container, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)

        return tabla_container
    
    # Funciones para crear gráficos
    def _ajustar_graficos_ancho(self, width_px):
        try:
            if not hasattr(self, "_graficos_canvases"):
                return
            for canvas in self._graficos_canvases:
                fig = canvas.figure
                dpi = fig.get_dpi() if hasattr(fig, "get_dpi") else 100
                new_w_in = max(6, (width_px - 60) / float(dpi))
                current_h_in = fig.get_size_inches()[1]
                fig.set_size_inches(new_w_in, current_h_in, forward=True)
                fig.tight_layout()
                try:
                    canvas.draw_idle()
                except:
                    canvas.draw()
        except Exception:
            pass

    def crear_grafico_ventas(self, datos):
        """Crea un gráfico de ventas por período"""
        try:
            # Limpiar frame de gráficos
            for widget in self.graficos_frame.winfo_children():
                widget.destroy()
                
            # Mostrar el frame de gráficos
            self.graficos_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Preparar datos para el gráfico
            fechas = []
            totales = []
            
            for venta in datos:
                try:
                    # Manejar fecha de forma robusta
                    fecha = venta[3] if len(venta) > 3 else venta[0]
                    if hasattr(fecha, 'strftime'):
                        fechas.append(fecha.strftime("%Y-%m-%d"))
                    else:
                        fechas.append(str(fecha))
                    
                    # Manejar total de forma robusta
                    total = venta[2] if len(venta) > 2 else 0
                    if isinstance(total, (int, float, Decimal)):
                        totales.append(float(total))
                    elif isinstance(total, str):
                        try:
                            totales.append(float(total.replace(',', '.')))
                        except ValueError:
                            totales.append(0.0)
                    else:
                        totales.append(0.0)
                except (IndexError, AttributeError, TypeError):
                    # Si hay error con algún registro, usar valores por defecto
                    fechas.append("Sin fecha")
                    totales.append(0.0)
            
            # Verificar que hay datos para mostrar
            if not fechas or not totales or all(t == 0 for t in totales):
                # Mostrar mensaje de no datos
                fig = Figure(figsize=(8, 4), dpi=100)
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'No hay datos de ventas para mostrar', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=14, color='#7F8C8D')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
            else:
                # Crear figura y ejes
                fig = Figure(figsize=(8, 4), dpi=100)
                ax = fig.add_subplot(111)
                
                # Crear gráfico de barras
                bars = ax.bar(range(len(fechas)), totales, color='#3498DB')
            
                # Configurar ejes
                ax.set_title('Ventas por Período')
                ax.set_xlabel('Fecha')
                ax.set_ylabel('Total (S/)')
                
                # Limitar etiquetas en el eje x si hay muchas fechas
                if len(fechas) > 10:
                    ax.set_xticks(range(0, len(fechas), len(fechas)//10))
                    ax.set_xticklabels([fechas[i] for i in range(0, len(fechas), len(fechas)//10)], rotation=45)
                else:
                    ax.set_xticks(range(len(fechas)))
                    ax.set_xticklabels(fechas, rotation=45)
                
                # Añadir valores sobre las barras
                for bar in bars:
                    height = bar.get_height()
                    try:
                        val = float(height)
                    except Exception:
                        val = 0.0
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'S/{val:.2f}', ha='center', va='bottom', rotation=0)
            
            fig.tight_layout()
            
            # Crear canvas para mostrar el gráfico
            canvas = FigureCanvasTkAgg(fig, master=self.graficos_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            # Registrar canvas para ajuste dinámico
            if hasattr(self, "_graficos_canvases"):
                self._graficos_canvases.append(canvas)
            
            # Añadir barra de herramientas de navegación
            toolbar = NavigationToolbar2Tk(canvas, self.graficos_frame)
            toolbar.update()
            # Ajustar ancho inicial según el canvas actual
            try:
                ancho = self.preview_canvas.winfo_width()
                if ancho > 0:
                    self._ajustar_graficos_ancho(ancho)
            except Exception:
                pass
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear gráfico de ventas: {str(e)}")
    
    def crear_grafico_productos(self, datos):
        """Crea un gráfico de productos más vendidos"""
        try:
            # Limpiar frame de gráficos
            for widget in self.graficos_frame.winfo_children():
                widget.destroy()
                
            # Mostrar el frame de gráficos
            self.graficos_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Preparar datos para el gráfico
            productos = []
            cantidades = []
            
            for producto in datos:
                try:
                    # Estructura esperada: (nombre, cantidad, total)
                    nombre = producto[0] if len(producto) > 0 else "Sin nombre"
                    productos.append(str(nombre))
                    
                    # Cantidad vendida
                    cantidad = producto[1] if len(producto) > 1 else 0
                    if isinstance(cantidad, (int, float, Decimal)):
                        cantidades.append(int(float(cantidad)))
                    elif isinstance(cantidad, str):
                        try:
                            cantidades.append(int(float(cantidad.replace(',', '.'))))
                        except ValueError:
                            cantidades.append(0)
                    else:
                        cantidades.append(0)
                except (IndexError, AttributeError, TypeError):
                    productos.append("Producto desconocido")
                    cantidades.append(0)
            
            # Verificar que hay datos para mostrar
            if not productos or not cantidades or all(c == 0 for c in cantidades):
                # Mostrar mensaje de no datos
                fig = Figure(figsize=(8, 4), dpi=100)
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'No hay datos de productos para mostrar', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=14, color='#7F8C8D')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
            else:
                # Crear figura y ejes
                fig = Figure(figsize=(8, 4), dpi=100)
                ax = fig.add_subplot(111)
                
                # Crear gráfico de barras horizontales
                bars = ax.barh(range(len(productos)), cantidades, color='#2ECC71')
            
                # Configurar ejes
                ax.set_title('Productos Más Vendidos')
                ax.set_xlabel('Cantidad Vendida')
                ax.set_ylabel('Producto')
                
                # Configurar etiquetas en el eje y
                ax.set_yticks(range(len(productos)))
                ax.set_yticklabels(productos)
                
                # Añadir valores al final de las barras
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2.,
                            f'{width}', ha='left', va='center')
            
            fig.tight_layout()
            
            # Crear canvas para mostrar el gráfico
            canvas = FigureCanvasTkAgg(fig, master=self.graficos_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            # Registrar canvas para ajuste dinámico
            if hasattr(self, "_graficos_canvases"):
                self._graficos_canvases.append(canvas)
            
            # Añadir barra de herramientas de navegación
            toolbar = NavigationToolbar2Tk(canvas, self.graficos_frame)
            toolbar.update()
            # Ajustar ancho inicial según el canvas actual
            try:
                ancho = self.preview_canvas.winfo_width()
                if ancho > 0:
                    self._ajustar_graficos_ancho(ancho)
            except Exception:
                pass
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear gráfico de productos: {str(e)}")
    
    def crear_grafico_inventario(self, datos):
        """Crea un gráfico de inventario"""
        try:
            # Limpiar frame de gráficos
            for widget in self.graficos_frame.winfo_children():
                widget.destroy()
                
            # Mostrar el frame de gráficos
            self.graficos_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Preparar datos para el gráfico
            productos = []
            stock = []
            colores = []
            
            for producto in datos:
                try:
                    # Manejar nombre del producto de forma robusta
                    nombre = producto[1] if len(producto) > 1 else "Sin nombre"
                    productos.append(str(nombre))
                    
                    # Manejar stock de forma robusta
                    stock_actual = producto[4] if len(producto) > 4 else 0
                    if isinstance(stock_actual, (int, float)):
                        stock_actual = int(stock_actual)
                    elif isinstance(stock_actual, str):
                        try:
                            stock_actual = int(float(stock_actual.replace(',', '.')))
                        except ValueError:
                            stock_actual = 0
                    else:
                        stock_actual = 0
                    
                    stock.append(stock_actual)
                    
                    # Asignar color según el nivel de stock en relación al mínimo
                    minimo = producto[5] if len(producto) > 5 else 0
                    try:
                        if isinstance(minimo, str):
                            minimo = int(float(minimo.replace(',', '.')))
                        elif isinstance(minimo, (float, Decimal)):
                            minimo = int(float(minimo))
                    except Exception:
                        minimo = 0

                    if stock_actual <= max(minimo, 0):
                        colores.append('#E74C3C')  # Rojo: por debajo o igual al mínimo
                    elif stock_actual <= max(minimo * 2, minimo + 5):
                        colores.append('#F39C12')  # Naranja: cercano al mínimo
                    else:
                        colores.append('#2ECC71')  # Verde: saludable
                        
                except (IndexError, AttributeError, TypeError):
                    # Si hay error con algún registro, usar valores por defecto
                    productos.append("Producto desconocido")
                    stock.append(0)
                    colores.append('#E74C3C')
            
            # Limitar a los 15 productos con menos stock para mejor visualización
            if len(productos) > 15:
                # Ordenar por stock ascendente
                productos_ordenados = [(productos[i], stock[i], colores[i]) for i in range(len(productos))]
                productos_ordenados.sort(key=lambda x: x[1])
                
                # Tomar los 15 con menos stock
                productos = [p[0] for p in productos_ordenados[:15]]
                stock = [p[1] for p in productos_ordenados[:15]]
                colores = [p[2] for p in productos_ordenados[:15]]
            
            # Crear figura y ejes
            fig = Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            # Crear gráfico de barras horizontales
            bars = ax.barh(range(len(productos)), stock, color=colores)
            
            # Configurar ejes
            ax.set_title('Nivel de Stock por Producto')
            ax.set_xlabel('Cantidad en Stock')
            ax.set_ylabel('Producto')
            
            # Configurar etiquetas en el eje y
            ax.set_yticks(range(len(productos)))
            ax.set_yticklabels(productos)
            
            # Añadir valores al final de las barras
            for i, bar in enumerate(bars):
                width = bar.get_width()
                try:
                    wv = int(width)
                except Exception:
                    wv = 0
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                        f'{wv}', ha='left', va='center')
            
            fig.tight_layout()
            
            # Crear canvas para mostrar el gráfico
            canvas = FigureCanvasTkAgg(fig, master=self.graficos_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            # Registrar canvas para ajuste dinámico
            if hasattr(self, "_graficos_canvases"):
                self._graficos_canvases.append(canvas)
            
            # Añadir barra de herramientas de navegación
            toolbar = NavigationToolbar2Tk(canvas, self.graficos_frame)
            toolbar.update()
            # Ajustar ancho inicial según el canvas actual
            try:
                ancho = self.preview_canvas.winfo_width()
                if ancho > 0:
                    self._ajustar_graficos_ancho(ancho)
            except Exception:
                pass
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear gráfico de inventario: {str(e)}")
    
    def crear_grafico_clientes(self, datos):
        """Crea un gráfico de clientes frecuentes"""
        try:
            # Limpiar frame de gráficos
            for widget in self.graficos_frame.winfo_children():
                widget.destroy()
                
            # Mostrar el frame de gráficos
            self.graficos_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Preparar datos para el gráfico
            clientes = []
            compras = []
            totales = []
            
            for cliente in datos:
                try:
                    # Estructura esperada: (id, nombre, email, telefono, compras, total_gastado)
                    nombre = cliente[1] if len(cliente) > 1 else "Sin nombre"
                    clientes.append(str(nombre))
                    
                    # Número de compras
                    num_compras = cliente[4] if len(cliente) > 4 else 0
                    if isinstance(num_compras, (int, float, Decimal)):
                        compras.append(int(float(num_compras)))
                    elif isinstance(num_compras, str):
                        try:
                            compras.append(int(float(num_compras.replace(',', '.'))))
                        except ValueError:
                            compras.append(0)
                    else:
                        compras.append(0)
                    
                    # Total gastado
                    total_gastado = cliente[5] if len(cliente) > 5 else 0
                    if isinstance(total_gastado, (int, float, Decimal)):
                        totales.append(float(total_gastado))
                    elif isinstance(total_gastado, str):
                        try:
                            totales.append(float(total_gastado.replace(',', '.')))
                        except ValueError:
                            totales.append(0.0)
                    else:
                        totales.append(0.0)
                        
                except (IndexError, AttributeError, TypeError):
                    clientes.append("Cliente desconocido")
                    compras.append(0)
                    totales.append(0.0)
            
            # Limitar a los 10 mejores clientes para mejor visualización
            if len(clientes) > 10:
                # Ordenar por total gastado descendente
                clientes_ordenados = [(clientes[i], compras[i], totales[i]) for i in range(len(clientes))]
                clientes_ordenados.sort(key=lambda x: x[2], reverse=True)
                
                # Tomar los 10 mejores
                clientes = [c[0] for c in clientes_ordenados[:10]]
                compras = [c[1] for c in clientes_ordenados[:10]]
                totales = [c[2] for c in clientes_ordenados[:10]]
            
            # Crear figura y ejes
            fig = Figure(figsize=(8, 6), dpi=100)
            
            # Gráfico 1: Número de compras
            ax1 = fig.add_subplot(211)
            bars1 = ax1.bar(range(len(clientes)), compras, color='#3498DB')
            
            ax1.set_title('Número de Compras por Cliente')
            ax1.set_ylabel('Compras')
            
            # Configurar etiquetas en el eje x
            ax1.set_xticks(range(len(clientes)))
            ax1.set_xticklabels(clientes, rotation=45)
            
            # Añadir valores sobre las barras
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
            
            # Gráfico 2: Total gastado
            ax2 = fig.add_subplot(212)
            bars2 = ax2.bar(range(len(clientes)), totales, color='#2ECC71')
            
            ax2.set_title('Total Gastado por Cliente')
            ax2.set_ylabel('Total (S/)')
            
            # Configurar etiquetas en el eje x
            ax2.set_xticks(range(len(clientes)))
            ax2.set_xticklabels(clientes, rotation=45)
            
            # Añadir valores sobre las barras
            for bar in bars2:
                height = bar.get_height()
                try:
                    val = float(height)
                except Exception:
                    val = 0.0
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'S/{val:.2f}', ha='center', va='bottom')
            
            fig.tight_layout()
            
            # Crear canvas para mostrar el gráfico
            canvas = FigureCanvasTkAgg(fig, master=self.graficos_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            # Registrar canvas para ajuste dinámico
            if hasattr(self, "_graficos_canvases"):
                self._graficos_canvases.append(canvas)
            
            # Añadir barra de herramientas de navegación
            toolbar = NavigationToolbar2Tk(canvas, self.graficos_frame)
            toolbar.update()
            # Ajustar ancho inicial según el canvas actual
            try:
                ancho = self.preview_canvas.winfo_width()
                if ancho > 0:
                    self._ajustar_graficos_ancho(ancho)
            except Exception:
                pass
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear gráfico de clientes: {str(e)}")
            
    # Funciones de exportación
    def exportar_pdf_ventas(self, datos):
        """Exporta un reporte de ventas a PDF"""
        try:
            # Solicitar ubicación para guardar el archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Guardar reporte de ventas como"
            )
            
            if not filename:
                return
                
            # Generar PDF con el generador de PDF
            self.pdf_generator.generar_reporte_ventas(datos, filename)
            
            # Mostrar mensaje de éxito y preguntar si desea abrir el archivo
            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a PDF: {str(e)}")
            
    def exportar_excel_ventas(self, datos):
        """Exporta un reporte de ventas a Excel"""
        try:
            # Solicitar ubicación para guardar el archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar reporte de ventas como"
            )
            
            if not filename:
                return
                
            # Normalizar y reordenar columnas -> (ID, Fecha, Cliente, Total, Estado)
            filas = []
            try:
                iterable = datos if isinstance(datos, list) else []
                for v in iterable:
                    try:
                        id_v = v[0] if len(v) > 0 else ""
                        cliente = v[1] if len(v) > 1 else ""
                        total = v[2] if len(v) > 2 else 0
                        fecha = v[3] if len(v) > 3 else ""
                        estado = v[4] if len(v) > 4 else "Completada"

                        if isinstance(total, str):
                            try:
                                total = float(total.strip().replace('S/', '').replace('$', '').replace(' ', '').replace(',', '.'))
                            except Exception:
                                total = 0.0
                        elif isinstance(total, Decimal):
                            total = float(total)
                        elif not isinstance(total, (int, float)):
                            total = 0.0

                        filas.append([id_v, fecha, cliente, total, estado])
                    except Exception:
                        filas.append(["", "", "", 0.0, ""])            
            except Exception:
                pass

            df = pd.DataFrame(filas, columns=["ID", "Fecha", "Cliente", "Total", "Estado"]) if filas else pd.DataFrame(columns=["ID","Fecha","Cliente","Total","Estado"])            
            
            # Exportar a Excel
            df.to_excel(filename, index=False, sheet_name="Ventas")
            
            # Mostrar mensaje de éxito y preguntar si desea abrir el archivo
            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a Excel: {str(e)}")
            
    def exportar_csv_ventas(self, datos):
        """Exporta un reporte de ventas a CSV"""
        try:
            # Solicitar ubicación para guardar el archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar reporte de ventas como"
            )
            
            if not filename:
                return
                
            # Normalizar y reordenar columnas -> (ID, Fecha, Cliente, Total, Estado)
            filas = []
            try:
                iterable = datos if isinstance(datos, list) else []
                for v in iterable:
                    try:
                        id_v = v[0] if len(v) > 0 else ""
                        cliente = v[1] if len(v) > 1 else ""
                        total = v[2] if len(v) > 2 else 0
                        fecha = v[3] if len(v) > 3 else ""
                        estado = v[4] if len(v) > 4 else "Completada"

                        if isinstance(total, str):
                            try:
                                total = float(total.strip().replace('S/', '').replace('$', '').replace(' ', '').replace(',', '.'))
                            except Exception:
                                total = 0.0
                        elif isinstance(total, Decimal):
                            total = float(total)
                        elif not isinstance(total, (int, float)):
                            total = 0.0

                        filas.append([id_v, fecha, cliente, total, estado])
                    except Exception:
                        filas.append(["", "", "", 0.0, ""])            
            except Exception:
                pass

            df = pd.DataFrame(filas, columns=["ID", "Fecha", "Cliente", "Total", "Estado"]) if filas else pd.DataFrame(columns=["ID","Fecha","Cliente","Total","Estado"])            
            
            # Exportar a CSV
            df.to_csv(filename, index=False)
            
            # Mostrar mensaje de éxito y preguntar si desea abrir el archivo
            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a CSV: {str(e)}")
            
    def exportar_pdf_productos(self, datos):
        """Exporta un reporte de productos más vendidos a PDF"""
        try:
            # Solicitar ubicación para guardar el archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Guardar reporte de productos como"
            )
            
            if not filename:
                return
                
            # Generar PDF con el generador de PDF
            self.pdf_generator.generar_reporte_productos(datos, filename)
            
            # Mostrar mensaje de éxito y preguntar si desea abrir el archivo
            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a PDF: {str(e)}")
            
    def exportar_excel_productos(self, datos):
        """Exporta un reporte de productos más vendidos a Excel"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar reporte de productos como"
            )
            if not filename:
                return

            # Normalizar datos -> (Producto, Cantidad Vendida, Total Ventas)
            filas = []
            iterable = datos if isinstance(datos, list) else []
            for p in iterable:
                try:
                    nombre = p[0] if len(p) > 0 else ""
                    cantidad = p[1] if len(p) > 1 else 0
                    total = p[2] if len(p) > 2 else 0

                    # Casts robustos
                    try:
                        if isinstance(cantidad, str):
                            cantidad = int(float(cantidad.replace(',', '.')))
                        elif isinstance(cantidad, (int, float, Decimal)):
                            cantidad = int(float(cantidad))
                        else:
                            cantidad = 0
                    except Exception:
                        cantidad = 0

                    if isinstance(total, str):
                        try:
                            total = float(total.strip().replace('S/', '').replace('$', '').replace(' ', '').replace(',', '.'))
                        except Exception:
                            total = 0.0
                    elif isinstance(total, Decimal):
                        total = float(total)
                    elif not isinstance(total, (int, float)):
                        total = 0.0

                    filas.append([nombre, cantidad, total])
                except Exception:
                    filas.append(["", 0, 0.0])

            df = pd.DataFrame(filas, columns=["Producto", "Cantidad Vendida", "Total Ventas"]) if filas else pd.DataFrame(columns=["Producto","Cantidad Vendida","Total Ventas"])            
            df.to_excel(filename, index=False, sheet_name="Productos")

            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a Excel: {str(e)}")
            
    def exportar_csv_productos(self, datos):
        """Exporta un reporte de productos más vendidos a CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar reporte de productos como"
            )
            if not filename:
                return

            # Normalizar datos -> (Producto, Cantidad Vendida, Total Ventas)
            filas = []
            iterable = datos if isinstance(datos, list) else []
            for p in iterable:
                try:
                    nombre = p[0] if len(p) > 0 else ""
                    cantidad = p[1] if len(p) > 1 else 0
                    total = p[2] if len(p) > 2 else 0

                    try:
                        if isinstance(cantidad, str):
                            cantidad = int(float(cantidad.replace(',', '.')))
                        elif isinstance(cantidad, (int, float, Decimal)):
                            cantidad = int(float(cantidad))
                        else:
                            cantidad = 0
                    except Exception:
                        cantidad = 0

                    if isinstance(total, str):
                        try:
                            total = float(total.strip().replace('S/', '').replace('$', '').replace(' ', '').replace(',', '.'))
                        except Exception:
                            total = 0.0
                    elif isinstance(total, Decimal):
                        total = float(total)
                    elif not isinstance(total, (int, float)):
                        total = 0.0

                    filas.append([nombre, cantidad, total])
                except Exception:
                    filas.append(["", 0, 0.0])

            df = pd.DataFrame(filas, columns=["Producto", "Cantidad Vendida", "Total Ventas"]) if filas else pd.DataFrame(columns=["Producto","Cantidad Vendida","Total Ventas"]) 
            df.to_csv(filename, index=False, sep=';', encoding='utf-8-sig')

            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a CSV: {str(e)}")
            
    def exportar_pdf_inventario(self, datos):
        """Exporta un reporte de inventario a PDF"""
        try:
            # Solicitar ubicación para guardar el archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Guardar reporte de inventario como"
            )
            
            if not filename:
                return
                
            # Generar PDF con el generador de PDF
            self.pdf_generator.generar_reporte_inventario(datos, filename)
            
            # Mostrar mensaje de éxito y preguntar si desea abrir el archivo
            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a PDF: {str(e)}")
            
    def exportar_excel_inventario(self, datos):
        """Exporta un reporte de inventario a Excel"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar reporte de inventario como"
            )
            if not filename:
                return

            # Normalizar datos -> (ID, Producto, Categoría, Precio, Stock, Stock Mínimo)
            filas = []
            iterable = datos if isinstance(datos, list) else []
            for p in iterable:
                try:
                    if isinstance(p, dict):
                        pid = p.get('id', p.get('ID', p.get('producto_id', '')))
                        nombre = p.get('nombre', p.get('producto', ''))
                        categoria = p.get('categoria', '')
                        precio = p.get('precio', 0)
                        stock = p.get('stock', p.get('cantidad', 0))
                        minimo = p.get('stock_minimo', p.get('minimo', 0))
                    else:
                        pid = p[0] if len(p) > 0 else ''
                        nombre = p[1] if len(p) > 1 else ''
                        categoria = p[2] if len(p) > 2 else ''
                        precio = p[3] if len(p) > 3 else 0
                        stock = p[4] if len(p) > 4 else 0
                        minimo = p[5] if len(p) > 5 else 0

                    # Casts
                    if isinstance(precio, str):
                        try:
                            precio = float(precio.strip().replace('S/', '').replace('$', '').replace(' ', '').replace(',', '.'))
                        except Exception:
                            precio = 0.0
                    elif isinstance(precio, Decimal):
                        precio = float(precio)
                    elif not isinstance(precio, (int, float)):
                        precio = 0.0

                    try:
                        if isinstance(stock, str):
                            stock = int(float(stock.replace(',', '.')))
                        elif isinstance(stock, (int, float, Decimal)):
                            stock = int(float(stock))
                        else:
                            stock = 0
                    except Exception:
                        stock = 0

                    try:
                        if isinstance(minimo, str):
                            minimo = int(float(minimo.replace(',', '.')))
                        elif isinstance(minimo, (int, float, Decimal)):
                            minimo = int(float(minimo))
                        else:
                            minimo = 0
                    except Exception:
                        minimo = 0

                    filas.append([pid, nombre, categoria, precio, stock, minimo])
                except Exception:
                    filas.append(['', '', '', 0.0, 0, 0])

            columnas = ["ID", "Producto", "Categoría", "Precio", "Stock", "Stock Mínimo"]
            df = pd.DataFrame(filas, columns=columnas) if filas else pd.DataFrame(columns=columnas)
            df.to_excel(filename, index=False, sheet_name="Inventario")

            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a Excel: {str(e)}")
            
    def exportar_csv_inventario(self, datos):
        """Exporta un reporte de inventario a CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar reporte de inventario como"
            )
            if not filename:
                return

            # Normalizar datos -> (ID, Producto, Categoría, Precio, Stock, Stock Mínimo)
            filas = []
            iterable = datos if isinstance(datos, list) else []
            for p in iterable:
                try:
                    if isinstance(p, dict):
                        pid = p.get('id', p.get('ID', p.get('producto_id', '')))
                        nombre = p.get('nombre', p.get('producto', ''))
                        categoria = p.get('categoria', '')
                        precio = p.get('precio', 0)
                        stock = p.get('stock', p.get('cantidad', 0))
                        minimo = p.get('stock_minimo', p.get('minimo', 0))
                    else:
                        pid = p[0] if len(p) > 0 else ''
                        nombre = p[1] if len(p) > 1 else ''
                        categoria = p[2] if len(p) > 2 else ''
                        precio = p[3] if len(p) > 3 else 0
                        stock = p[4] if len(p) > 4 else 0
                        minimo = p[5] if len(p) > 5 else 0

                    if isinstance(precio, str):
                        try:
                            precio = float(precio.strip().replace('S/', '').replace('$', '').replace(' ', '').replace(',', '.'))
                        except Exception:
                            precio = 0.0
                    elif isinstance(precio, Decimal):
                        precio = float(precio)
                    elif not isinstance(precio, (int, float)):
                        precio = 0.0

                    try:
                        if isinstance(stock, str):
                            stock = int(float(stock.replace(',', '.')))
                        elif isinstance(stock, (int, float, Decimal)):
                            stock = int(float(stock))
                        else:
                            stock = 0
                    except Exception:
                        stock = 0

                    try:
                        if isinstance(minimo, str):
                            minimo = int(float(minimo.replace(',', '.')))
                        elif isinstance(minimo, (int, float, Decimal)):
                            minimo = int(float(minimo))
                        else:
                            minimo = 0
                    except Exception:
                        minimo = 0

                    filas.append([pid, nombre, categoria, precio, stock, minimo])
                except Exception:
                    filas.append(['', '', '', 0.0, 0, 0])

            columnas = ["ID", "Producto", "Categoría", "Precio", "Stock", "Stock Mínimo"]
            df = pd.DataFrame(filas, columns=columnas) if filas else pd.DataFrame(columns=columnas)
            df.to_csv(filename, index=False, sep=';', encoding='utf-8-sig')

            # Mostrar mensaje de éxito y preguntar si desea abrir el archivo
            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a CSV: {str(e)}")
            
    def exportar_pdf_clientes(self, datos):
        """Exporta un reporte de clientes frecuentes a PDF"""
        try:
            # Solicitar ubicación para guardar el archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Guardar reporte de clientes como"
            )
            
            if not filename:
                return
                
            # Generar PDF con el generador de PDF
            self.pdf_generator.generar_reporte_clientes(datos, filename)
            
            # Mostrar mensaje de éxito y preguntar si desea abrir el archivo
            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a PDF: {str(e)}")
            
    def exportar_excel_clientes(self, datos):
        """Exporta un reporte de clientes frecuentes a Excel"""
        try:
            # Solicitar ubicación para guardar el archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar reporte de clientes como"
            )
            
            if not filename:
                return
                
            # Normalizar datos -> (ID, Cliente, Compras, Total Gastado)
            filas = []
            try:
                iterable = datos if isinstance(datos, list) else []
                for c in iterable:
                    try:
                        if isinstance(c, dict):
                            cid = c.get('id', c.get('ID', 0))
                            nombre = c.get('nombre', c.get('cliente', ''))
                            compras = c.get('compras', c.get('cantidad', c.get('n_compras', 0)))
                            total = c.get('total_gastado', c.get('total', 0))
                        else:
                            cid = c[0] if len(c) > 0 else 0
                            nombre = c[1] if len(c) > 1 else ''
                            compras = c[4] if len(c) > 4 else 0
                            total = c[5] if len(c) > 5 else 0

                        try:
                            if isinstance(compras, str):
                                compras = int(float(compras.replace(',', '.')))
                            elif isinstance(compras, (int, float, Decimal)):
                                compras = int(float(compras))
                            else:
                                compras = 0
                        except Exception:
                            compras = 0

                        if isinstance(total, str):
                            try:
                                total = float(total.strip().replace('S/', '').replace('$', '').replace(' ', '').replace(',', '.'))
                            except Exception:
                                total = 0.0
                        elif isinstance(total, Decimal):
                            total = float(total)
                        elif not isinstance(total, (int, float)):
                            total = 0.0

                        filas.append([cid, nombre, compras, total])
                    except Exception:
                        filas.append([0, '', 0, 0.0])
            except Exception:
                pass

            df = pd.DataFrame(filas, columns=["ID", "Cliente", "Compras", "Total Gastado"]) if filas else pd.DataFrame(columns=["ID","Cliente","Compras","Total Gastado"]) 
            
            # Exportar a Excel
            df.to_excel(filename, index=False, sheet_name="Clientes")
            
            # Mostrar mensaje de éxito y preguntar si desea abrir el archivo
            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a Excel: {str(e)}")
            
    def exportar_csv_clientes(self, datos):
        """Exporta un reporte de clientes frecuentes a CSV"""
        try:
            # Solicitar ubicación para guardar el archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar reporte de clientes como"
            )
            
            if not filename:
                return
                
            # Normalizar datos -> (ID, Cliente, Compras, Total Gastado)
            filas = []
            try:
                iterable = datos if isinstance(datos, list) else []
                for c in iterable:
                    try:
                        if isinstance(c, dict):
                            cid = c.get('id', c.get('ID', 0))
                            nombre = c.get('nombre', c.get('cliente', ''))
                            compras = c.get('compras', c.get('cantidad', c.get('n_compras', 0)))
                            total = c.get('total_gastado', c.get('total', 0))
                        else:
                            cid = c[0] if len(c) > 0 else 0
                            nombre = c[1] if len(c) > 1 else ''
                            compras = c[4] if len(c) > 4 else 0
                            total = c[5] if len(c) > 5 else 0

                        try:
                            if isinstance(compras, str):
                                compras = int(float(compras.replace(',', '.')))
                            elif isinstance(compras, (int, float, Decimal)):
                                compras = int(float(compras))
                            else:
                                compras = 0
                        except Exception:
                            compras = 0

                        if isinstance(total, str):
                            try:
                                total = float(total.strip().replace('S/', '').replace('$', '').replace(' ', '').replace(',', '.'))
                            except Exception:
                                total = 0.0
                        elif isinstance(total, Decimal):
                            total = float(total)
                        elif not isinstance(total, (int, float)):
                            total = 0.0

                        filas.append([cid, nombre, compras, total])
                    except Exception:
                        filas.append([0, '', 0, 0.0])
            except Exception:
                pass

            df = pd.DataFrame(filas, columns=["ID", "Cliente", "Compras", "Total Gastado"]) if filas else pd.DataFrame(columns=["ID","Cliente","Compras","Total Gastado"]) 
            
            # Exportar a CSV
            df.to_csv(filename, index=False, sep=';', encoding='utf-8-sig')
            
            # Mostrar mensaje de éxito y preguntar si desea abrir el archivo
            if messagebox.askyesno("Éxito", "Reporte generado con éxito. ¿Desea abrirlo ahora?"):
                os.startfile(filename)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a CSV: {str(e)}")
    

# Iniciar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = NexusCafeApp(root)
