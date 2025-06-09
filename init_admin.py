from app import db, bcrypt
from app.models import Usuario, RolesEnum

# Datos del usuario admin
ADMIN_DOCUMENTO = "0001"
ADMIN_NOMBRE = "Administrador"
ADMIN_EMAIL = "admin@quickexit.com"
ADMIN_PASSWORD = "1234"
ADMIN_ROL = RolesEnum.admin


def crear_admin():
    print("Buscando usuario admin...")
    usuario_existente = Usuario.query.filter_by(email=ADMIN_EMAIL).first()
    if usuario_existente:
        print("Ya existe un usuario con ese correo.")
        return
    hashed_pw = bcrypt.generate_password_hash(ADMIN_PASSWORD).decode('utf-8')
    admin = Usuario(
        documento=ADMIN_DOCUMENTO,
        nombre=ADMIN_NOMBRE,
        email=ADMIN_EMAIL,
        password_hash=hashed_pw,
        rol=ADMIN_ROL,
        validado=True
    )
    db.session.add(admin)
    db.session.commit()
    print("Usuario admin creado correctamente.")

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        crear_admin() 