#!/usr/bin/env python3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.pdf_generator import PDFGenerator

DOCS_DIR = os.path.join(BASE_DIR, 'docs')

def main():
    pdf = PDFGenerator()

    manuals = [
        ('Manual_Tecnico.md', 'Manual_Tecnico.pdf', 'Manual Técnico – NexusCoffee'),
        ('Manual_Usuario.md', 'Manual_Usuario.pdf', 'Manual de Usuario – NexusCoffee'),
    ]

    for md_name, pdf_name, title in manuals:
        md_path = os.path.join(DOCS_DIR, md_name)
        pdf_path = os.path.join(DOCS_DIR, pdf_name)
        ok = pdf.generar_pdf_markdown(md_path, pdf_path, titulo=title)
        print(f"[{'OK' if ok else 'FAIL'}] {md_name} -> {pdf_path}")

if __name__ == '__main__':
    main()
