import os
from dotenv import load_dotenv
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

APP_ENV = os.getenv("APP_ENV", "LOCAL")

if APP_ENV == "LOCAL":
    print("Local dev mode detected")
    load_dotenv("./env.local")

class Config:
    def __init__(self):
        # Keys and Endpoints
        self.GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
        self.REDIS_URL = os.environ["REDIS_URL"]
        
        # Models
        self.LLM_MODEL = ChatGoogleGenerativeAI(
            model=os.environ["LLM_MODEL"], 
            streaming=True, 
            callbacks=[FinalStreamingStdOutCallbackHandler(answer_prefix_tokens=["answer", ":"])]
        )
        self.EMBED_MODEL = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        # Paths
        # Create ./data/files and ./data/vectorstore directories if they don't exist
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(base_dir, "data")
        files_dir = os.path.join(data_dir, "files")
        vectorstore_dir = os.path.join(data_dir, "vectorstore")

        os.makedirs(files_dir, exist_ok=True)
        os.makedirs(vectorstore_dir, exist_ok=True)

        self.DATADIR = data_dir
        self.VECTORSTORE = vectorstore_dir + os.sep
        self.DATAFILES = files_dir + os.sep