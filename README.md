# QuickExit

## Descripción General
QuickExit es una aplicación web desarrollada en Flask y MySQL, diseñada para la gestión eficiente de salidas y entradas de aprendices, instructores y personal administrativo en la institución SENA Regional Caquetá, Centro Tecnológico de la Amazonia (Florencia). El sistema automatiza y audita los procesos de control de acceso, permitiendo un seguimiento detallado y seguro de las actividades institucionales.

## Funcionalidades Principales

- **Gestión de Usuarios:**
  - Creación, edición, activación/inactivación y eliminación de usuarios con roles diferenciados (aprendiz, instructor, administrativo, portería).
  - Eliminación en cascada: al eliminar un usuario aprendiz, se eliminan automáticamente todas sus solicitudes, logs de auditoría y validaciones asociadas, garantizando la integridad y limpieza de la base de datos.

- **Gestión de Solicitudes de Salida:**
  - Los aprendices pueden registrar solicitudes de salida, que son validadas por instructores y administrativos.
  - El sistema permite el seguimiento del estado de cada solicitud (pendiente, aprobada, autorizada, rechazada, completada).

- **Auditoría General:**
  - Todas las acciones relevantes (creación, validación, eliminación de usuarios y solicitudes, cambios de estado, etc.) quedan registradas en la tabla `auditoria_general`.
  - Los logs incluyen: usuario que realizó la acción, tipo de acción, detalles, IP, agente de usuario y, si aplica, la solicitud asociada.
  - Los logs administrativos (como eliminación o cambio de estado de usuario) quedan registrados incluso si no están asociados a una solicitud específica.

- **Eliminación en Cascada:**
  - Al eliminar un usuario aprendiz, se eliminan automáticamente:
    - Sus solicitudes de salida.
    - Los registros de auditoría asociados a esas solicitudes.
    - Las validaciones asociadas a esas solicitudes.
  - Esto asegura que no queden datos huérfanos ni registros innecesarios en el sistema.

- **Interfaz de Administración:**
  - Paneles diferenciados para cada rol.
  - Búsqueda avanzada y filtros para gestión de usuarios y solicitudes.
  - Visualización clara del historial y estado de cada usuario y solicitud.

## Tecnologías Utilizadas
- **Backend:** Flask (Python)
- **Base de datos:** MySQL
- **Frontend:** HTML5, CSS3, JavaScript (con Bootstrap y FontAwesome)

## Instalación y Despliegue
1. Clona el repositorio y navega al directorio del proyecto.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configura la base de datos MySQL y ajusta los parámetros en `config.py`.
4. Ejecuta las migraciones y scripts de inicialización si es necesario.
5. Inicia la aplicación:
   ```bash
   python run.py
   ```

## Estructura de la Base de Datos
- **Usuarios:** Roles diferenciados, integridad referencial y eliminación en cascada.
- **Solicitudes:** Relacionadas con usuarios y tipos de salida.
- **Auditoría General:** Registro detallado de todas las acciones relevantes.
- **Validaciones:** Relacionadas con solicitudes y eliminadas en cascada.

## Licencia
Este proyecto está licenciado bajo los términos de uso institucional y es propiedad intelectual de **Miguel Stiven Cortés Duarte**.

## Institución
Desarrollado para resolver la problemática de control y auditoría de salidas en el **SENA Regional Caquetá / Florencia**.
