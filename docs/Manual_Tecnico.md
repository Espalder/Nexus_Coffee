# Manual Técnico – NexusCoffee_Complete

## Descripción General
- Aplicación de escritorio para gestión de cafetería en Python (Tkinter)
- Arquitectura modular: separación por `modules/`, `services/`, `models/`, `views/`
- Persistencia en MySQL con inicialización automática de tablas
- Generación de reportes en PDF y utilitarios de respaldo

## Requisitos
- Python 3.8+ (Windows)
- MySQL Server 8.x (o compatible)
- Dependencias en `requirements.txt`
- Scripts de ayuda: `INSTALAR.bat` y `EJECUTAR.bat`

## Entradas Clave
- Punto de entrada: `NexusCoffee_Complete/main_modular.py` (`NexusCoffee_Complete\main_modular.py:1`)
- Configuración MySQL fija en código: `NexusCoffee_Complete/modules/config.py:6`
- Config JSON MySQL: `NexusCoffee_Complete/config_mysql.json:1`
- Credenciales por defecto en UI: `NexusCoffee_Complete/views/login_view.py:43`

## Estructura
- `modules/database.py`: gestor de BD y creación de tablas (`NexusCoffee_Complete\modules\database.py:1`)
- `modules/models.py`: modelos de negocio (Usuario, Producto, Venta, Cliente)
- `services/*`: servicios de dominio (auth, reportes, ventas) (`NexusCoffee_Complete\services\auth_service.py:1`)
- `views/*`: pantallas y componentes UI (`NexusCoffee_Complete\modules\views.py:57`)
- `nexus_core/db.py`: utilitarios de conexión MySQL
- `core/utils.py`: utilidades generales

## Configuración de Base de Datos
- En código: `modules/config.py` (`NexusCoffee_Complete\modules\config.py:6`) define `DB_CONFIG`
- Alternativa JSON: `config_mysql.json` (`NexusCoffee_Complete\config_mysql.json:1`)
- `DatabaseManager` inicializa y verifica conexión (`NexusCoffee_Complete\modules\database.py:12`)
- Tablas creadas: `usuarios`, `productos`, `ventas`, `detalles_venta`, `clientes`, `configuracion` (`NexusCoffee_Complete\modules\database.py:147` y `NexusCoffee_Complete\modules\database.py:157`)

## Instalación
- Opción scripts:
  - Ejecutar `INSTALAR.bat` para crear venv e instalar dependencias
  - Ejecutar `EJECUTAR.bat` para iniciar la aplicación
- Opción manual:
  - `python -m venv .venv && .venv\\Scripts\\activate`
  - `pip install -r requirements.txt`
  - Configurar MySQL y credenciales en `modules/config.py` o `config_mysql.json`

## Ejecución
- `python main_modular.py`
- Prueba rápida: `probar_aplicacion.py` verifica conexión y login (`NexusCoffee_Complete\probar_aplicacion.py:1`)

## Autenticación
- Hash SHA-256 de contraseña en consultas (`NexusCoffee_Complete\services\auth_service.py:11`)
- Usuario por defecto visible en UI: `admin/admin123` (`NexusCoffee_Complete\views\login_view.py:43`)

## Generación de PDFs
- `modules/pdf_generator.py` crea reportes en `pdfs_generados/`
- Asegurar permisos de escritura en la carpeta

## Temas y UI
- Config de tema y rutas en `modules/config.py` y `config.py` (`NexusCoffee_Complete\config.py:1`)
- Cambio de tema y estilos gestionados vía variables en `main_modular.py`

## Registro y Logs
- `config.py` define `LOG_CONFIG` y rutas (`NexusCoffee_Complete\config.py:118`)

## Respaldo
- Parámetros en `config.py` (`BACKUP_CONFIG`) (`NexusCoffee_Complete\config.py:102`)

## Buenas Prácticas
- No subir `__pycache__/`, `*.pyc`, `*.db`, `pdfs_generados/`, `reportes_pdf/`
- Usar variables de entorno para secretos en producción
- Proteger rama `main` y trabajar en `feature/*` o `develop`

## Troubleshooting
- Error MySQL: verificar servicio y credenciales (`NexusCoffee_Complete\modules\database.py:18`)
- UI no abre: revisar entorno virtual y dependencias
- PDFs no se generan: validar permisos y rutas (`NexusCoffee_Complete\modules\config.py:44`)

## Instalación Detallada
- Preparar entorno:
  - Instalar Python 3.8+ desde python.org (agregar a PATH)
  - Instalar MySQL Server 8.x y MySQL Workbench (opcional)
- Crear entorno virtual:
  - `python -m venv .venv`
  - Activar: `.venv\\Scripts\\activate`
- Instalar dependencias:
  - `pip install -r requirements.txt`
- Configurar MySQL:
  - Crear base y usuario (ejemplo):
    - `CREATE DATABASE nexus_coffee CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
    - `CREATE USER 'root'@'localhost' IDENTIFIED BY 'KV7$LU%9k&tQ#ayU';` (ajustar según seguridad)
    - `GRANT ALL PRIVILEGES ON nexus_coffee.* TO 'root'@'localhost';`
  - Ajustar credenciales en `modules/config.py` (`NexusCoffee_Complete\\modules\\config.py:6`) o `config_mysql.json` (`NexusCoffee_Complete\\config_mysql.json:1`)
- Inicialización automática:
  - Al ejecutar `main_modular.py`, `DatabaseManager.inicializar_bd()` crea tablas si no existen (`NexusCoffee_Complete\\modules\\database.py:147` y `NexusCoffee_Complete\\modules\\database.py:157`)

## Ejecución Detallada
- Comando directo: `python main_modular.py`
- Script de verificación: `python probar_aplicacion.py` valida conexión y login (`NexusCoffee_Complete\\probar_aplicacion.py:1`)
- Entrada de la UI: `NexusCoffee_Complete\\main_modular.py:1` con creación de `NexusCafeApp` y `root.mainloop()` (`NexusCoffee_Complete\\main_modular.py:79`)

## Arquitectura y Flujo
- UI (Tkinter): ventanas, marcos y widgets en `views/*` y `main_modular.py`
- Servicios: lógica de negocio desacoplada en `services/*` (auth, reportes, ventas)
- Modelos: entidades y operaciones en `modules/models.py` y `models/*`
- Persistencia: `DatabaseManager` (MySQL) gestiona conexión y queries seguras
- Generación de PDF: `modules/pdf_generator.py` produce reportes en `pdfs_generados/`

## Modelo de Datos
- `usuarios`: credenciales y roles; contraseña con SHA-256 (`NexusCoffee_Complete\\services\\auth_service.py:11`)
- `productos`: nombre, precio, stock, categoría, estado
- `ventas`: total, fecha, usuario; índices por fecha/cliente (`NexusCoffee_Complete\\modules\\database.py:147`)
- `detalles_venta`: relación venta-producto, cantidades y subtotales (`NexusCoffee_Complete\\modules\\database.py:157`)
- `clientes`: datos de contacto e índices por nombre/email
- `configuracion`: pares clave/valor para ajustes persistentes

## Configuración Avanzada
- Alternar tema y rutas en `config.py` (`NexusCoffee_Complete\\config.py:57` y `NexusCoffee_Complete\\config.py:166`)
- Log de aplicación configurado en `LOG_CONFIG` (`NexusCoffee_Complete\\config.py:118`)
- Directorios: `PDFS_DIR`, `BACKUP_DIR` (`NexusCoffee_Complete\\config.py:15`)
- Cambiar moneda, stock mínimo y parámetros UI en `modules/config.py` (`NexusCoffee_Complete\\modules\\config.py:17`)

## Seguridad y Roles
- Usuario por defecto `admin/admin123` expuesto en UI (`NexusCoffee_Complete\\views\\login_view.py:43`)
- Implementar políticas de cambio de password y roles vía tabla `usuarios`
- Preferir variables de entorno para credenciales en producción

## Generación y Personalización de Reportes
- Ubicación de PDFs: `pdfs_generados/` (`NexusCoffee_Complete\\modules\\config.py:44`)
- Personalizar contenido y estilo en `modules/pdf_generator.py`
- Incluir branding de la cafetería desde `CAFETERIA_CONFIG` (`NexusCoffee_Complete\\modules\\config.py:23`)

## Respaldo y Recuperación
- Configurar respaldo automático en `BACKUP_CONFIG` (`NexusCoffee_Complete\\config.py:102`)
- Exportar datos MySQL: `mysqldump -u <user> -p nexus_coffee > backup.sql`
- Restaurar datos: `mysql -u <user> -p nexus_coffee < backup.sql`

## Pruebas y Verificación
- `probar_aplicacion.py` realiza importaciones y login de prueba (`NexusCoffee_Complete\\probar_aplicacion.py:1`)
- `scripts/test_pdf_generation.py` valida generación de PDFs

## Despliegue
- Windows: usar scripts `.bat` incluidos
- Opcional: empaquetar con PyInstaller `pyinstaller --onefile main_modular.py` (revisar imports y datos)

## Problemas Comunes y Soluciones
- `Error de conexión MySQL`: revisar host/puerto, usuario, contraseña y servicio (`NexusCoffee_Complete\\modules\\database.py:18`)
- `Login fallido`: confirmar usuario `admin` y hash SHA-256 consistente (`NexusCoffee_Complete\\services\\auth_service.py:11`)
- `Permisos de archivos`: verificar escritura en `pdfs_generados/` y rutas configuradas
- `Dependencias rotas`: reinstalar con `pip install -r requirements.txt` y reactivar venv

