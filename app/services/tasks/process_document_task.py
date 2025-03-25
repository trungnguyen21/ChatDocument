import logging
from celery.result import AsyncResult

from app.services.celery_app import celery_app, redis_url
from app.modules import preprocessing, rag_chat

model = rag_chat.RagChat()
logger = logging.getLogger(__name__)

@celery_app.task(name="preprocessing_document")
def process_document(retrievers: dict, chains: dict, file_path: str, file_id: str):
    preprocessor = preprocessing.DocumentProcessor(file_path)
    try: 
        if retrievers.get(file_id) is None:
            retrievers[file_id] = preprocessor.vector_document()

        if chains.get(file_id) is None:
            chains[file_id] = model.init_chain_with_history(retrievers[file_id])
    except Exception as e:
        logger.error(f"Error in processing document: {e}")
        raise

def fetch_task_result(task_id: str):
    task_result = AsyncResult(id=task_id,
                              app=celery_app)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
    }
    return result

logger.info("Task service initialized")

if __name__ == "__main__":
    logger.info("Starting celery worker")
    celery_app.start()