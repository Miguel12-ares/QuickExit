from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import Usuario, Ficha, RolesEnum

main_bp = Blueprint('main', __name__)

# ------------------------------------------
# Página de inicio
# ------------------------------------------
@main_bp.route('/')
def home():
    return render_template('home.html')

# ------------------------------------------
# Registro de Usuarios
# ------------------------------------------
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    fichas = Ficha.query.filter_by(habilitada=True).all()  # Solo fichas habilitadas

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
            ficha = Ficha.query.filter_by(id_ficha=id_ficha, habilitada=True).first()
            if not ficha:
                flash('Ficha seleccionada no válida o deshabilitada.', 'danger')
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
@main_bp.route('/login', methods=['GET', 'POST'])
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
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# ------------------------------------------
# Dashboard (Redirección según Rol)
# ------------------------------------------
@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol.value == 'aprendiz':
        return redirect(url_for('aprendiz.aprendiz_dashboard'))
    elif current_user.rol.value == 'instructor':
        return redirect(url_for('instructor.instructor_dashboard'))
    elif current_user.rol.value in ['administrativo', 'admin']:
        return redirect(url_for('admin.administrativo_dashboard'))
    elif current_user.rol.value == 'porteria':
        return redirect(url_for('porteria.porteria_dashboard'))
    else:
        flash("No tienes un rol válido asignado.", "danger")
        return redirect(url_for('main.logout'))

# ------------------------------------------
# Página Mi Cuenta
# ------------------------------------------
@main_bp.route('/cuenta', methods=['GET', 'POST'])
@login_required
def mi_cuenta():
    from app.models import Usuario, RolesEnum  # Importación local para evitar ciclos
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