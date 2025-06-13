# QuickExit

![QuickExit Logo](app/static/img/logo.png)

## Descripción del Proyecto

**QuickExit** es una aplicación web diseñada para gestionar y validar las salidas y reingresos de aprendices en un entorno educativo, como el SENA. La plataforma ofrece diferentes paneles de control según el rol del usuario (Aprendiz, Instructor, Portero, Administrativo, Administrador), optimizando los procesos de solicitud, aprobación y registro de salidas.

## Características Principales

*   **Gestión de Usuarios:** Registro de aprendices y creación de usuarios administrativos (instructores, porteros). Ahora incluye un panel avanzado para que los administradores gestionen, busquen y eliminen usuarios (excepto administradores).
*   **Roles y Permisos:** Acceso diferenciado basado en roles (Aprendiz, Instructor, Portero, Administrativo, Administrador).
*   **Solicitudes de Salida:** Los aprendices pueden crear solicitudes de salida con motivos y horarios estimados.
*   **Validación de Instructores:** Los instructores líderes de ficha pueden aprobar o rechazar las solicitudes de salida de sus aprendices, así como validar sus registros.
*   **Validación Administrativa:** El personal administrativo puede validar las solicitudes de salida aprobadas por los instructores y gestionar fichas y porteros.
*   **Registro de Portería:** Los porteros registran las horas exactas de salida y reingreso de los aprendices.
*   **Historial de Solicitudes:** Seguimiento del estado y el historial de todas las solicitudes.
*   **Gestión de Fichas:** Creación, administración y habilitación/deshabilitación de fichas.
*   **Gestión de Instructores Líderes:** Asignación y remoción de instructores líderes para cada ficha.
*   **Buscadores AJAX:** Funcionalidad de búsqueda avanzada en tablas para usuarios, fichas, porteros e instructores, con filtros dinámicos.

## Tecnologías Utilizadas

*   **Backend:** Flask (Python)
*   **Base de Datos:** SQLite (desarrollo), PostgreSQL (producción - adaptable)
*   **ORM:** SQLAlchemy con Flask-SQLAlchemy
*   **Autenticación:** Flask-Login, Flask-Bcrypt
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS, AJAX)
*   **Estilos y Iconografía:** Font Awesome
*   **Manejo de Dependencias:** `pip`

## Configuración del Entorno

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local:

1.  **Clonar el Repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd QuickExit
    ```

2.  **Crear y Activar un Entorno Virtual:**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuración de Variables de Entorno (Opcional pero recomendado):**
    Crea un archivo `.env` en la raíz del proyecto para variables sensibles o de configuración.
    ```
    # Ejemplo de .env
    SECRET_KEY='tu_clave_secreta_aqui'
    DATABASE_URL='sqlite:///site.db'
    ```

## Configuración de la Base de Datos

1.  **Inicializar la Base de Datos:**
    ```bash
    python init_db.py
    ```

2.  **Crear Tablas y Migraciones (si aplicara cambios en modelos):
    (Este proyecto utiliza un enfoque directo, pero si se usan Flask-Migrate, los comandos serían así:)
    ```bash
    # flask db init
    # flask db migrate -m "Initial migration"
    # flask db upgrade
    ```

## Creación de Usuario Administrador Inicial

Ejecuta el siguiente script para crear un usuario con rol de `admin`:

```bash
python init_admin.py
```

Este script te pedirá que ingreses un documento, nombre, email y contraseña para el usuario administrador.

## Ejecución de la Aplicación

Para iniciar la aplicación en modo desarrollo, ejecuta:

```bash
python run.py
# O para desarrollo local con reinicio automático:
python localRun.py
```

La aplicación estará disponible en `http://127.0.0.1:5000`.

## Estructura del Proyecto

```
QuickExit/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── administrativo/
│   │   │       ├── admin.css
│   │   │       ├── crear_usuario.css
│   │   │       ├── dashboard.css
│   │   │       ├── gestionar_instructores_lideres.css
│   │   │       ├── gestionar_usuarios.css  
│   │   │       ├── instructores.css
│   │   │       ├── porteros.css
│   │   │       └── validar_salidas.css
│   │   └── js/
│   │       └── administrativo/
│   │           └── buscador_ajax/
│   │               ├── gestionar_usuarios.js 
│   │               └── porteros.js
│   ├── templates/
│   │   ├── administrativo/
│   │   │   ├── crear_usuario.html
│   │   │   ├── dashboard.html
│   │   │   ├── fichas/
│   │   │   ├── gestionar_instructores_lideres.html
│   │   │   ├── gestionar_usuarios.html  
│   │   │   ├── instructores.html
│   │   │   ├── porteros.html
│   │   │   └── validar_salidas.html
│   │   └── base.html
│   │   └── (otros templates por rol)
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
├── config.py
├── init_admin.py
├── init_db.py
├── requirements.txt
├── run.py
├── localRun.py
└── README.md  <-- Este archivo
```

## Uso de la Aplicación

### Registro y Login
*   **Registro:** Los aprendices pueden registrarse directamente en la plataforma. Su cuenta quedará pendiente de validación por su instructor líder.
*   **Login:** Todos los usuarios inician sesión con sus credenciales.

### Paneles por Rol

*   **Aprendiz:** Dashboard con opción para crear nuevas solicitudes de salida y ver su historial.
*   **Instructor:** Panel para gestionar solicitudes de salida de sus aprendices y validar cuentas de aprendices.
*   **Portero:** Dashboard para registrar las horas exactas de salida y reingreso de los aprendices cuyas solicitudes han sido aprobadas.
*   **Administrativo/Administrador:** Acceso completo a paneles de gestión.

### Panel Administrativo (Detallado)

El panel administrativo (`/administrativo`) ofrece las siguientes secciones:

*   **Gestión de Usuarios:**
    *   **Crear Usuario:** Permite crear nuevos usuarios con roles de `instructor` o `porteria`.
    *   **Gestionar Usuarios:** (NUEVO) Permite buscar, filtrar y eliminar usuarios del sistema (excepto administradores). Puedes buscar por documento, nombre, email, ficha (para aprendices e instructores) y filtrar por rol.
*   **Gestión de Fichas:** Crear nuevas fichas o administrar el estado (habilitar/deshabilitar) de las fichas existentes. Incluye un buscador avanzado.
*   **Validar Salidas:** Revisar y gestionar las solicitudes de salida que han sido aprobadas por los instructores.
*   **Gestionar Instructores:** Ver y buscar instructores registrados. Permite asignar o remover instructores líderes a fichas.
*   **Validar Porteros:** Aprobar o rechazar las cuentas de porteros registrados, así como cambiar su estado.

## Contribuir

Para contribuir al proyecto, por favor, sigue el flujo de trabajo estándar de Git: fork, branch, commit, push y pull request. Asegúrate de seguir las convenciones de código existentes.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` (si existe) para más detalles. 
