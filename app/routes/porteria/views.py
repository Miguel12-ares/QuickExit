from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Ficha, Solicitud, EstadoSolicitud, RolesEnum, SolicitudValidaciones
from datetime import datetime, date

porteria_bp = Blueprint('porteria', __name__)

# ------------------------------------------
# Dashboard de Portería
# ------------------------------------------
@porteria_bp.route('/porteria')
@login_required
def porteria_dashboard():
    if current_user.rol.value != 'porteria':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    return render_template('porteria/dashboard.html')

# ------------------------------------------
# Solicitudes de Salida
# ------------------------------------------
@porteria_bp.route('/porteria/solicitudes_salida')
@login_required
def porteria_solicitudes_salida():
    if current_user.rol.value != 'porteria':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitudes_salida = Solicitud.query.filter_by(estado=EstadoSolicitud.autorizada).all()
    return render_template('porteria/registrar_salida.html', solicitudes_salida=solicitudes_salida)

# ------------------------------------------
# Solicitudes de Reingreso
# ------------------------------------------
@porteria_bp.route('/porteria/solicitudes_reingreso')
@login_required
def porteria_solicitudes_reingreso():
    if current_user.rol.value != 'porteria':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitudes_reingreso = Solicitud.query.join(Solicitud.validacion).filter(
        Solicitud.estado == EstadoSolicitud.completada,
        Solicitud.tipo_salida.has(nombre='Temporal'),
        SolicitudValidaciones.fecha_validacion_portero_reingreso == None
    ).all()
    return render_template('porteria/registrar_reingreso.html', solicitudes_reingreso=solicitudes_reingreso)

# ------------------------------------------
# Registrar Reingreso
# ------------------------------------------
@porteria_bp.route('/porteria/registrar_reingreso/<int:id_solicitud>', methods=['POST'])
@login_required
def porteria_registrar_reingreso(id_solicitud):
    if current_user.rol.value != 'porteria':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitud = Solicitud.query.get_or_404(id_solicitud)
    if solicitud.id_validacion:
        validacion = solicitud.validacion
        validacion.id_portero_validador_reingreso = current_user.id_usuario
        now = datetime.now()
        validacion.fecha_validacion_portero_reingreso = now
        if hasattr(solicitud, 'hora_exacta_reingreso'):
            solicitud.hora_exacta_reingreso = now.time()
    db.session.commit()
    flash("Hora de reingreso registrada correctamente.", "success")
    return redirect(url_for('porteria.porteria_dashboard'))

# ------------------------------------------
# Registrar Salida
# ------------------------------------------
@porteria_bp.route('/porteria/registrar_salida/<int:id_solicitud>', methods=['POST'])
@login_required
def porteria_registrar_salida(id_solicitud):
    if current_user.rol.value != 'porteria':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitud = Solicitud.query.get_or_404(id_solicitud)
    solicitud.estado = EstadoSolicitud.completada
    if solicitud.id_validacion:
        validacion = solicitud.validacion
        validacion.id_portero_validador_salida = current_user.id_usuario
        now = datetime.now()
        validacion.fecha_validacion_portero_salida = now
        if hasattr(solicitud, 'hora_exacta_salida'):
            solicitud.hora_exacta_salida = now.time()
    db.session.commit()
    flash("Hora de salida registrada correctamente.", "success")
    return redirect(url_for('porteria.porteria_dashboard')) 