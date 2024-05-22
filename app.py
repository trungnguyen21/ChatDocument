from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Dict

import aiofiles, uuid, json
import os
import model_chain

app = FastAPI()

# Create ./data/files and ./data/vectorstore directories if they don't exist
if not os.path.exists("data"):
    os.mkdir("data")
if not os.path.exists("data/files"):
    os.mkdir("data/files")
if not os.path.exists("data/vectorstore"):
    os.mkdir("data/vectorstore")

data_path = "data/files"
file_names = os.listdir(data_path)

file_map_path = "data/file_map.json"

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

@app.get("/")
async def root():
    return {"message": "Starting"}


@app.get("/get_files")
def get_files():
    print(file_names)
    return {"message": f"Found {len(file_names)} file(s) in the server"}   

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    """
    File upload
    """
    # Generate a unique ID for the file
    unique_id = str(uuid.uuid4())
    file_path = os.path.join(data_path, unique_id + "_" + file.filename)

    # Save the file to disk with the unique ID as part of the filename
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Store the mapping from unique_id to file path
    file_map[unique_id] = file_path
    save_file_map(file_map)

    return {"Result": "OK", "file_id": unique_id}


retriever = None
rag_chain = None
@app.post("/initialize_model")
async def initialize_model(file_id: str):
    """
    Initialize the model
    """
    global retriever, rag_chain

    # Retrieve the file path using the provided file_id
    print(file_id)
    file_path = file_map.get(file_id)
    print(file_map)
    print("Looking at file path: " + str(file_path))
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or invalid file_id")

    print("Initializing retriever and rag_chain...")
    retriever = model_chain.vectorDocuments(file_path)
    rag_chain = model_chain.init_chain_with_history(retriever)
    return {"message": "Retriever and rag_chain initialized successfully."}


@app.post("/get_response/{file_id}")
async def get_response(file_id: str, body: RequestBody):
    """
    Get response
    """
    global retriever, rag_chain

    # If retriever and rag_chain are not initialized, initialize them
    if retriever is None or rag_chain is None:
        raise HTTPException(status_code=500, detail="Retriever and rag_chain are not initialized. Call /initialize_model first.")

    # Retrieve the file path using the provided file_id
    print(file_id)
    file_path = file_map.get(file_id)
    print(file_map)
    print("Looking at file path: " + str(file_path))
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or invalid file_id")

    print("Handling file at ", file_path)
    # Use the file path to answer the question
    response = model_chain.answeringQuestion(body.question, file_id, rag_chain)
    return {"message": response}
