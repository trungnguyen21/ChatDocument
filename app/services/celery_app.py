from celery import Celery
import logging

from app.config.config import Config

config = Config()
redis_url = config.REDIS_URL

celery_app = Celery(
    __name__,
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.result_backend = redis_url

logger = logging.getLogger(__name__)

import app.services.tasks.process_document_task #noqa