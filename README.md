# QuickExit


## Descripción del Proyecto

**QuickExit** es una aplicación web para la gestión y validación de salidas y reingresos de aprendices en entornos educativos (como el SENA). Ofrece paneles diferenciados según el rol del usuario (Aprendiz, Instructor, Portero, Administrativo, Administrador) y optimiza los procesos de solicitud, aprobación y registro de salidas.

## Características Principales

- **Gestión de Usuarios:** Registro de aprendices y creación/gestión de usuarios administrativos (instructores, porteros, administrativos, admin).
- **Roles y Permisos:** Acceso diferenciado y paneles personalizados para cada rol.
- **Solicitudes de Salida:** Los aprendices pueden crear solicitudes de salida con motivos y horarios estimados.
- **Validación de Instructores y Administrativos:** Aprobación/rechazo de solicitudes y validación de cuentas.
- **Registro de Portería:** Registro de horas exactas de salida y reingreso.
- **Historial y Seguimiento:** Visualización del estado y el historial de todas las solicitudes.
- **Gestión de Fichas:** Creación, administración, habilitación/deshabilitación y asignación de instructores líderes.
- **Buscadores AJAX:** Búsqueda avanzada y filtros dinámicos en tablas de usuarios, fichas, porteros e instructores.
- **Notificaciones Elegantes:** Sistema centralizado de notificaciones visuales para mensajes, alertas y confirmaciones (incluye doble validación en acciones críticas).

## Tecnologías Utilizadas

*   **Backend:** Flask (Python)
*   **Base de Datos:** MySQL (producción - adaptable)
*   **ORM:** SQLAlchemy con Flask-SQLAlchemy
*   **Autenticación:** Flask-Login, Flask-Bcrypt
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS, AJAX)
*   **Estilos y Iconografía:** Font Awesome
*   **Manejo de Dependencias:** `pip`
## Configuración y Puesta en Marcha

### 1. Clonar el Repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd QuickExit
```

### 2. Crear y Activar un Entorno Virtual
```bash
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configuración de Variables de Entorno
Puedes crear un archivo `.env` o configurar variables de entorno para:
- `SQLALCHEMY_DATABASE_URI` (por defecto: MySQL local)
- `SECRET_KEY` (clave secreta para sesiones)

Ejemplo `.env`:
```
SECRET_KEY='tu_clave_secreta'
SQLALCHEMY_DATABASE_URI='mysql+pymysql://usuario:password@localhost/quickexit_db'
```

### 5. Inicializar la Base de Datos
```bash
python init_db.py
```
Esto creará todas las tablas necesarias.

### 6. Crear Usuario Administrador Inicial
Ejecuta el siguiente script para crear un usuario admin por defecto:
```bash
python init_admin.py
```
Por defecto, el usuario creado es:
- Documento: `0001`
- Nombre: `Administrador`
- Email: `admin@quickexit.com`
- Contraseña: `1234`

Puedes modificar estos valores en `init_admin.py` antes de ejecutar el script.

### 7. Ejecutar la Aplicación
- Para desarrollo local:
  ```bash
  python run.py
  # O
  python localRun.py
  ```
- Accede a la app en: [http://localhost:5000](http://localhost:5000)

## Estructura del Proyecto

```
QuickExit/
├── app/
│   ├── static/
│   ├── templates/
│   ├── models.py
│   ├── routes/
│   └── ...
├── migrations/
├── config.py
├── init_admin.py
├── init_db.py
├── requirements.txt
├── run.py
├── localRun.py
└── README.md
```

## Uso de la Aplicación

### Registro y Validación
- **Aprendices:** Se registran directamente. Solo pueden elegir fichas habilitadas y con instructor líder asignado. Su cuenta queda pendiente de validación por el instructor líder.
- **Administradores:** Crean usuarios administrativos, instructores y porteros desde el panel.
- **Validaciones:** Todas las acciones críticas (eliminar, aprobar, rechazar) requieren doble confirmación mediante notificaciones elegantes.

### Paneles por Rol
- **Aprendiz:** Solicitud y seguimiento de salidas.
- **Instructor:** Validación de aprendices y solicitudes.
- **Portero:** Registro de salidas y reingresos.
- **Administrativo/Admin:** Gestión completa de usuarios, fichas, instructores y solicitudes.

### Panel Administrativo
- **Gestión de Usuarios:** Crear, buscar, filtrar y eliminar usuarios (excepto admin).
- **Gestión de Fichas:** Crear, habilitar/deshabilitar, asignar/remover instructores líderes.
- **Validar Salidas:** Gestionar solicitudes aprobadas por instructores.
- **Buscadores AJAX:** Búsqueda avanzada en todas las tablas administrativas.

## Notificaciones y Confirmaciones
- Todas las alertas y confirmaciones usan un sistema visual moderno.
- Doble validación para acciones críticas (eliminar, aprobar, rechazar).
- Los mensajes flash de Flask se muestran como notificaciones elegantes.

## Contribuir

1. Haz un fork del repositorio.
2. Crea una rama para tu feature o fix.
3. Haz tus cambios y abre un Pull Request.

## Licencia

MIT
