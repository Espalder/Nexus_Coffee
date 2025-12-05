# Manual de Usuario – NexusCoffee

## Qué es NexusCoffee
- Sistema para administrar ventas, inventario, clientes y reportes de una cafetería
- Interfaz sencilla y moderna con botones y menús claros

## Requisitos
- Windows con Python instalado (el instalador lo prepara)
- MySQL funcionando si usas modo MySQL

## Instalación
- Haz doble clic en `INSTALAR.bat`
- Espera a que termine la instalación automática

## Cómo iniciar
- Haz doble clic en `EJECUTAR.bat`
- Se abrirá la ventana de inicio de sesión
- Usuario por defecto: `admin` | Contraseña: `admin123` (`NexusCoffee_Complete\views\login_view.py:43`)

## Pantallas principales
- Inicio de sesión: ingresa usuario y contraseña
- Dashboard: resumen con accesos a ventas, inventario, clientes y reportes
- Inventario: agrega, edita y elimina productos
- Ventas: registra ventas, calcula totales y genera comprobantes
- Clientes: crea y administra clientes
- Reportes: genera PDF de inventario y ventas
- Configuración: ajustes generales (tema, datos de la cafetería)

## Flujo de trabajo típico
- Inicia sesión como `admin`
- Revisa o carga productos en Inventario
- Registra una venta en Ventas
- Genera un reporte en PDF desde Reportes

## Generación de PDF
- Desde Reportes elige el tipo de reporte y genera
- Los archivos se guardan en `pdfs_generados/`

## Consejos
- Usa el botón de Configuración para ajustar tema y datos
- Mantén actualizado el inventario para que las ventas sean correctas
- Realiza respaldos periódicos si trabajas con base de datos local

## Resolución de problemas
- No inicia: ejecuta `INSTALAR.bat` de nuevo y verifica Internet
- Error de base de datos: confirma que MySQL esté encendido y credenciales correctas (`NexusCoffee_Complete\modules\config.py:6`)
- No genera PDF: revisa permisos de la carpeta `pdfs_generados/`

## Cierre de sesión
- Usa el botón “Salir” del menú superior (`NexusCoffee_Complete\modules\views.py:175`)

## Datos por defecto
- Usuario: `admin`
- Contraseña: `admin123`

## Paso a Paso Detallado
- Inicio de sesión:
  - Ingresa `admin` y `admin123` (visible en pantalla de login) (`NexusCoffee_Complete\views\login_view.py:43`)
  - Presiona Enter o el botón “Iniciar Sesión” (`NexusCoffee_Complete\modules\views.py:69`)
- Dashboard:
  - Accede a módulos desde el menú superior (Ventas, Inventario, Clientes, Reportes, Configuración)
- Inventario:
  - Agregar producto: botón “Agregar” → completa nombre, precio, stock → guardar
  - Editar: selecciona producto → “Editar” → modifica y guarda
  - Eliminar: selecciona producto → “Eliminar” → confirma
  - Ordenar y buscar: usa encabezados de columna y caja de búsqueda
- Ventas:
  - Selecciona productos → define cantidad → agrega al carrito
  - Aplica descuentos si corresponde → confirma la venta
  - Genera comprobante/recibo si está habilitado
- Clientes:
  - Agregar cliente: nombre, email y teléfono
  - Editar/Eliminar desde la lista de clientes
- Reportes:
  - Inventario: genera PDF con stock actual
  - Ventas: genera PDF por rango de fechas
  - Ubicación de PDFs: carpeta `pdfs_generados/`
- Configuración:
  - Cambia tema (claro/oscuro), datos de la cafetería y preferencias
  - Ajusta parámetros como moneda y stock mínimo (`NexusCoffee_Complete\modules\config.py:17`)

## Atajos y Consejos
- Enter para confirmar login (`NexusCoffee_Complete\modules\views.py:69`)
- Mantén el inventario al día para evitar errores en ventas
- Revisa reportes periódicamente para control de negocio

## Errores y Soluciones
- No abre la aplicación:
  - Ejecuta `INSTALAR.bat` nuevamente para reinstalar dependencias
  - Verifica que tengas conexión a Internet para la instalación
- Error de base de datos:
  - Asegura que MySQL esté encendido y credenciales sean correctas (`NexusCoffee_Complete\modules\config.py:6`)
  - Si cambiaste usuario/contraseña, actualízalos en `config_mysql.json` (`NexusCoffee_Complete\config_mysql.json:1`)
- No se generan PDFs:
  - Confirma permisos de escritura en `pdfs_generados/`

## Copias de Seguridad
- Realiza respaldos de la base de datos con herramientas MySQL (mysqldump)
- Guarda los respaldos en un lugar seguro fuera del equipo principal

## Cerrar Sesión
- Usa el botón “Salir” en la barra superior (`NexusCoffee_Complete\modules\views.py:175`)

## Preguntas Frecuentes (FAQ)
- ¿Cuál es el usuario inicial?
  - `admin` con contraseña `admin123`.
- ¿Dónde se guardan los reportes?
  - En la carpeta `pdfs_generados/`.
- ¿Puedo cambiar el tema?
  - Sí, en Configuración.
- ¿Cómo agrego un nuevo producto?
  - En Inventario, usa “Agregar”, completa datos y guarda.

