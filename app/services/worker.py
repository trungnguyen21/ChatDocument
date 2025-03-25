from app.services.tasks.process_document_task import process_document
from app.services.celery_app import celery_app, logger

def register_task():
    try:
        logger.info("Registering tasks")
        celery_app.tasks.register(process_document)
        logger.info("Tasks registered")
    except Exception as e:
        logger.error(f"Error in registering tasks: {e}")
        raise

register_task()