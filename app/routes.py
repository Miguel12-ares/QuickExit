from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db, bcrypt
from app.models import Usuario, Ficha, TipoSalida, Solicitud, AuditoriaGeneral, EstadoSolicitud, RolesEnum
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date
from sqlalchemy import select, or_

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
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
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
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
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
    # Después de validar un usuario (especialmente porteros), redirigir al nuevo dashboard unificado de gestión de usuarios.
    if usuario.rol == RolesEnum.instructor:
        return redirect(url_for('main.administrar_instructores'))
    elif usuario.rol == RolesEnum.porteria:
        return redirect(url_for('main.gestionar_usuarios_dashboard'))
    else:
        return redirect(url_for('main.dashboard'))

@main.route('/administrativo')
@login_required
def administrativo_dashboard():
    if current_user.rol.value not in ['administrativo', 'admin']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    # Este es el dashboard administrativo principal. Los enlaces a la gestión de usuarios ahora apuntan al nuevo dashboard unificado.
    return render_template('administrativo/dashboard.html')

# Nueva ruta para el dashboard de gestión de usuarios unificado
# Este panel ahora agrupa las funcionalidades de crear usuarios, validar porteros y gestionar usuarios.
@main.route('/administrativo/usuarios/dashboard')
@login_required
def gestionar_usuarios_dashboard():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    return render_template('administrativo/usuarios/dashboard.html') # Renderiza el nuevo dashboard unificado

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
    return render_template('instructor/instructor.html', pendientes=solicitudes_pendientes, historial=solicitudes_historial)

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
    
    # Obtener aprendices pendientes de validación de las fichas del instructor
    aprendices_pendientes = []
    
    # Si no hay fichas, mostrar el mensaje
    if not fichas_lider:
        flash("No tienes fichas asignadas como instructor líder", "warning")
        return render_template('instructor/validar_aprendices.html', 
                            aprendices=aprendices_pendientes,
                            fichas=fichas_lider)
    
    # Si hay fichas, buscar aprendices pendientes
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

@main.route('/instructor/solicitudes_pendientes')
@login_required
def instructor_solicitudes_pendientes():
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitudes_pendientes = Solicitud.query.filter_by(estado=EstadoSolicitud.pendiente).all()
    return render_template('instructor/solicitudes_pendientes.html', pendientes=solicitudes_pendientes)

@main.route('/instructor/historial')
@login_required
def instructor_historial():
    if current_user.rol.value != 'instructor':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitudes_historial = Solicitud.query.filter(
        Solicitud.estado.in_([EstadoSolicitud.aprobada, EstadoSolicitud.rechazada]),
        Solicitud.id_instructor_aprobador == current_user.id_usuario
    ).all()
    return render_template('instructor/historial.html', historial=solicitudes_historial)

# ------------------------------------------
# Dashboard (Redirección según Rol)
# ------------------------------------------
@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol.value == 'aprendiz':
        return redirect(url_for('main.aprendiz_dashboard'))
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
# Área del Aprendiz
# ------------------------------------------
@main.route('/aprendiz/dashboard')
@login_required
def aprendiz_dashboard():
    if current_user.rol.value != 'aprendiz':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('main.dashboard'))
    return render_template('aprendiz/dashboard.html')

@main.route('/aprendiz/nueva_solicitud', methods=['GET', 'POST'])
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
            estado=EstadoSolicitud.pendiente
        )
        db.session.add(nueva_solicitud_obj)
        db.session.commit()
        flash('Solicitud creada exitosamente', 'success')
        return redirect(url_for('main.aprendiz_dashboard'))
    
    return render_template('aprendiz/nueva_solicitud.html', tipos_salida=tipos_salida)

@main.route('/aprendiz/historial')
@login_required
def aprendiz_historial():
    if current_user.rol.value != 'aprendiz':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('main.dashboard'))
    solicitudes = Solicitud.query.filter_by(id_aprendiz=current_user.id_usuario).all()
    return render_template('aprendiz/historial.html', solicitudes=solicitudes)

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
    # Estas variables ya no se usarán directamente aquí, pero se mantienen para referencia
    # solicitudes_salida = Solicitud.query.filter_by(estado=EstadoSolicitud.aprobada_instructor).all()
    # solicitudes_reingreso = Solicitud.query.filter_by(estado=EstadoSolicitud.salida_registrada).all()
    return render_template('porteria/dashboard.html')

@main.route('/porteria/solicitudes_salida')
@login_required
def porteria_solicitudes_salida():
    if current_user.rol.value != 'porteria':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitudes_salida = Solicitud.query.filter_by(estado=EstadoSolicitud.aprobada).all()
    return render_template('porteria/registrar_salida.html', solicitudes_salida=solicitudes_salida)

@main.route('/porteria/solicitudes_reingreso')
@login_required
def porteria_solicitudes_reingreso():
    if current_user.rol.value != 'porteria':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    solicitudes_reingreso = Solicitud.query.filter(
        Solicitud.estado == EstadoSolicitud.completada,
        Solicitud.hora_exacta_reingreso == None,
        Solicitud.tipo_salida.has(nombre='Temporal')
    ).all()
    return render_template('porteria/registrar_reingreso.html', solicitudes_reingreso=solicitudes_reingreso)

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
        return redirect(url_for('main.administrar_fichas'))
    
    instructor = Usuario.query.get_or_404(id_instructor)
    if instructor.rol != RolesEnum.instructor:
        flash("El usuario seleccionado no es un instructor", "danger")
        return redirect(url_for('main.administrar_fichas'))
    
    ficha.id_instructor_lider = instructor.id_usuario
    db.session.commit()
    
    flash(f"Instructor {instructor.nombre} asignado como líder de la ficha {ficha.nombre}", "success")
    return redirect(url_for('main.administrar_fichas'))

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
    return redirect(url_for('main.administrar_fichas'))

@main.route('/administrativo/crear_usuario', methods=['GET'])
@login_required
def crear_usuario_avanzado_form():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    # Esta ruta ahora renderiza la plantilla de creación de usuario desde su nueva ubicación.
    return render_template('administrativo/usuarios/crear_usuario.html')

@main.route('/administrativo/crear_usuario', methods=['POST'])
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
    return redirect(url_for('main.gestionar_usuarios_dashboard'))

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
    # No pasar fichas al render, la tabla se llena por AJAX
    return render_template('administrativo/fichas/administrar.html')

@main.route('/api/buscar_fichas')
@login_required
def api_buscar_fichas():
    if current_user.rol.value not in ['administrativo', 'admin']:
        return jsonify({'error': 'No autorizado'}), 403

    buscar_id = request.args.get('buscar_id', '').strip()
    buscar_nombre = request.args.get('buscar_nombre', '').strip()
    buscar_instructor = request.args.get('buscar_instructor', '').strip()

    query = Ficha.query

    if buscar_id:
        query = query.filter(Ficha.id_ficha.like(f"%{buscar_id}%"))
    if buscar_nombre:
        query = query.filter(Ficha.nombre.ilike(f"%{buscar_nombre}%"))
    if buscar_instructor:
        # Filtrar por nombre del instructor líder asociado a la ficha
        query = query.filter(Ficha.instructor_lider.has(Usuario.nombre.ilike(f"%{buscar_instructor}%")))

    fichas = query.all()

    # Serializar los datos para JSON
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

# Nueva ruta para actualizar el estado de validación de cualquier usuario (Activo/Inactivo)
@main.route('/admin/actualizar_estado_usuario/<int:id_usuario>', methods=['POST'])
@login_required
def actualizar_estado_usuario(id_usuario):
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    
    usuario = Usuario.query.get_or_404(id_usuario)
    validado_str = request.form.get('validado')
    usuario.validado = (validado_str == 'true')
    
    db.session.commit()
    flash(f"Estado de usuario {usuario.nombre} actualizado a {'Activo' if usuario.validado else 'Inactivo'}.", "success")
    # Como esta ruta es llamada desde el JS que recarga la tabla, no es necesario un redirect directo a la misma página.
    # Sin embargo, devolvemos un JSON para indicar éxito.
    return jsonify(message="Estado actualizado con éxito."), 200

@main.route('/api/buscar_instructores')
@login_required
def api_buscar_instructores():
    if current_user.rol.value not in ['admin', 'administrativo']:
        return jsonify({'error': 'No autorizado'}), 403
    buscar_id = request.args.get('buscar_id', '').strip()
    buscar_nombre = request.args.get('buscar_nombre', '').strip()
    buscar_email = request.args.get('buscar_email', '').strip()
    query = Usuario.query.filter_by(rol=RolesEnum.instructor)
    if buscar_id:
        query = query.filter(Usuario.id_usuario.like(f"%{buscar_id}%"))
    if buscar_nombre:
        query = query.filter(Usuario.nombre.ilike(f"%{buscar_nombre}%"))
    if buscar_email:
        query = query.filter(Usuario.email.ilike(f"%{buscar_email}%"))
    instructores = query.all()
    result = []
    for i in instructores:
        ficha_nombre = i.ficha.nombre if i.ficha else None
        result.append({
            'id_usuario': i.id_usuario,
            'nombre': i.nombre,
            'email': i.email,
            'ficha_nombre': ficha_nombre,
            'validado': i.validado
        })
    return jsonify({'instructores': result})

# ------------------------------------------
# Página Mi Cuenta
# ------------------------------------------
@main.route('/cuenta', methods=['GET', 'POST'])
@login_required
def mi_cuenta():
    instructor_lider = None
    if current_user.rol == RolesEnum.aprendiz and current_user.ficha:
        instructor_lider = current_user.ficha.instructor_lider

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        current_password = request.form.get('current_password', '').strip()
        password = request.form.get('password', '').strip()
        cambios = False

        # Verificar la contraseña actual
        if not bcrypt.check_password_hash(current_user.password_hash, current_password):
            flash('La contraseña actual es incorrecta.', 'danger')
            return redirect(url_for('main.mi_cuenta'))

        if email and email != current_user.email:
            if Usuario.query.filter(Usuario.email == email, Usuario.id_usuario != current_user.id_usuario).first():
                flash('El correo electrónico ya está en uso.', 'danger')
            else:
                current_user.email = email
                cambios = True
        if password:
            current_user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            cambios = True
        if cambios:
            db.session.commit()
            flash('Datos actualizados correctamente.', 'success')
        else:
            flash('No se realizaron cambios.', 'info')
        return redirect(url_for('main.mi_cuenta'))
    return render_template('cuenta/mi_cuenta.html', usuario=current_user, instructor_lider=instructor_lider)

@main.route('/administrativo/gestionar_usuarios')
@login_required
def gestionar_usuarios():
    if current_user.rol.value not in ['admin', 'administrativo']:
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('main.dashboard'))
    return render_template('administrativo/usuarios/gestionar_usuarios.html')

@main.route('/api/buscar_usuarios')
@login_required
def api_buscar_usuarios():
    if current_user.rol.value not in ['admin', 'administrativo']:
        return jsonify({'error': 'No autorizado'}), 403

    buscar_documento = request.args.get('buscar_documento', '').strip()
    buscar_nombre = request.args.get('buscar_nombre', '').strip()
    buscar_email = request.args.get('buscar_email', '').strip()
    buscar_ficha = request.args.get('buscar_ficha', '').strip()
    buscar_rol = request.args.get('buscar_rol', '').strip()

    print(f"[DEBUG] buscar_ficha: {buscar_ficha}")
    print(f"[DEBUG] buscar_rol: {buscar_rol}")

    # Iniciar la consulta uniendo Usuario y Ficha para poder filtrar y obtener info de ficha
    # El JOIN considera tanto aprendices (por id_ficha) como instructores líderes (por id_instructor_lider).
    query = db.session.query(Usuario, Ficha).outerjoin(Ficha, or_(
        Usuario.id_ficha == Ficha.id_ficha,             # Condición para aprendices
        Usuario.id_usuario == Ficha.id_instructor_lider # Condición para instructores líderes
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
        ficha_id_valido = None
        try:
            ficha_id_valido = int(buscar_ficha)
            print(f"[DEBUG] ficha_id_valido (int): {ficha_id_valido}")
            # Aplicar filtro por ID de ficha directamente sobre la tabla Ficha unida
            query = query.filter(Ficha.id_ficha == ficha_id_valido)
        except ValueError:
            print(f"[DEBUG] ValueError: '{buscar_ficha}' no es un número válido. Filtrando por ID inexistente.")
            # Si no es un número válido, asegurar que la búsqueda por ficha no retorne resultados
            query = query.filter(Ficha.id_ficha == -1)

    print(f"[DEBUG] SQL Query antes de ejecutar: {query.statement}")

    # Ejecutar la consulta y obtener las tuplas (Usuario, Ficha)
    results = query.all()

    print(f"[DEBUG] Número de resultados obtenidos: {len(results)}")
    for usr, ficha in results:
        print(f"[DEBUG] Usuario ID: {usr.id_usuario}, Rol: {usr.rol.value}, Ficha ID (JOIN): {ficha.id_ficha if ficha else 'None'}")

    usuarios_json = []
    # Usar un conjunto para evitar usuarios duplicados si la unión resulta en múltiples fichas
    # para un instructor (aunque en el modelo actual, un instructor debería ser líder de una principal).
    processed_user_ids = set()
    
    for usr, ficha in results:
        if usr.id_usuario not in processed_user_ids:
            ficha_info = None
            # La información de la ficha se obtiene directamente del objeto ficha unido
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

    print(f"[DEBUG] Número de usuarios serializados para JSON: {len(usuarios_json)}")
    return jsonify({'usuarios': usuarios_json})

@main.route('/admin/eliminar_usuario/<int:id_usuario>', methods=['POST'])
@login_required
def eliminar_usuario(id_usuario):
    print(f"[TEMP DEBUG] === INICIO ELIMINACIÓN USUARIO {id_usuario} ===")
    
    if current_user.rol.value not in ['admin', 'administrativo']:
        print(f"[TEMP DEBUG] Acceso denegado para rol: {current_user.rol.value}")
        flash("Acceso no autorizado", "danger")
        return jsonify({'success': False, 'message': 'Acceso no autorizado'}), 403
    
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        print(f"[TEMP DEBUG] Usuario {id_usuario} no encontrado")
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    print(f"[TEMP DEBUG] Usuario encontrado: {usuario.nombre} - Rol: {usuario.rol.value} - Validado: {usuario.validado}")

    # No permitir eliminar administradores
    if usuario.rol == RolesEnum.admin:
        print(f"[TEMP DEBUG] Bloqueado: es administrador")
        flash("No se puede eliminar un usuario con rol de administrador.", "danger")
        return jsonify({'success': False, 'message': 'No se puede eliminar un usuario con rol de administrador.'}), 400

    try:
        # Verificar dependencias críticas
        solicitudes_aprendiz = Solicitud.query.filter_by(id_aprendiz=id_usuario).count()
        solicitudes_instructor = Solicitud.query.filter_by(id_instructor_aprobador=id_usuario).count()
        fichas_lider = Ficha.query.filter_by(id_instructor_lider=id_usuario).count()

        print(f"[TEMP DEBUG] Dependencias - Solicitudes aprendiz: {solicitudes_aprendiz}, Solicitudes instructor: {solicitudes_instructor}, Fichas líder: {fichas_lider}")

        # Si tiene solicitudes, no permitir eliminar (mantiene integridad de datos históricos)
        if solicitudes_aprendiz > 0 or solicitudes_instructor > 0:
            mensaje = f"No se puede eliminar a {usuario.nombre} porque tiene solicitudes asociadas como "
            if solicitudes_aprendiz > 0 and solicitudes_instructor > 0:
                mensaje += f"aprendiz ({solicitudes_aprendiz}) e instructor ({solicitudes_instructor}). "
            elif solicitudes_aprendiz > 0:
                mensaje += f"aprendiz ({solicitudes_aprendiz}). "
            else:
                mensaje += f"instructor ({solicitudes_instructor}). "
            
            # Sugerir alternativa para usuarios inactivos
            if not usuario.validado:
                mensaje += "Como el usuario está inactivo, considere mantenerlo deshabilitado en lugar de eliminarlo."
            else:
                mensaje += "Considere desactivar el usuario en lugar de eliminarlo para preservar el historial."
            
            print(f"[TEMP DEBUG] Bloqueado por dependencias: {mensaje}")
            return jsonify({'success': False, 'message': mensaje}), 400

        # Limpiar relaciones seguras antes de eliminar
        if fichas_lider > 0:
            print(f"[TEMP DEBUG] Limpiando {fichas_lider} fichas como instructor líder")
            # Remover como instructor líder de fichas
            Ficha.query.filter_by(id_instructor_lider=id_usuario).update({'id_instructor_lider': None})
        
        # Eliminar el usuario
        nombre_usuario = usuario.nombre
        print(f"[TEMP DEBUG] Procediendo a eliminar usuario: {nombre_usuario}")
        db.session.delete(usuario)
        db.session.commit()
        
        print(f"[TEMP DEBUG] ✅ Usuario {nombre_usuario} eliminado exitosamente")
        flash(f"Usuario {nombre_usuario} eliminado exitosamente.", "success")
        return jsonify({'success': True, 'message': f'Usuario {nombre_usuario} eliminado exitosamente.'})
        
    except Exception as e:
        print(f"[TEMP DEBUG] ❌ Excepción: {str(e)}")
        db.session.rollback()
        error_msg = f"Error al eliminar el usuario: {str(e)}"
        flash(error_msg, "danger")
        return jsonify({'success': False, 'message': error_msg}), 500