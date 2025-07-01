# QuickExit

QuickExit es una plataforma web para la gestión de salidas, usuarios y fichas en entornos educativos, orientada a la administración eficiente y segura de permisos y roles.

## Características principales

- Gestión de usuarios por roles: aprendices, instructores, administrativos y portería.
- Registro y validación de salidas y reingresos.
- Paneles diferenciados para cada tipo de usuario.
- Administración de fichas y asignación de instructores líderes.
- Sistema de notificaciones elegante y centralizado para mensajes, alertas y confirmaciones.
- Control de acceso y validación de datos.

## Instalación

1. Clona el repositorio:
   ```bash
   git clone <url-del-repo>
   cd QuickExit
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configura la base de datos y variables de entorno según `config.py`.
4. Ejecuta la aplicación:
   ```bash
   python run.py
   ```

## Uso

- Accede a la aplicación en `http://localhost:5000`.
- Regístrate como aprendiz (solo fichas habilitadas aparecerán en el registro).
- Los administrativos pueden crear, habilitar/deshabilitar y asignar instructores a fichas desde el panel de administración.
- El sistema de notificaciones muestra mensajes de éxito, error, advertencia y confirmaciones de manera elegante y no intrusiva.
- Todas las acciones críticas (eliminar, aprobar, rechazar) requieren doble confirmación mediante notificaciones.

## Notificaciones elegantes

- Todas las alertas y confirmaciones usan un sistema de notificaciones visual, moderno y centralizado.
- Los mensajes flash de Flask y las validaciones críticas se muestran como notificaciones en la interfaz.
- El sistema reemplaza el uso de `alert()` y `confirm()` nativos.
- Las notificaciones pueden tener acciones personalizadas y doble validación para operaciones sensibles.

## Restricciones y validaciones

- **Registro de aprendices:** solo pueden seleccionar fichas habilitadas y con instructor líder asignado.
- **Asignación de instructores:** solo se pueden asignar instructores validados a fichas habilitadas.
- **Creación de fichas:** no se permite asignar instructores vacíos o inválidos.
- **Panel de administración de fichas:** permite ver y gestionar tanto fichas habilitadas como deshabilitadas.

## Estructura del proyecto

- `app/` - Código principal de la aplicación (Flask, modelos, rutas, plantillas, estáticos)
- `migrations/` - Archivos de migración de base de datos
- `requirements.txt` - Dependencias del proyecto
- `run.py` - Script principal para ejecutar la app

## Contribución

1. Haz un fork del repositorio.
2. Crea una rama para tu feature o fix.
3. Haz tus cambios y abre un Pull Request.

## Licencia

MIT
