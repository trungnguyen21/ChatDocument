from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from celery.result import AsyncResult

from pydantic import BaseModel
from typing import Dict

from app import worker
from app.modules import rag_chat, utils

import aiofiles, uuid, json
import logging
import os
import redis
# import modules.rag_chat as model

REDIS_URL = os.environ.get("REDIS_URL")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()

model = rag_chat.RagChat()
helpers = utils.Utils()
task_service = worker.TaskService()

# Create ./data/files and ./data/vectorstore directories if they don't exist
if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists("data/files"):
    os.mkdir("data/files")

data_path = "data/files"
file_map_path = "data/file_map.json"

#delete all keys in redis

redis_client = redis.from_url(REDIS_URL)

retrievers = {}
rag_chains = {}

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Function to load the file map from the JSON file
def load_file_map() -> Dict[str, str]:
    if os.path.exists(file_map_path):
        with open(file_map_path, "r") as f:
            return json.load(f)
    return {} 

# Function to save the file map to the JSON file
def save_file_map(file_map: Dict[str, str]):
    with open(file_map_path, "w") as f:
        json.dump(file_map, f)

file_map: Dict[str, str] = load_file_map()

class RequestBody(BaseModel):
    question: str
    session_id: str

class SectionIDBody(BaseModel):
    session_id: str

@app.get("/api")
async def root():
    return {"message": "Hello World"}

@app.get("/api/db-health")
async def db_health():
    try:
        redis_client.ping()
    except Exception as e:
        print(f"Error in pinging redis @ {REDIS_URL}: {e}")
        raise HTTPException(status_code=500, detail="Database is not correctly configured.")
    return {"message": f"Database is healthy"}


@app.get("/api/files")
def files(file_id: str):
    """
    Get the list of files
    """
    # TODO: implement with external db
    return {"message": file_map.get(file_id)}

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
    file_path = os.path.join(data_path, file_id + "_" + file_name)

    # Save the file to disk with the unique ID as part of the filename
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Store the mapping from unique_id to file path
    file_map[file_id] = file_path
    save_file_map(file_map)

    return JSONResponse(content={"file_id": file_id})

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
    file_id = session_body.session_id
    print(f"File id: {file_id}")
    file_path = file_map.get(file_id)
    print("Looking at file path: " + str(file_path))

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or invalid file_id" + file_path)

    print("Initializing retriever and rag_chain...")
    try:
        task = task_service.process_document.delay(
            retrievers=retrievers,
            chains=rag_chains,
            file_path=file_path,
            file_id=file_id
        )
        return JSONResponse(content={"task_id": task.id})
    except Exception as e:
        print(f"Error in initializing model: {e}")
        raise HTTPException(status_code=500, detail="Error in initializing model.")

@app.get("/api/preprocessing_status")
def get_processing_status(task_id: str):
    """
    Get the status of the model
    """
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
    }
    return JSONResponse(content=result)


@app.post("/api/chat_completion/")
async def chat_completion(session_id: str, question: str):
    """
    Get response from model, use LLM if the model is not initialized
    """
    file_id = session_id
    retriever = retrievers.get(file_id)
    rag_chain = rag_chains.get(file_id)
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
    Get chat history
    """
    chat_history = helpers.get_session_history(session_id).messages
    return {"message": chat_history}

@app.delete("/api/delete")
async def delete(file_id: str):
    """
    Delete a file
    """
    file_path = file_map.get(file_id)
    if file_path:
        try:
            os.remove(file_path)
            del file_map[file_id]
            save_file_map(file_map)
        except Exception as e:
            print(f"Error in deleting file: {e}")
            raise HTTPException(status_code=500, detail="Error in deleting file.")

    retrievers.pop(file_id)
    rag_chains.pop(file_id)
    redis_client.delete(f"doc:{file_id}:*")
    redis_client.delete(f"message_store:{file_id}:*")
    return {"message": "File deleted successfully."}

@app.delete("/api/flush")
async def flush():
    """
    Flush all data
    """
    try:
        redis_client.flushall()
    except Exception as e:
        print(f"Error in flushing data: {e}")
        raise HTTPException(status_code=500, detail="Error in flushing data.")
    
    retrievers.clear()
    rag_chains.clear()
    
    #delete all files in data/files
    file_names = os.listdir(data_path)
    for file in file_names:
        os.remove(os.path.join(data_path, file))
        file_map.clear()
        save_file_map(file_map)

    return {"message": "Data flushed successfully."}
