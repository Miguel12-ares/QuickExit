from .main import main_bp
from .admin import admin_bp
from .aprendiz import aprendiz_bp
from .porteria import porteria_bp
from .instructor import instructor_bp

# Aquí se pueden importar y registrar otros blueprints en el futuro

__all__ = [
    'main_bp',
    'admin_bp',
    'aprendiz_bp',
    'porteria_bp',
    'instructor_bp',
] 