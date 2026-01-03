import os
import redis
import logging

from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from langchain_community.vectorstores.redis import Redis
from langchain_experimental.text_splitter import SemanticChunker

from app.config.config import Config

class DocumentProcessor:
    def __init__(self, file_path: str):
        config = Config()
        self.redis_url = config.REDIS_URL
        self.redis_client = redis.from_url(self.redis_url)
        self.file_path = file_path
        self.embeddings = config.EMBED_MODEL
        self.file_name = os.path.basename(self.file_path) # Format: file_<uuid>.pdf
        self.file_id = self.file_name.split("_")[0]
    
    def vector_document(self):
        """
        Create and return a retriever for the document.
        """
        try:
            redis_vector = self.load_document()
            retriever = redis_vector.as_retriever(search_kwargs={"k": 3})
            logging.info("Step 2. Successfully created a retriever")

            return retriever
        except Exception as e:
            logging.error(f"Error in vector_document: {e}")
            raise

    def ingest_document(self, docs: list) -> Redis:
        """
        Ingest document into the vectordb.
        Args:
            docs (list): List of documents
            file_name (str): Name of the file (the uuid of the file)
        Returns:
            Redis: Redis object
        """
        try:
            for i in range(0, len(docs), 100):
                if i + 100 > len(docs):
                    chunks = docs[i:]
                else:
                    chunks = docs[i:i+100]

                vector = Redis.from_documents(
                    chunks, 
                    self.embeddings,
                    redis_url=self.redis_url,
                    index_name=self.file_name,
                )
            vector.write_schema("data/schema.yaml")
            return vector
        except Exception as e:
            logging.error(f"Error in ingest_document: {e}")
            raise

    def create_vector_store(self):
        """
        Create vector store from the document.
        """
        try:
            loader = PyMuPDF4LLMLoader(self.file_path)
            docs = loader.load()
            logging.info("Step 1. Successfully loaded the document.")

            text_splitter = SemanticChunker(self.embeddings)
            documents = text_splitter.split_documents(docs)
            logging.info("Step 1.1. Splitted the document into chunks")

            redis_vector = self.ingest_document(documents)
            logging.info("Step 1.2. Ingested document into vector store")

            return redis_vector
        except Exception as e:
            logging.error(f"Error in create_vector_store: {e}")
            raise
    
    def load_vector_store(self):
        """
        Load vector store from Redis.
        """
        try:
            return Redis.from_existing_index(
                embedding=self.embeddings,
                index_name=self.file_id,
                redis_url=self.redis_url,
                schema="data/schema.yaml",
                key_prefix="doc"
            )
        except Exception as e:
            logging.error(f"Error in load_vector_store: {e}")
            raise

    def load_document(self):
        """
        Checks if a Redis vector store for the document exists; creates one if not.
        Returns:
            Redis: The Redis vector store object for the document.
        """
        try:
            logging.info("Loading file name:" + self.file_id)

            # check if the vectorstore already exist
            if len(self.redis_client.keys(f"doc:{self.file_id}:*")) > 0:
                logging.info("Vectorstore already exist. Skipping step 1")
                redis_vector = self.load_vector_store()
            else:
                redis_vector = self.create_vector_store()

            return redis_vector
        except Exception as e:
            logging.error(f"Error in load_document: {e}")
            raise
