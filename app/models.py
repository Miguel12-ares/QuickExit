from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import enum
from app import db, login_manager, bcrypt

class RolesEnum(enum.Enum):
    aprendiz = 'aprendiz'
    instructor = 'instructor'
    administrativo = 'administrativo'
    porteria = 'porteria'
    admin = 'admin'

class EstadoSolicitud(enum.Enum):
    pendiente = 'pendiente'
    aprobada = 'aprobada'  # Aprobada por instructor
    autorizada = 'autorizada'  # Validada por administrativo, lista para portería
    rechazada = 'rechazada'
    completada = 'completada'

class Ficha(db.Model):
    __tablename__ = 'FICHAS'
    id_ficha = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    id_instructor_lider = db.Column(db.Integer, db.ForeignKey('USUARIOS.id_usuario'), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    habilitada = db.Column(db.Boolean, default=True, nullable=False)
    
    usuarios = db.relationship('Usuario', 
                             backref='ficha', 
                             lazy=True,
                             foreign_keys='Usuario.id_ficha')
    
    instructor_lider = db.relationship('Usuario',
                                     foreign_keys=[id_instructor_lider],
                                     backref='fichas_lideradas')

class TipoSalida(db.Model):
    __tablename__ = 'TIPOS_SALIDA'
    id_tipo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    requiere_reingreso = db.Column(db.Boolean, default=False, nullable=False)
    solicitudes = db.relationship('Solicitud', backref='tipo_salida', lazy=True)

    @classmethod
    def crear_tipos_por_defecto(cls):
        tipos = [
            {'nombre': 'Temporal', 'requiere_reingreso': True},
            {'nombre': 'Definitiva', 'requiere_reingreso': False}
        ]
        for tipo in tipos:
            if not cls.query.filter_by(nombre=tipo['nombre']).first():
                nuevo_tipo = cls(nombre=tipo['nombre'], requiere_reingreso=tipo['requiere_reingreso'])
                db.session.add(nuevo_tipo)
        db.session.commit()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'USUARIOS'
    id_usuario = db.Column(db.Integer, primary_key=True)
    documento = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum(RolesEnum), nullable=False)
    id_ficha = db.Column(db.Integer, db.ForeignKey('FICHAS.id_ficha'), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    validado = db.Column(db.Boolean, default=True, nullable=False)

    # Especificar explícitamente la relación con Solicitud
    solicitudes_creadas = db.relationship(
        'Solicitud',
        backref='aprendiz',
        lazy=True,
        foreign_keys='Solicitud.id_aprendiz',
        passive_deletes=True
    )

    def get_id(self):
        return str(self.id_usuario)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Solicitud(db.Model):
    __tablename__ = 'SOLICITUDES'
    id_solicitud = db.Column(db.Integer, primary_key=True)
    id_aprendiz = db.Column(db.Integer, db.ForeignKey('USUARIOS.id_usuario'), nullable=False)
    id_tipo_salida = db.Column(db.Integer, db.ForeignKey('TIPOS_SALIDA.id_tipo'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    hora_salida_estimada = db.Column(db.Time, nullable=False)
    hora_reingreso_estimada = db.Column(db.Time, nullable=True)
    motivo = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.Enum(EstadoSolicitud), default=EstadoSolicitud.pendiente, nullable=False)
    id_validacion = db.Column(db.Integer, db.ForeignKey('solicitud_validaciones.id_validacion'))
    hora_exacta_salida = db.Column(db.Time, nullable=True)
    hora_exacta_reingreso = db.Column(db.Time, nullable=True)

    auditorias = db.relationship('AuditoriaGeneral', backref='solicitud', lazy=True)

    validacion = db.relationship(
        'SolicitudValidaciones',
        back_populates='solicitud',
        uselist=False,
        foreign_keys=[id_validacion]
    )

class SolicitudValidaciones(db.Model):
    __tablename__ = 'solicitud_validaciones'
    id_validacion = db.Column(db.Integer, primary_key=True)
    id_solicitud = db.Column(db.Integer, db.ForeignKey('SOLICITUDES.id_solicitud'), nullable=False)
    id_instructor_validador = db.Column(db.Integer, db.ForeignKey('USUARIOS.id_usuario'), nullable=True)
    id_administrativo_validador = db.Column(db.Integer, db.ForeignKey('USUARIOS.id_usuario'), nullable=True)
    id_portero_validador_salida = db.Column(db.Integer, db.ForeignKey('USUARIOS.id_usuario'), nullable=True)
    id_portero_validador_reingreso = db.Column(db.Integer, db.ForeignKey('USUARIOS.id_usuario'), nullable=True)
    fecha_validacion_instructor = db.Column(db.DateTime, nullable=True)
    fecha_validacion_admin = db.Column(db.DateTime, nullable=True)
    fecha_validacion_portero_salida = db.Column(db.DateTime, nullable=True)
    fecha_validacion_portero_reingreso = db.Column(db.DateTime, nullable=True)

    solicitud = db.relationship(
        'Solicitud',
        back_populates='validacion',
        uselist=False,
        foreign_keys='Solicitud.id_validacion'
    )

class AuditoriaGeneral(db.Model):
    __tablename__ = 'AUDITORIA_GENERAL'
    id_log = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('USUARIOS.id_usuario'), nullable=False)
    id_solicitud = db.Column(db.Integer, db.ForeignKey('SOLICITUDES.id_solicitud'), nullable=False)
    accion = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    detalles = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)

class Configuracion(db.Model):
    __tablename__ = 'CONFIGURACION'
    id_config = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)