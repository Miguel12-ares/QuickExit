from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models import Usuario, Ficha, RolesEnum, Solicitud, EstadoSolicitud
from . import admin_bp  # Importar el blueprint desde __init__.py
from datetime import datetime

# ------------------------------------------
# Panel Administrativo Principal
# ------------------------------------------
@admin_bp.route('/administrativo', endpoint='administrativo_dashboard')
@login_required
def administrativo_dashboard():
    print('DEBUG: Entrando a administrativo_dashboard')
    if current_user.rol.value not in ['administrativo', 'admin']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    return render_template('administrativo/dashboard.html')

# Dashboard unificado de gestión de usuarios
@admin_bp.route('/administrativo/usuarios/dashboard')
@login_required
def gestionar_usuarios_dashboard():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    return render_template('administrativo/usuarios/dashboard.html')

# Formulario para crear usuario avanzado
@admin_bp.route('/administrativo/crear_usuario', methods=['GET'])
@login_required
def crear_usuario_avanzado_form():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    return render_template('administrativo/usuarios/crear_usuario.html')

# Proceso de creación de usuario avanzado
@admin_bp.route('/administrativo/crear_usuario', methods=['POST'])
@login_required
def crear_usuario_avanzado():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))

    documento = request.form.get('documento', '').strip()
    nombre = request.form.get('nombre', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    rol_str = request.form.get('rol', '').strip()

    if not documento or not nombre or not email or not password or not rol_str:
        flash('Todos los campos son obligatorios', 'danger')
        return redirect(url_for('admin.crear_usuario_avanzado_form'))

    if rol_str not in ['instructor', 'porteria']:
        flash('Rol no válido', 'danger')
        return redirect(url_for('admin.crear_usuario_avanzado_form'))

    usuario_existente = Usuario.query.filter(
        (Usuario.email == email) | (Usuario.documento == documento)
    ).first()
    if usuario_existente:
        flash('Usuario ya registrado con este email o documento', 'danger')
        return redirect(url_for('admin.crear_usuario_avanzado_form'))

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    rol = RolesEnum(rol_str)
    nuevo_usuario = Usuario(
        documento=documento,
        nombre=nombre,
        email=email,
        password_hash=hashed_pw,
        rol=rol,
        validado=True  # Los usuarios creados por administrativo están validados por defecto
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    flash(f'Usuario {nombre} creado exitosamente', 'success')
    return redirect(url_for('admin.gestionar_usuarios_dashboard'))

# ------------------------------------------
# Gestión de Fichas (Administrativo)
# ------------------------------------------
@admin_bp.route('/administrativo/fichas/crear', methods=['GET', 'POST'])
@login_required
def crear_ficha():
    if current_user.rol.value not in ['administrativo', 'admin']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    instructores = Usuario.query.filter_by(rol=RolesEnum.instructor, validado=True).all()
    if request.method == 'POST':
        id_ficha = request.form.get('id_ficha', '').strip()
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        id_instructor_lider = request.form.get('id_instructor_lider')
        if not id_ficha or not nombre:
            flash('El ID y el nombre de la ficha son obligatorios', 'danger')
            return redirect(url_for('admin.crear_ficha'))
        if Ficha.query.get(id_ficha):
            flash('Ya existe una ficha con ese ID', 'danger')
            return redirect(url_for('admin.crear_ficha'))
        ficha = Ficha(
            id_ficha=int(id_ficha),
            nombre=nombre,
            descripcion=descripcion,
            id_instructor_lider=id_instructor_lider if id_instructor_lider else None
        )
        db.session.add(ficha)
        db.session.commit()
        flash('Ficha creada exitosamente', 'success')
        return redirect(url_for('admin.administrar_fichas'))
    return render_template('administrativo/fichas/crear.html', instructores=instructores)

@admin_bp.route('/administrativo/fichas/administrar', methods=['GET', 'POST'])
@login_required
def administrar_fichas():
    if current_user.rol.value not in ['administrativo', 'admin']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        id_ficha = request.form.get('id_ficha')
        nuevo_estado = request.form.get('nuevo_estado')
        ficha = Ficha.query.get(id_ficha)
        if ficha:
            ficha.habilitada = True if nuevo_estado == 'activa' else False
            # Si se deshabilita, deshabilitar aprendices asociados
            if not ficha.habilitada:
                for aprendiz in ficha.usuarios:
                    aprendiz.validado = False
            db.session.commit()
            flash('Estado de la ficha actualizado correctamente', 'success')
        return redirect(url_for('admin.administrar_fichas'))
    return render_template('administrativo/fichas/administrar.html')

@admin_bp.route('/admin/validar_salidas')
@login_required
def validar_salidas():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitudes = Solicitud.query.filter_by(estado=EstadoSolicitud.aprobada).all()
    return render_template('administrativo/validar_salidas.html', solicitudes=solicitudes)

@admin_bp.route('/admin/asignar_instructor_lider/<int:id_ficha>', methods=['POST'])
@login_required
def asignar_instructor_lider(id_ficha):
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    ficha = Ficha.query.get_or_404(id_ficha)
    id_instructor = request.form.get('id_instructor')
    if not id_instructor:
        flash("Debe seleccionar un instructor", "danger")
        return redirect(url_for('admin.administrar_fichas'))
    instructor = Usuario.query.get_or_404(id_instructor)
    if instructor.rol != RolesEnum.instructor:
        flash("El usuario seleccionado no es un instructor", "danger")
        return redirect(url_for('admin.administrar_fichas'))
    ficha.id_instructor_lider = instructor.id_usuario
    db.session.commit()
    flash(f"Instructor {instructor.nombre} asignado como líder de la ficha {ficha.nombre}", "success")
    return redirect(url_for('admin.administrar_fichas'))

@admin_bp.route('/admin/remover_instructor_lider/<int:id_ficha>', methods=['POST'])
@login_required
def remover_instructor_lider(id_ficha):
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    ficha = Ficha.query.get_or_404(id_ficha)
    ficha.id_instructor_lider = None
    db.session.commit()
    flash(f"Instructor líder removido de la ficha {ficha.nombre}", "success")
    return redirect(url_for('admin.administrar_fichas'))

@admin_bp.route('/administrativo/gestionar_usuarios')
@login_required
def gestionar_usuarios():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    return render_template('administrativo/usuarios/gestionar_usuarios.html')

@admin_bp.route('/gestionar_solicitud/<int:id_solicitud>/<accion>', methods=['POST'], endpoint='admin_gestionar_solicitud')
@login_required
def admin_gestionar_solicitud(id_solicitud, accion):
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitud = Solicitud.query.get_or_404(id_solicitud)
    if solicitud.estado != EstadoSolicitud.aprobada:
        flash("La solicitud debe estar aprobada por el instructor primero.", "info")
        return redirect(url_for('admin.validar_salidas'))
    if accion == 'aprobar':
        solicitud.estado = EstadoSolicitud.autorizada
        if solicitud.id_validacion:
            validacion = solicitud.validacion
            validacion.id_administrativo_validador = current_user.id_usuario
            validacion.fecha_validacion_admin = datetime.now()
        flash("Salida validada y enviada a portería.", "success")
    elif accion == 'rechazar':
        solicitud.estado = EstadoSolicitud.rechazada
        if solicitud.id_validacion:
            validacion = solicitud.validacion
            validacion.id_administrativo_validador = current_user.id_usuario
            validacion.fecha_validacion_admin = datetime.now()
        flash("Salida rechazada.", "info")
    else:
        flash("Acción no válida.", "danger")
        return redirect(url_for('admin.validar_salidas'))
    db.session.commit()
    return redirect(url_for('admin.validar_salidas')) 