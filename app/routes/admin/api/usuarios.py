from flask import Blueprint, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Ficha, RolesEnum, Solicitud, AuditoriaGeneral
from sqlalchemy import or_

admin_api_usuarios = Blueprint('admin_api_usuarios', __name__)

# Buscar usuarios (API)
@admin_api_usuarios.route('/api/buscar_usuarios')
@login_required
def api_buscar_usuarios():
    if current_user.rol.value not in ['admin', 'administrativo']:
        return jsonify({'error': 'No autorizado'}), 403

    buscar_documento = request.args.get('buscar_documento', '').strip()
    buscar_nombre = request.args.get('buscar_nombre', '').strip()
    buscar_email = request.args.get('buscar_email', '').strip()
    buscar_ficha = request.args.get('buscar_ficha', '').strip()
    buscar_rol = request.args.get('buscar_rol', '').strip()

    query = db.session.query(Usuario, Ficha).outerjoin(Ficha, or_(
        Usuario.id_ficha == Ficha.id_ficha,
        Usuario.id_usuario == Ficha.id_instructor_lider
    )).filter(
        (Usuario.rol != RolesEnum.admin) &
        (Usuario.rol != RolesEnum.administrativo)
    )

    if buscar_documento:
        query = query.filter(Usuario.documento.like(f"%{buscar_documento}%"))
    if buscar_nombre:
        query = query.filter(Usuario.nombre.ilike(f"%{buscar_nombre}%"))
    if buscar_email:
        query = query.filter(Usuario.email.ilike(f"%{buscar_email}%"))
    if buscar_rol:
        query = query.filter(Usuario.rol == RolesEnum(buscar_rol))
    if buscar_ficha:
        try:
            ficha_id_valido = int(buscar_ficha)
            query = query.filter(Ficha.id_ficha == ficha_id_valido)
        except ValueError:
            query = query.filter(Ficha.id_ficha == -1)

    results = query.all()
    usuarios_json = []
    processed_user_ids = set()
    for usr, ficha in results:
        if usr.id_usuario not in processed_user_ids:
            ficha_info = None
            if ficha:
                ficha_info = {'id_ficha': ficha.id_ficha, 'nombre': ficha.nombre}
            usuarios_json.append({
                'id_usuario': usr.id_usuario,
                'documento': usr.documento,
                'nombre': usr.nombre,
                'email': usr.email,
                'rol': usr.rol.value,
                'ficha': ficha_info,
                'validado': usr.validado
            })
            processed_user_ids.add(usr.id_usuario)
    return jsonify({'usuarios': usuarios_json})

# Eliminar usuario (API)
@admin_api_usuarios.route('/api/eliminar_usuario/<int:id_usuario>', methods=['POST'])
@login_required
def eliminar_usuario(id_usuario):
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return jsonify({'success': False, 'message': 'Acceso no autorizado'}), 403
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    if usuario.rol == RolesEnum.admin:
        flash("No se puede eliminar un usuario con rol de administrador.", "danger")
        return jsonify({'success': False, 'message': 'No se puede eliminar un usuario con rol de administrador.'}), 400
    try:
        # Eliminamos el bloqueo por solicitudes asociadas, confiando en el ON DELETE CASCADE
        if usuario.rol == RolesEnum.instructor:
            fichas_lideradas = Ficha.query.filter_by(id_instructor_lider=id_usuario)
            if fichas_lideradas.count() > 0:
                fichas_lideradas.update({'id_instructor_lider': None}, synchronize_session=False)
            if hasattr(Solicitud, 'id_instructor_aprobador'):
                solicitudes_aprobadas = Solicitud.query.filter_by(id_instructor_aprobador=id_usuario)
                if solicitudes_aprobadas.count() > 0:
                    solicitudes_aprobadas.update({'id_instructor_aprobador': None}, synchronize_session=False)
        nombre_usuario = usuario.nombre
        db.session.delete(usuario)
        db.session.commit()
        # Auditoría
        try:
            log = AuditoriaGeneral(
                id_usuario=current_user.id_usuario,
                id_solicitud=None,
                accion='eliminar_usuario',
                detalles=f'Usuario eliminado: {nombre_usuario} (ID: {id_usuario})',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error al registrar log de auditoría: {e}")
        flash(f"Usuario {nombre_usuario} eliminado exitosamente.", "success")
        return jsonify({'success': True, 'message': f'Usuario {nombre_usuario} eliminado exitosamente.'})
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error al eliminar el usuario: {str(e)}"
        flash(error_msg, "danger")
        return jsonify({'success': False, 'message': error_msg}), 500

# Actualizar estado de usuario (API)
@admin_api_usuarios.route('/api/actualizar_estado_usuario/<int:id_usuario>', methods=['POST'])
@login_required
def actualizar_estado_usuario(id_usuario):
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    usuario = Usuario.query.get_or_404(id_usuario)
    validado_str = request.form.get('validado')
    usuario.validado = (validado_str == 'true')
    db.session.commit()
    # Auditoría
    try:
        log = AuditoriaGeneral(
            id_usuario=current_user.id_usuario,
            id_solicitud=None,
            accion='actualizar_estado_usuario',
            detalles=f'Usuario: {usuario.nombre} (ID: {usuario.id_usuario}), Nuevo estado: {usuario.validado}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar log de auditoría: {e}")
    flash(f"Estado de usuario {usuario.nombre} actualizado a {'Activo' if usuario.validado else 'Inactivo'}.", "success")
    return jsonify(message="Estado actualizado con éxito."), 200 