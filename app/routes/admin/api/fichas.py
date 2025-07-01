from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Ficha, Usuario, RolesEnum

admin_api_fichas = Blueprint('admin_api_fichas', __name__)

@admin_api_fichas.route('/api/buscar_fichas')
@login_required
def api_buscar_fichas():
    if current_user.rol.value not in ['administrativo', 'admin']:
        return jsonify({'error': 'No autorizado'}), 403
    buscar_id = request.args.get('buscar_id', '').strip()
    buscar_nombre = request.args.get('buscar_nombre', '').strip()
    buscar_instructor = request.args.get('buscar_instructor', '').strip()
    solo_habilitadas = request.args.get('solo_habilitadas', None)
    query = Ficha.query
    if solo_habilitadas == '1':
        query = query.filter_by(habilitada=True)
    if buscar_id:
        query = query.filter(Ficha.id_ficha.like(f"%{buscar_id}%"))
    if buscar_nombre:
        query = query.filter(Ficha.nombre.ilike(f"%{buscar_nombre}%"))
    if buscar_instructor:
        query = query.filter(Ficha.instructor_lider.has(Usuario.nombre.ilike(f"%{buscar_instructor}%")))
    fichas = query.all()
    fichas_json = []
    for ficha in fichas:
        fichas_json.append({
            'id_ficha': ficha.id_ficha,
            'nombre': ficha.nombre,
            'instructor_lider': ficha.instructor_lider.nombre if ficha.instructor_lider else 'Sin asignar',
            'id_instructor_lider': ficha.id_instructor_lider,
            'fecha_creacion': ficha.fecha_creacion.strftime('%Y-%m-%d'),
            'habilitada': ficha.habilitada,
            'descripcion': ficha.descripcion or '-'
        })
    return jsonify({'fichas': fichas_json}) 