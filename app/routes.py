from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db, bcrypt
from app.models import Usuario, Ficha, TipoSalida, Solicitud, AuditoriaGeneral, EstadoSolicitud, RolesEnum
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date

main = Blueprint('main', __name__)

# ------------------------------------------
# Página de inicio
# ------------------------------------------
@main.route('/')
def home():
    return render_template('home.html')

# ------------------------------------------
# Registro de Usuarios
# ------------------------------------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    fichas = Ficha.query.all()  # Obtener todas las fichas (solo para aprendices)

    if request.method == 'POST':
        documento = request.form.get('documento', '').strip()
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        rol_str = request.form.get('rol', '').strip()
        id_ficha = request.form.get('id_ficha') if rol_str == 'aprendiz' else None

        if rol_str != 'aprendiz':
            flash('Solo se permite el registro de aprendices. Si eres instructor o portero, contacta al área administrativa.', 'danger')
            return redirect(url_for('main.register'))

        if not documento or not nombre or not email or not password or not rol_str:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('main.register'))

        if rol_str == 'aprendiz':
            ficha = Ficha.query.filter_by(id_ficha=id_ficha).first()
            if not ficha:
                flash('Ficha seleccionada no válida.', 'danger')
                return redirect(url_for('main.register'))
            
            if not ficha.instructor_lider:
                flash('Esta ficha no tiene un instructor líder asignado. Contacte al administrador.', 'danger')
                return redirect(url_for('main.register'))

        usuario_existente = Usuario.query.filter(
            (Usuario.email == email) | (Usuario.documento == documento)
        ).first()
        if usuario_existente:
            flash('Usuario ya registrado con este email o documento', 'danger')
            return redirect(url_for('main.register'))

        # Para "aprendiz" se requiere validación del instructor líder
        is_validado = False if rol_str == 'aprendiz' else True

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        rol = RolesEnum(rol_str)
        nuevo_usuario = Usuario(
            documento=documento,
            nombre=nombre,
            email=email,
            password_hash=hashed_pw,
            rol=rol,
            id_ficha=id_ficha,
            validado=is_validado
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        msg = 'Registro exitoso. Inicia sesión.' if is_validado else 'Registro exitoso. Tu cuenta está pendiente de validación por el instructor líder de tu ficha.'
        flash(msg, 'info')
        return redirect(url_for('main.login'))

    return render_template('register.html', fichas=fichas)

# ------------------------------------------
# Inicio de Sesión
# ------------------------------------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario:
            flash('No existe un usuario registrado con ese correo.', 'danger')
            return render_template('login.html')
        if not bcrypt.check_password_hash(usuario.password_hash, password):
            flash('Contraseña incorrecta.', 'danger')
            return render_template('login.html')
        # Si es aprendiz, verificar que su ficha esté habilitada
        if usuario.rol == RolesEnum.aprendiz:
            ficha = Ficha.query.get(usuario.id_ficha)
            if not ficha or not ficha.habilitada:
                flash('Tu número de ficha se encuentra suspendido. No puedes acceder al sistema.', 'danger')
                return render_template('login.html')
        if not usuario.validado:
            flash('Tu cuenta aún está pendiente de validación. Contacta al administrador.', 'warning')
            return render_template('login.html')
        login_user(usuario)
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

# ------------------------------------------
# Cerrar Sesión
# ------------------------------------------
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# ------------------------------------------
# Área Administrativa
# ------------------------------------------
@main.route('/admin/validar_salidas')
@login_required
def validar_salidas():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitudes = Solicitud.query.filter_by(estado='aprobada').all()
    return render_template('administrativo/validar_salidas.html', solicitudes=solicitudes)

@main.route('/admin/instructores')
@login_required
def administrar_instructores():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    instructores = Usuario.query.filter(Usuario.rol == RolesEnum.instructor, Usuario.validado == False).all()
    return render_template('administrativo/instructores.html', instructores=instructores)

@main.route('/admin/porteros')
@login_required
def administrar_porteros():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    porteros = Usuario.query.filter(Usuario.rol == RolesEnum.porteria, Usuario.validado == False).all()
    return render_template('administrativo/porteros.html', porteros=porteros)

@main.route('/admin/validar_usuario/<int:id_usuario>/<accion>', methods=['POST'])
@login_required
def validar_usuario(id_usuario, accion):
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    
    usuario = Usuario.query.get_or_404(id_usuario)
    if accion == 'aprobar':
        usuario.validado = True
        flash(f"Usuario {usuario.nombre} aprobado.", "success")
    elif accion == 'rechazar':
        db.session.delete(usuario)
        flash(f"Usuario {usuario.nombre} rechazado.", "info")
    else:
        flash("Acción no válida.", "danger")
        return redirect(url_for('main.dashboard'))
    
    db.session.commit()
    if usuario.rol == RolesEnum.instructor:
        return redirect(url_for('main.administrar_instructores'))
    elif usuario.rol == RolesEnum.porteria:
        return redirect(url_for('main.administrar_porteros'))
    else:
        return redirect(url_for('main.dashboard'))

@main.route('/administrativo')
@login_required
def administrativo_dashboard():
    if current_user.rol.value not in ['administrativo', 'admin']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    return render_template('administrativo/dashboard.html')

# ------------------------------------------
# Área del Instructor
# ------------------------------------------
@main.route('/instructor')
@login_required
def instructor_dashboard():
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    
    solicitudes_pendientes = Solicitud.query.filter_by(estado=EstadoSolicitud.pendiente).all()
    solicitudes_historial = Solicitud.query.filter(
        Solicitud.estado.in_([EstadoSolicitud.aprobada, EstadoSolicitud.rechazada]),
        Solicitud.id_instructor_aprobador == current_user.id_usuario
    ).all()

    return render_template('instructor/dashboard.html', pendientes=solicitudes_pendientes, historial=solicitudes_historial)

@main.route('/instructor/gestionar/<int:id_solicitud>/<accion>', methods=['POST'])
@login_required
def instructor_gestionar_solicitud(id_solicitud, accion):
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    
    solicitud = Solicitud.query.get_or_404(id_solicitud)
    if solicitud.estado != EstadoSolicitud.pendiente:
        flash("La solicitud ya fue gestionada.", "info")
        return redirect(url_for('main.instructor_dashboard'))

    if accion == 'aprobar':
        solicitud.estado = EstadoSolicitud.aprobada
        solicitud.id_instructor_aprobador = current_user.id_usuario
        flash("Solicitud aprobada. Pasa al área administrativa.", "success")
    elif accion == 'rechazar':
        solicitud.estado = EstadoSolicitud.rechazada
        solicitud.id_instructor_aprobador = current_user.id_usuario
        flash("Solicitud rechazada.", "info")
    else:
        flash("Acción no válida.", "danger")
        return redirect(url_for('main.instructor_dashboard'))
    
    db.session.commit()
    return redirect(url_for('main.instructor_dashboard'))

@main.route('/instructor/validar_aprendices')
@login_required
def validar_aprendices():
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    
    # Obtener las fichas donde el instructor es líder
    fichas_lider = Ficha.query.filter_by(id_instructor_lider=current_user.id_usuario).all()
    
    if not fichas_lider:
        flash("No tienes fichas asignadas como instructor líder", "warning")
        return redirect(url_for('main.dashboard'))
    
    # Obtener aprendices pendientes de validación de las fichas del instructor
    aprendices_pendientes = Usuario.query.filter(
        Usuario.rol == RolesEnum.aprendiz,
        Usuario.validado == False,
        Usuario.id_ficha.in_([f.id_ficha for f in fichas_lider])
    ).all()
    
    return render_template('instructor/validar_aprendices.html', 
                         aprendices=aprendices_pendientes,
                         fichas=fichas_lider)

@main.route('/instructor/validar_aprendiz/<int:id_usuario>/<accion>', methods=['POST'])
@login_required
def validar_aprendiz(id_usuario, accion):
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    
    aprendiz = Usuario.query.get_or_404(id_usuario)
    
    # Verificar que el aprendiz pertenezca a una ficha donde el instructor es líder
    ficha = Ficha.query.filter_by(
        id_ficha=aprendiz.id_ficha,
        id_instructor_lider=current_user.id_usuario
    ).first()
    
    if not ficha:
        flash("No tienes permiso para validar a este aprendiz", "danger")
        return redirect(url_for('main.validar_aprendices'))
    
    if accion == 'aprobar':
        aprendiz.validado = True
        flash(f"Aprendiz {aprendiz.nombre} validado correctamente", "success")
    elif accion == 'rechazar':
        db.session.delete(aprendiz)
        flash(f"Aprendiz {aprendiz.nombre} rechazado", "info")
    else:
        flash("Acción no válida", "danger")
        return redirect(url_for('main.validar_aprendices'))
    
    db.session.commit()
    return redirect(url_for('main.validar_aprendices'))

# ------------------------------------------
# Dashboard (Redirección según Rol)
# ------------------------------------------
@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol.value == 'aprendiz':
        solicitudes = Solicitud.query.filter_by(id_aprendiz=current_user.id_usuario).all()
        tipos_salida = TipoSalida.query.all()
        return render_template('aprendiz/dashboard.html', solicitudes=solicitudes, tipos_salida=tipos_salida)
    elif current_user.rol.value == 'instructor':
        return redirect(url_for('main.instructor_dashboard'))
    elif current_user.rol.value in ['administrativo', 'admin']:
        return redirect(url_for('main.administrativo_dashboard'))
    elif current_user.rol.value == 'porteria':
        return redirect(url_for('main.porteria_dashboard'))
    else:
        flash("No tienes un rol válido asignado.", "danger")
        return redirect(url_for('main.logout'))

# ------------------------------------------
# Nueva Solicitud de Salida (POST)
# ------------------------------------------
@main.route('/nueva_solicitud', methods=['POST'])
@login_required
def nueva_solicitud():
    if current_user.rol.value != 'aprendiz':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('main.dashboard'))
    
    nueva_solicitud = Solicitud(
        id_aprendiz=current_user.id_usuario,
        id_tipo_salida=request.form.get('tipo_salida'),
        hora_salida_estimada=request.form.get('hora_salida'),
        hora_reingreso_estimada=request.form.get('hora_reingreso'),
        motivo=request.form.get('motivo'),
        estado=EstadoSolicitud.pendiente
    )
    db.session.add(nueva_solicitud)
    db.session.commit()
    flash('Solicitud creada', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/admin/gestionar_solicitud/<int:id_solicitud>/<accion>', methods=['POST'])
@login_required
def admin_gestionar_solicitud(id_solicitud, accion):
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))

    solicitud = Solicitud.query.get_or_404(id_solicitud)
    if solicitud.estado != EstadoSolicitud.aprobada:
        flash("La solicitud debe estar aprobada por el instructor primero.", "info")
        return redirect(url_for('main.validar_salidas'))

    if accion == 'aprobar':
        solicitud.estado = EstadoSolicitud.completada
        flash("Salida validada y completada.", "success")
    elif accion == 'rechazar':
        solicitud.estado = EstadoSolicitud.rechazada
        flash("Salida rechazada.", "info")
    else:
        flash("Acción no válida.", "danger")
        return redirect(url_for('main.validar_salidas'))

    db.session.commit()
    return redirect(url_for('main.validar_salidas'))

@main.route('/porteria')
@login_required
def porteria_dashboard():
    if current_user.rol.value != 'porteria':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))

    # Mostrar todas las solicitudes aprobadas y pendientes de salida
    solicitudes_salida = Solicitud.query.filter(
        Solicitud.estado == EstadoSolicitud.completada,
        Solicitud.hora_exacta_salida == None
    ).all()

    # Mostrar todas las temporales con salida registrada pero sin reingreso
    solicitudes_reingreso = Solicitud.query.filter(
        Solicitud.estado == EstadoSolicitud.completada,
        Solicitud.hora_exacta_salida != None,
        Solicitud.hora_exacta_reingreso == None,
        Solicitud.tipo_salida.has(nombre='Temporal')
    ).all()

    return render_template('porteria/dashboard.html', solicitudes_salida=solicitudes_salida, solicitudes_reingreso=solicitudes_reingreso)

@main.route('/porteria/registrar_reingreso/<int:id_solicitud>', methods=['POST'])
@login_required
def porteria_registrar_reingreso(id_solicitud):
    if current_user.rol.value != 'porteria':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))

    solicitud = Solicitud.query.get_or_404(id_solicitud)
    hora_reingreso = request.form.get('hora_exacta_reingreso')
    if not hora_reingreso:
        flash("Debes ingresar la hora exacta de reingreso.", "danger")
        return redirect(url_for('main.porteria_dashboard'))

    solicitud.hora_exacta_reingreso = hora_reingreso
    db.session.commit()
    flash("Hora de reingreso registrada correctamente.", "success")
    return redirect(url_for('main.porteria_dashboard'))

@main.route('/porteria/registrar_salida/<int:id_solicitud>', methods=['POST'])
@login_required
def porteria_registrar_salida(id_solicitud):
    if current_user.rol.value != 'porteria':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))

    solicitud = Solicitud.query.get_or_404(id_solicitud)
    hora_salida = request.form.get('hora_exacta_salida')
    if not hora_salida:
        flash("Debes ingresar la hora exacta de salida.", "danger")
        return redirect(url_for('main.porteria_dashboard'))

    solicitud.hora_exacta_salida = hora_salida
    db.session.commit()
    flash("Hora de salida registrada correctamente.", "success")
    return redirect(url_for('main.porteria_dashboard'))

@main.route('/admin/gestionar_instructores_lideres')
@login_required
def gestionar_instructores_lideres():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    
    # Obtener todos los instructores
    instructores = Usuario.query.filter_by(rol=RolesEnum.instructor).all()
    # Obtener todas las fichas
    fichas = Ficha.query.all()
    
    return render_template('administrativo/gestionar_instructores_lideres.html', 
                         instructores=instructores, 
                         fichas=fichas)

@main.route('/admin/asignar_instructor_lider/<int:id_ficha>', methods=['POST'])
@login_required
def asignar_instructor_lider(id_ficha):
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    
    ficha = Ficha.query.get_or_404(id_ficha)
    id_instructor = request.form.get('id_instructor')
    
    if not id_instructor:
        flash("Debe seleccionar un instructor", "danger")
        return redirect(url_for('main.gestionar_instructores_lideres'))
    
    instructor = Usuario.query.get_or_404(id_instructor)
    if instructor.rol != RolesEnum.instructor:
        flash("El usuario seleccionado no es un instructor", "danger")
        return redirect(url_for('main.gestionar_instructores_lideres'))
    
    ficha.id_instructor_lider = instructor.id_usuario
    db.session.commit()
    
    flash(f"Instructor {instructor.nombre} asignado como líder de la ficha {ficha.nombre}", "success")
    return redirect(url_for('main.gestionar_instructores_lideres'))

@main.route('/admin/remover_instructor_lider/<int:id_ficha>', methods=['POST'])
@login_required
def remover_instructor_lider(id_ficha):
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    
    ficha = Ficha.query.get_or_404(id_ficha)
    ficha.id_instructor_lider = None
    db.session.commit()
    
    flash(f"Instructor líder removido de la ficha {ficha.nombre}", "success")
    return redirect(url_for('main.gestionar_instructores_lideres'))

@main.route('/administrativo/crear_usuario', methods=['GET'])
@login_required
def crear_usuario_avanzado_form():
    if current_user.rol.value not in ['administrativo', 'admin']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    return render_template('administrativo/crear_usuario.html')

@main.route('/administrativo/crear_usuario', methods=['POST'])
@login_required
def crear_usuario_avanzado():
    if current_user.rol.value not in ['administrativo', 'admin']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))

    documento = request.form.get('documento', '').strip()
    nombre = request.form.get('nombre', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    rol_str = request.form.get('rol', '').strip()

    if not documento or not nombre or not email or not password or not rol_str:
        flash('Todos los campos son obligatorios', 'danger')
        return redirect(url_for('main.crear_usuario_avanzado_form'))

    if rol_str not in ['instructor', 'porteria']:
        flash('Rol no válido', 'danger')
        return redirect(url_for('main.crear_usuario_avanzado_form'))

    usuario_existente = Usuario.query.filter(
        (Usuario.email == email) | (Usuario.documento == documento)
    ).first()
    if usuario_existente:
        flash('Usuario ya registrado con este email o documento', 'danger')
        return redirect(url_for('main.crear_usuario_avanzado_form'))

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
    return redirect(url_for('main.administrativo_dashboard'))

# ------------------------------------------
# Gestión de Fichas (Administrativo)
# ------------------------------------------
@main.route('/administrativo/fichas/crear', methods=['GET', 'POST'])
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
            return redirect(url_for('main.crear_ficha'))
        if Ficha.query.get(id_ficha):
            flash('Ya existe una ficha con ese ID', 'danger')
            return redirect(url_for('main.crear_ficha'))
        ficha = Ficha(
            id_ficha=int(id_ficha),
            nombre=nombre,
            descripcion=descripcion,
            id_instructor_lider=id_instructor_lider if id_instructor_lider else None
        )
        db.session.add(ficha)
        db.session.commit()
        flash('Ficha creada exitosamente', 'success')
        return redirect(url_for('main.administrar_fichas'))
    return render_template('administrativo/fichas/crear.html', instructores=instructores)

@main.route('/administrativo/fichas/administrar', methods=['GET', 'POST'])
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
        return redirect(url_for('main.administrar_fichas'))
    fichas = Ficha.query.all()
    return render_template('administrativo/fichas/administrar.html', fichas=fichas)
