import logging

from celery import Celery
from back_end.config.config import Config
from .modules import preprocessing, rag_chat

model = rag_chat.RagChat()

config = Config()
redis_url = config.REDIS_URL

celery = Celery(
    __name__,
    broker=redis_url,
    backend=redis_url
)

class ProcessingTask:
    def __init__(self):
        pass

    @celery.task(name="preprocessing_document")
    def process_document(retrievers: dict, chains: dict, file_path: str, file_id: str):
        preprocessor = preprocessing.DocumentProcessor(file_path)
        try: 
            if retrievers.get(file_id) is None:
                retrievers[file_id] = preprocessor.vector_document.delay(file_path)

            if chains.get(file_id) is None:
                chains[file_id] = model.init_chain_with_history(retrievers[file_id])
        except Exception as e:
            logging.error(f"Error in processing document: {e}")
            raise
