# config.py
import os

# Usar variable de entorno si existe, si no, usar valor local por defecto
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://uwp4mcn7ndpzn1yq:RudBjybBtcjVmUhQn05M@bmzv59food8yw9io46pr-mysql.services.clever-cloud.com:3306/bmzv59food8yw9io46pr"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')

# Configuración de la base de datos (ya no se necesita si usas SQLALCHEMY_DATABASE_URI)
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'quickexit_db')
