from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Usuario, RolesEnum

admin_api_instructores = Blueprint('admin_api_instructores', __name__)

@admin_api_instructores.route('/api/buscar_instructores')
@login_required
def api_buscar_instructores():
    if current_user.rol.value not in ['admin', 'administrativo']:
        return jsonify({'error': 'No autorizado'}), 403
    buscar_id = request.args.get('buscar_id', '').strip()
    buscar_nombre = request.args.get('buscar_nombre', '').strip()
    buscar_email = request.args.get('buscar_email', '').strip()
    query = Usuario.query.filter_by(rol=RolesEnum.instructor, validado=True)
    if buscar_id:
        query = query.filter(Usuario.id_usuario.like(f"%{buscar_id}%"))
    if buscar_nombre:
        query = query.filter(Usuario.nombre.ilike(f"%{buscar_nombre}%"))
    if buscar_email:
        query = query.filter(Usuario.email.ilike(f"%{buscar_email}%"))
    instructores = query.all()
    result = []
    for i in instructores:
        ficha_nombre = i.ficha.nombre if i.ficha and i.ficha.habilitada else None
        result.append({
            'id_usuario': i.id_usuario,
            'nombre': i.nombre,
            'email': i.email,
            'ficha_nombre': ficha_nombre,
            'validado': i.validado
        })
    return jsonify({'instructores': result}) 