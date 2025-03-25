from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from pydantic import BaseModel

from app.services.tasks.process_document_task import process_document, fetch_task_result
from app.modules import rag_chat, utils, cache
from app.config import config

import aiofiles, uuid
import logging
import os
import redis

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI()

# Initialize modules
model = rag_chat.RagChat()
helpers = utils.Utils()
mem = cache.Cache()
keys = config.Config()

# Initialize redis client
redis_client = redis.from_url(keys.REDIS_URL)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

class RequestBody(BaseModel):
    question: str
    file_id: str

class SectionIDBody(BaseModel):
    file_id: str

@app.get("/api")
async def root():
    return {"message": "Hello World"}

@app.get("/api/db-health")
async def db_health():
    try:
        redis_client.ping()
    except Exception as e:
        logger.error(f"Error in pinging redis @ {keys.REDIS_URL}: {e}")
        raise HTTPException(status_code=500, detail="Database is not correctly configured.")
    return {"message": f"Database is healthy"}


@app.get("/api/files")
def files(file_id: str):
    """
    Get the list of files
    """
    # TODO: implement with external db
    return {"message": mem.get_file_by_id(file_id)}

@app.post("/api/upload/")
async def upload(file: UploadFile) -> JSONResponse:
    """
    File upload
    Args:
        file: file to upload
    Returns:
        file_id: the id of the file
    """
    # Generate a unique ID for the file
    file_id = str(uuid.uuid4())
    file_name = file.filename
    file_path = os.path.join(mem.get_data_path(), file_id + "_" + file_name)

    # Save the file to disk with the unique ID as part of the filename
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    
    try: 
        # Store the mapping from unique_id to file path
        mem.save_file(file_id, file_path)
        return JSONResponse(content={"file_id": file_id})
    except Exception as e:
        logger.error(f"Error in saving uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Error in saving uploaded file.")

@app.post("/api/model_activation")
async def model_activation(session_body: SectionIDBody):
    """
    Initialize the model
    Args:
        file_id: the id of the file
    Returns:
        task_id: the id of the task
    """

    # Retrieve the file path using the provided file_id
    file_id = session_body.file_id
    logger.info(f"File id: {file_id}")
    file_path = mem.get_file_by_id(file_id)
    logger.info("Looking at file path: " + str(file_path))

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or invalid file_id" + file_path)

    logger.info("Initializing retriever and rag_chain...")
    try:
        task = process_document.delay(
            retrievers=mem.get_retrievers(),
            chains=mem.get_rag_chains(),
            file_path=file_path,
            file_id=file_id
        )
        return JSONResponse(content={"task_id": task.id})
    except Exception as e:
        logger.error(f"Error in initializing model: {e}")
        raise HTTPException(status_code=500, detail="Error in initializing model.")

@app.get("/api/preprocessing_status")
def get_processing_status(task_id: str):
    """
    Get the status of the model
    """
    try:
        result = fetch_task_result(task_id)
    except Exception as e:
        logger.error(f"Error in getting processing status: {e}")
        raise HTTPException(status_code=404, detail="Cannot find the specified task.")
    return JSONResponse(content=result)


@app.post("/api/chat_completion/")
async def chat_completion(file_id: str, question: str):
    """
    Get response from model, use LLM if the model is not initialized
    """
    file_id = file_id
    retriever, rag_chain = mem.get_cached_file(file_id)
    # If retriever and rag_chain are not initialized, initialize them
    if retriever is None or rag_chain is None:
        # Normal LLM call without context
        async def generate():
            async for token in model.chat_completion(question):
                yield token.content + " "
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        async def generate():
            async for token in model.output_generation(question, file_id, rag_chain):
                yield str(token) + " "
        return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/chat/")
async def chat(question: str):
    async def generate():
        async for token in model.chat_completion(question):
            yield token.content + " "

    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/api/chat_history")
async def chat_history(session_id: str):
    """
    Get chat history, uses file_id as session_id
    """
    chat_history = helpers.get_session_history(session_id).messages
    return {"message": chat_history}

@app.delete("/api/delete")
async def delete(file_id: str):
    """
    Delete a file
    """
    try:
        mem.delete_file(file_id)
        redis_client.delete(f"doc:{file_id}:*")
        redis_client.delete(f"message_store:{file_id}:*")
        return {"message": "File deleted successfully."}
    except Exception as e:
        logger.error(f"Error in deleting file: {e}")
        raise HTTPException(status_code=500, detail="Error in deleting file.")

@app.delete("/api/flush")
async def flush():
    """
    Flush all data
    """
    try:
        redis_client.flushall()
        mem.clear_cache()
    except Exception as e:
        logger.error(f"Error in flushing data: {e}")
        raise HTTPException(status_code=500, detail="Error in flushing data.")

    return {"message": "Data flushed successfully."}
