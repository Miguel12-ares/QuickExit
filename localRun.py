from app import create_app
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    logger.info('Iniciando la aplicación...')
    try:
        app.run(debug=True)
    except Exception as e:
        logger.error(f'Error al iniciar la aplicación: {str(e)}')
        raise
