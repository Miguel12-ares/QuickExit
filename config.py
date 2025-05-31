# config.py
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/quickexit_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True  # Esto mostrará las consultas SQL en la consola
SECRET_KEY = 'mysecretkey'

# Configuración de la base de datos
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'quickexit_db'
