from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Ficha, TipoSalida, Solicitud, EstadoSolicitud, RolesEnum
from datetime import datetime

aprendiz_bp = Blueprint('aprendiz', __name__)

# ------------------------------------------
# Dashboard del Aprendiz
# ------------------------------------------
@aprendiz_bp.route('/aprendiz/dashboard')
@login_required
def aprendiz_dashboard():
    if current_user.rol.value != 'aprendiz':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('main.dashboard'))
    return render_template('aprendiz/dashboard.html')

# ------------------------------------------
# Nueva Solicitud de Aprendiz
# ------------------------------------------
@aprendiz_bp.route('/aprendiz/nueva_solicitud', methods=['GET', 'POST'])
@login_required
def aprendiz_nueva_solicitud():
    if current_user.rol.value != 'aprendiz':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('main.dashboard'))
    tipos_salida = TipoSalida.query.all()
    if request.method == 'POST':
        nueva_solicitud_obj = Solicitud(
            id_aprendiz=current_user.id_usuario,
            id_tipo_salida=request.form.get('tipo_salida'),
            hora_salida_estimada=request.form.get('hora_salida'),
            hora_reingreso_estimada=request.form.get('hora_reingreso'),
            motivo=request.form.get('motivo'),
            estado=EstadoSolicitud.pendiente,
            fecha_creacion=datetime.now()
        )
        db.session.add(nueva_solicitud_obj)
        db.session.commit()
        flash('Solicitud creada exitosamente', 'success')
        return redirect(url_for('aprendiz.aprendiz_dashboard'))
    return render_template('aprendiz/nueva_solicitud.html', tipos_salida=tipos_salida)

# ------------------------------------------
# Historial de Solicitudes del Aprendiz
# ------------------------------------------
@aprendiz_bp.route('/aprendiz/historial')
@login_required
def aprendiz_historial():
    if current_user.rol.value != 'aprendiz':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('main.dashboard'))
    solicitudes = Solicitud.query.filter_by(id_aprendiz=current_user.id_usuario).all()
    return render_template('aprendiz/historial.html', solicitudes=solicitudes) 