from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Importar vistas (esto debe estar antes de importar APIs)
from . import views

# Importar APIs para que sus rutas se agreguen al blueprint principal
from .api import usuarios, instructores, fichas
from .api.fichas import admin_api_fichas
from .api.usuarios import admin_api_usuarios
from .api.instructores import admin_api_instructores

admin_bp.register_blueprint(admin_api_fichas)
admin_bp.register_blueprint(admin_api_usuarios)
admin_bp.register_blueprint(admin_api_instructores)

__all__ = ['admin_bp'] 