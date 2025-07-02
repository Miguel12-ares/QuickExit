from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Ficha, Solicitud, EstadoSolicitud, RolesEnum, SolicitudValidaciones
from datetime import datetime, date

instructor_bp = Blueprint('instructor', __name__)

# ------------------------------------------
# Dashboard de Instructor
# ------------------------------------------
@instructor_bp.route('/instructor')
@login_required
def instructor_dashboard():
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitudes_pendientes = Solicitud.query.filter_by(estado=EstadoSolicitud.pendiente).all()
    solicitudes_historial = Solicitud.query.filter(
        Solicitud.validacion.has(id_instructor_validador=current_user.id_usuario)
    ).all()
    return render_template('instructor/instructor.html', pendientes=solicitudes_pendientes, historial=solicitudes_historial)

# ------------------------------------------
# Gestionar Solicitud
# ------------------------------------------
@instructor_bp.route('/instructor/gestionar/<int:id_solicitud>/<accion>', methods=['POST'])
@login_required
def instructor_gestionar_solicitud(id_solicitud, accion):
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('instructor.instructor_dashboard'))
    solicitud = Solicitud.query.get_or_404(id_solicitud)
    if solicitud.estado != EstadoSolicitud.pendiente:
        flash("La solicitud ya fue gestionada.", "info")
        return redirect(url_for('instructor.instructor_dashboard'))
    if accion == 'aprobar':
        solicitud.estado = EstadoSolicitud.aprobada
        # Crear registro de validación si no existe
        if not solicitud.id_validacion:
            validacion = SolicitudValidaciones(
                id_solicitud=solicitud.id_solicitud,
                id_instructor_validador=current_user.id_usuario,
                fecha_validacion_instructor=datetime.now()
            )
            db.session.add(validacion)
            db.session.flush()  # Para obtener el id_validacion
            solicitud.id_validacion = validacion.id_validacion
        else:
            validacion = solicitud.validacion
            validacion.id_instructor_validador = current_user.id_usuario
            validacion.fecha_validacion_instructor = datetime.now()
        flash("Solicitud aprobada. Pasa al área administrativa.", "success")
    elif accion == 'rechazar':
        solicitud.estado = EstadoSolicitud.rechazada
        # Igual que arriba, pero para rechazos
        if not solicitud.id_validacion:
            validacion = SolicitudValidaciones(
                id_solicitud=solicitud.id_solicitud,
                id_instructor_validador=current_user.id_usuario,
                fecha_validacion_instructor=datetime.now()
            )
            db.session.add(validacion)
            db.session.flush()
            solicitud.id_validacion = validacion.id_validacion
        else:
            validacion = solicitud.validacion
            validacion.id_instructor_validador = current_user.id_usuario
            validacion.fecha_validacion_instructor = datetime.now()
        flash("Solicitud rechazada.", "info")
    else:
        flash("Acción no válida.", "danger")
        return redirect(url_for('instructor.instructor_dashboard'))
    db.session.commit()
    return redirect(url_for('instructor.instructor_dashboard'))

# ------------------------------------------
# Validar Aprendices
# ------------------------------------------
@instructor_bp.route('/instructor/validar_aprendices')
@login_required
def validar_aprendices():
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    fichas_lider = Ficha.query.filter_by(id_instructor_lider=current_user.id_usuario).all()
    aprendices_pendientes = []
    if not fichas_lider:
        flash("No tienes fichas asignadas como instructor líder", "warning")
        return render_template('instructor/validar_aprendices.html', aprendices=aprendices_pendientes, fichas=fichas_lider)
    aprendices_pendientes = Usuario.query.filter(
        Usuario.rol == RolesEnum.aprendiz,
        Usuario.validado == False,
        Usuario.id_ficha.in_([f.id_ficha for f in fichas_lider])
    ).all()
    return render_template('instructor/validar_aprendices.html', aprendices=aprendices_pendientes, fichas=fichas_lider)

# ------------------------------------------
# Validar Aprendiz
# ------------------------------------------
@instructor_bp.route('/instructor/validar_aprendiz/<int:id_usuario>/<accion>', methods=['POST'])
@login_required
def validar_aprendiz(id_usuario, accion):
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    aprendiz = Usuario.query.get_or_404(id_usuario)
    ficha = Ficha.query.filter_by(id_ficha=aprendiz.id_ficha, id_instructor_lider=current_user.id_usuario).first()
    if not ficha:
        flash("No tienes permiso para validar a este aprendiz", "danger")
        return redirect(url_for('instructor.validar_aprendices'))
    if accion == 'aprobar':
        aprendiz.validado = True
        flash(f"Aprendiz {aprendiz.nombre} validado correctamente", "success")
    elif accion == 'rechazar':
        db.session.delete(aprendiz)
        flash(f"Aprendiz {aprendiz.nombre} rechazado", "info")
    else:
        flash("Acción no válida", "danger")
        return redirect(url_for('instructor.validar_aprendices'))
    db.session.commit()
    return redirect(url_for('instructor.validar_aprendices'))

# ------------------------------------------
# Solicitudes Pendientes
# ------------------------------------------
@instructor_bp.route('/instructor/solicitudes_pendientes')
@login_required
def instructor_solicitudes_pendientes():
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitudes_pendientes = Solicitud.query.filter_by(estado=EstadoSolicitud.pendiente).all()
    return render_template('instructor/solicitudes_pendientes.html', pendientes=solicitudes_pendientes)

# ------------------------------------------
# Historial de Solicitudes
# ------------------------------------------
@instructor_bp.route('/instructor/historial')
@login_required
def instructor_historial():
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitudes_historial = Solicitud.query.filter(
        Solicitud.validacion.has(id_instructor_validador=current_user.id_usuario)
    ).all()
    return render_template('instructor/historial.html', historial=solicitudes_historial) 