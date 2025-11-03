import os
from dotenv import load_dotenv
from langchain.callbacks.streaming_stdout_final_only import FinalStreamingStdOutCallbackHandler
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


load_dotenv()

class Config:
    def __init__(self):
        # Keys and Endpoints
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.REDIS_URL = os.getenv("REDIS_URL")
        
        # Models
        self.LLM_MODEL = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            streaming=True, 
            callbacks=[FinalStreamingStdOutCallbackHandler(answer_prefix_tokens=["answer", ":"])]
        )
        self.EMBED_MODEL = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        # Paths
        self.VECTORSTORE = os.path.dirname(__file__) + "/data/vectorstore/"