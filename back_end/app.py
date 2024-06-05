from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict

import aiofiles, uuid, json
import os
import model_chain, redis, config

app = FastAPI()

# Create ./data/files and ./data/vectorstore directories if they don't exist
if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists("data/files"):
    os.mkdir("data/files")

data_path = "data/files"
file_map_path = "data/file_map.json"

#delete all keys in redis
redis_client = redis.from_url(config.REDIS_URL)

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

@app.get("/")
async def root():
    return {"message": "Starting"}


@app.get("/get_files")
def get_files():
    """
    Get the list of files
    """
    files = redis_client.keys("doc:*")
    print(files)
    return {"message": files}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    """
    File upload
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

    return {"Result": "OK", "file_id": file_id}


@app.post("/initialize_model/")
async def initialize_model(session_body: SectionIDBody):
    """
    Initialize the model
    """

    # Retrieve the file path using the provided file_id
    file_id = session_body.session_id
    print(file_id)
    file_path = file_map.get(file_id)
    print("Looking at file path: " + str(file_path))

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or invalid file_id" + file_path)

    print("Initializing retriever and rag_chain...")
    try:
        if retrievers.get(file_id) is None:
            retrievers[file_id] = model_chain.vectorDocuments(file_path)
            print("Retriver not found. Retriever initialized successfully.")

        if rag_chains.get(file_id) is None:
            rag_chains[file_id] = model_chain.init_chain_with_history(retrievers[file_id])
            print("Rag_chain not found. Rag_chain initialized successfully.")

    except Exception as e:
        print(f"Error in initializing model: {e}")
        raise
    return {"message": "Retriever and rag_chain initialized successfully."}


@app.post("/get_response/")
async def get_response(body: RequestBody):
    """
    Get response
    """
    print(retrievers)
    file_id = body.session_id
    retriever = retrievers.get(file_id)
    rag_chain = rag_chains.get(file_id)
    # If retriever and rag_chain are not initialized, initialize them
    if retriever is None or rag_chain is None:
        raise HTTPException(status_code=500, detail="Retriever and rag_chain are not initialized. Call /initialize_model first.")

    # Use the file path to answer the question
    response = model_chain.answeringQuestion(body.question, file_id, rag_chain)
    return {"message": response}

@app.get("/get_chat_history/")
async def get_chat_history(session_id: str):
    """
    Get chat history
    """
    chat_history = model_chain.get_session_history(session_id).messages
    return {"message": chat_history}

@app.delete("/flush_all/")
async def flush_all():
    """
    Flush all data
    """
    retrievers.clear()
    rag_chains.clear()
    
    #delete all files in data/files
    file_names = os.listdir(data_path)
    for file in file_names:
        os.remove(os.path.join(data_path, file))

    save_file_map({})


    try:
        redis_client.flushall()
    except Exception as e:
        print(f"Error in flushing data: {e}")
        raise
    return {"message": "Data flushed successfully."}