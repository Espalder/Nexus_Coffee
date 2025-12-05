#!/usr/bin/env python3
"""
Módulo para generar PDFs para Nexus Café
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import datetime

class PDFGenerator:
    def __init__(self):
        pass
    
    def generar_pdf_ventas(self, ventas, filename, titulo="REPORTE DE VENTAS"):
        """Generar un PDF con el reporte de ventas"""
        try:
            # Crear documento
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            normal_style = styles['Normal']
            
            # Título
            elements.append(Paragraph(titulo, title_style))
            elements.append(Spacer(1, 12))
            
            # Fecha del reporte
            elements.append(Paragraph(f"Fecha del reporte: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            elements.append(Spacer(1, 12))
            
            # Tabla de ventas
            data = [["ID", "Cliente", "Total", "Fecha"]]
            for venta in ventas:
                data.append([
                    str(venta[0]),
                    venta[1],
                    f"S/ {venta[2]:.2f}",
                    venta[3].strftime("%Y-%m-%d %H:%M") if isinstance(venta[3], datetime.datetime) else str(venta[3])
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Total de ventas
            total_ventas = sum(venta[2] for venta in ventas)
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"TOTAL DE VENTAS: S/ {total_ventas:.2f}", styles['Heading2']))
            
            # Generar PDF
            doc.build(elements)
            
            return True
            
        except Exception as e:
            print(f"Error generando PDF de ventas: {e}")
            return False
    
    def generar_pdf_inventario(self, productos, filename, titulo="REPORTE DE INVENTARIO"):
        """Generar un PDF con el reporte de inventario"""
        try:
            # Crear documento
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            normal_style = styles['Normal']
            
            # Título
            elements.append(Paragraph(titulo, title_style))
            elements.append(Spacer(1, 12))
            
            # Fecha del reporte
            elements.append(Paragraph(f"Fecha del reporte: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            elements.append(Spacer(1, 12))
            
            # Tabla de productos
            data = [["ID", "Nombre", "Categoría", "Precio", "Stock", "Stock Mínimo"]]
            for producto in productos:
                data.append([
                    str(producto[0]),
                    producto[1],
                    producto[2],
                    f"S/ {producto[3]:.2f}",
                    str(producto[4]),
                    str(producto[5])
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Total de productos
            total_productos = len(productos)
            elementos_stock_bajo = sum(1 for p in productos if p[4] <= p[5])
            
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"TOTAL DE PRODUCTOS: {total_productos}", styles['Heading2']))
            elements.append(Paragraph(f"PRODUCTOS CON STOCK BAJO: {elementos_stock_bajo}", styles['Heading3']))
            
            # Generar PDF
            doc.build(elements)
            
            return True
            
        except Exception as e:
            print(f"Error generando PDF de inventario: {e}")
            return False
    
    def generar_reporte_ventas(self, ventas, filename):
        """Método wrapper para compatibilidad con main_modular.py"""
        return self.generar_pdf_ventas(ventas, filename)
    
    def generar_reporte_inventario(self, productos, filename):
        """Método wrapper para compatibilidad con main_modular.py"""
        return self.generar_pdf_inventario(productos, filename)
    
    def generar_reporte_productos(self, productos, filename):
        """Generar un PDF con el reporte de productos más vendidos"""
        try:
            # Crear documento
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            normal_style = styles['Normal']
            
            # Título
            elements.append(Paragraph("REPORTE DE PRODUCTOS MÁS VENDIDOS", title_style))
            elements.append(Spacer(1, 12))
            
            # Fecha del reporte
            elements.append(Paragraph(f"Fecha del reporte: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            elements.append(Spacer(1, 12))
            
            # Tabla de productos
            data = [["Producto", "Cantidad Vendida", "Total Ventas"]]
            total_general = 0
            
            for producto in productos:
                # Manejar diferentes formatos de tupla
                if len(producto) >= 3:
                    nombre = str(producto[0]) if producto[0] else "Sin nombre"
                    cantidad = int(producto[1]) if producto[1] else 0
                    total = float(producto[2]) if producto[2] else 0.0
                else:
                    nombre = "Producto desconocido"
                    cantidad = 0
                    total = 0.0
                
                total_general += total
                
                data.append([
                    nombre,
                    str(cantidad),
                    f"S/ {total:.2f}"
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Resumen
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"TOTAL DE PRODUCTOS: {len(productos)}", styles['Heading2']))
            elements.append(Paragraph(f"TOTAL EN VENTAS: S/ {total_general:.2f}", styles['Heading2']))
            
            # Generar PDF
            doc.build(elements)
            
            return True
            
        except Exception as e:
            print(f"Error generando PDF de productos: {e}")
            return False
    
    def generar_reporte_clientes(self, clientes, filename):
        """Generar un PDF con el reporte de clientes frecuentes"""
        try:
            # Crear documento
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            normal_style = styles['Normal']
            
            # Título
            elements.append(Paragraph("REPORTE DE CLIENTES FRECUENTES", title_style))
            elements.append(Spacer(1, 12))
            
            # Fecha del reporte
            elements.append(Paragraph(f"Fecha del reporte: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            elements.append(Spacer(1, 12))
            
            # Tabla de clientes
            data = [["ID", "Cliente", "Compras", "Total Gastado"]]
            total_compras = 0
            total_gastado = 0
            
            for cliente in clientes:
                # Manejar diferentes formatos de tupla de forma robusta
                try:
                    # Detectar forma de tupla: (id, nombre, compras, total) o (id, nombre, email, telefono, fecha_registro, compras, total)
                    if len(cliente) >= 4 and not (len(cliente) >= 7):
                        id_val = cliente[0] if cliente[0] is not None else 0
                        nombre_val = cliente[1] or "Sin nombre"
                        compras_raw = cliente[2]
                        total_raw = cliente[3]
                    elif len(cliente) >= 7:
                        id_val = cliente[0] if cliente[0] is not None else 0
                        nombre_val = cliente[1] or "Sin nombre"
                        compras_raw = cliente[5]
                        total_raw = cliente[6]
                    else:
                        id_val = cliente[0] if len(cliente) > 0 and cliente[0] is not None else 0
                        nombre_val = cliente[1] if len(cliente) > 1 and cliente[1] else "Sin nombre"
                        compras_raw = cliente[2] if len(cliente) > 2 else 0
                        total_raw = cliente[3] if len(cliente) > 3 else 0
                    
                    # Normalizar compras
                    try:
                        if isinstance(compras_raw, (int, float)):
                            compras_val = int(compras_raw)
                        elif isinstance(compras_raw, str):
                            compras_val = int(float(compras_raw.replace(',', '.'))) if compras_raw.strip() else 0
                        else:
                            compras_val = 0
                    except Exception:
                        compras_val = 0
                    
                    # Normalizar total gastado
                    try:
                        if total_raw is None or (isinstance(total_raw, str) and total_raw.strip() == ""):
                            total_val = 0.0
                        elif isinstance(total_raw, str):
                            total_val = float(total_raw.replace(',', '.'))
                        else:
                            total_val = float(total_raw)
                    except Exception:
                        total_val = 0.0
                        
                except Exception:
                    # En caso de estructura inesperada
                    id_val = 0
                    nombre_val = "Cliente desconocido"
                    compras_val = 0
                    total_val = 0.0
                
                total_compras += compras_val
                total_gastado += total_val
                
                data.append([
                    str(id_val),
                    nombre_val,
                    str(compras_val),
                    f"S/ {total_val:.2f}"
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Resumen
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"TOTAL DE CLIENTES: {len(clientes)}", styles['Heading2']))
            elements.append(Paragraph(f"TOTAL DE COMPRAS: {total_compras}", styles['Heading2']))
            elements.append(Paragraph(f"TOTAL GASTADO: S/ {total_gastado:.2f}", styles['Heading2']))
            
            # Generar PDF
            doc.build(elements)
            
            return True
            
        except Exception as e:
            print(f"Error generando PDF de clientes: {e}")
            return False

    def generar_pdf_markdown(self, md_path, pdf_path, titulo=None):
        try:
            from reportlab.platypus import ListFlowable, ListItem
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            h2_style = styles['Heading2']
            h3_style = styles['Heading3']
            normal_style = styles['Normal']

            elements = []

            if titulo:
                elements.append(Paragraph(titulo, title_style))
                elements.append(Spacer(1, 12))

            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.splitlines()
            pending_list = []

            def flush_list():
                nonlocal pending_list
                if pending_list:
                    elements.append(ListFlowable(pending_list, bulletType='bullet'))
                    pending_list = []

            for line in lines:
                s = line.rstrip()
                if not s:
                    flush_list()
                    elements.append(Spacer(1, 6))
                    continue
                if s.startswith('# '):
                    flush_list()
                    elements.append(Paragraph(s[2:].strip(), title_style))
                elif s.startswith('## '):
                    flush_list()
                    elements.append(Paragraph(s[3:].strip(), h2_style))
                elif s.startswith('### '):
                    flush_list()
                    elements.append(Paragraph(s[4:].strip(), h3_style))
                elif s.startswith('- '):
                    item_para = Paragraph(s[2:].strip(), normal_style)
                    pending_list.append(ListItem(item_para))
                else:
                    flush_list()
                    elements.append(Paragraph(s, normal_style))

            flush_list()

            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            doc.build(elements)
            return True
        except Exception as e:
            print(f"Error generando PDF desde Markdown: {e}")
            return False
