from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores.redis import Redis
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables import Runnable

import os, config, redis

os.environ["COHERE_API_KEY"] = config.cohere_api_key
os.environ["GOOGLE_API_KEY"] = config.GOOGLE_GEMINI_API_KEY
REDIS_URL = config.REDIS_URL

# Testing purposes
file = "data/files/sample1.pdf"

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Create a redis client
redis_client = redis.from_url(REDIS_URL)

# Prompt template
contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\
Be professional and do not include emojis or slang in your answer.\

{context}"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

vector_path = os.path.dirname(__file__) + "/data/vectorstore/"

def load_document(file_path: str):
    """
    Indexing document, returns VectorStoreRetriever
    Step 1: Check if the vectorstore for this document exist.
            If it does, return the data and create a new chain in step 4

    Step 2: Split the documents into chunks

    Step 3: Create an ensemble retriever
        1. Create a sematic retriever from RedisVectorStore
        2. Create a BM25 retriever
    """
    try:
        first_cut = f"{file_path.split('/')[-1]}"
        second_cut = first_cut.removeprefix("files")
        thirdcut = second_cut.split("\\")[-1]
        vectorstore_file = thirdcut.split("_")[0]

        print("loading file name:" + vectorstore_file)

        # check if the vectorstore already exist
        if len(redis_client.keys(f"doc:{vectorstore_file}:*")) > 0:
            print("Step 1. Vectorstore already exist. Skipping step 2")
            return Redis.from_existing_index(
                embedding=embeddings,
                index_name=vectorstore_file, 
                redis_url=REDIS_URL,
                schema="data/schema.yaml",
                key_prefix="doc")
        else:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            print("Step 1. Successfully loaded the document.")

            text_splitter = SemanticChunker(embeddings)
            documents = text_splitter.split_documents(docs)
            print("Step 2. Splitted the document into chunks")

            redis_vector = ingest_document(documents, vectorstore_file)
            print("Step 3. Ingested document into vector store")

            return redis_vector
    except Exception as e:
        print(f"Error in load_document: {e}")
        raise

def vectorDocuments(file_path: str):
    """
    """
    try:
        redis_vector = load_document(file_path)
        retriever = redis_vector.as_retriever(search_kwargs={"k": 2})
        print("Step 3. Successfully created a retriever")

        return retriever
    except Exception as e:
        print(f"Error in vectorDocuments: {e}")
        raise

def ingest_document(docs: list, file_name: str) -> Redis:
    """
    Ingest document into the vectordb. Redis only supports 100 
    documents at a time.
    Args: 
        docs: List[Document]
        file_name: name of the file stored on Redis
    """
    try:
        for i in range(0, len(docs), 100):
            if i + 100 > len(docs):
                chunks = docs[i:]
            else:
                chunks = docs[i:i+100]

            vector = Redis.from_documents(
                chunks, 
                embeddings,
                redis_url=REDIS_URL,
                index_name=file_name.split("_")[0],
            )
        vector.write_schema("data/schema.yaml")
        return vector
    except Exception as e:
        print(f"Error in ingest_document: {e}")
        raise

def get_session_history(session_id: str):
    """
    Get the chat history of the session \n
    Args:
        session_id: str
    """
    return RedisChatMessageHistory(session_id, REDIS_URL)

def init_chain_with_history(retriever):
    """
    Step 4 of starting the chat bot
    Create history chain
    String -> Chain \n
    Args:
        retriever: VectorStoreRetriever
    """
    try:
        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        print("Step 4. Created chain success")

        return rag_chain
    except Exception as e:
        print(f"Error in init_chain_with_history: {e}")
        raise

def answeringQuestion(question: str, session_id: str, chain: Runnable):
    """
    Answer the given question, session_id and file_path
    String String chain -> String \n
    Args:
        question: str
        session_id: str
        rag_chain_with_history: Runnable
    """
    try:
        output = chain.invoke(
            {
            'input': question,
            'chat_history': get_session_history(session_id).messages
            }
        )
        log_chat_history(session_id, question, str(output["answer"]))

        print("Step 4. Successfully generated an output")
        return str(output["answer"])
    except Exception as e:
        print(f"Error in answeringQuestion: {e}")
        raise

def log_chat_history(session_id: str, human_message, ai_message):
    """
    Manually log chat messages into our database \n
    Args:
        session_id: str
        human_message: str
        ai_message: str
    """
    try:
        message_log = RedisChatMessageHistory(session_id, config.REDIS_URL)
        message_log.add_user_message(human_message)
        message_log.add_ai_message(ai_message)
    except Exception as e:
        print(f"Error in log_chat_history: {e}")
        raise

## Testing
def user_interface(file):
    print("Initializing the chatbot...")

    session_id = input("Please enter your session id: ")
    try:
        retriever = vectorDocuments(file)
        rag_chain = init_chain_with_history(retriever)
    except Exception as e:
        print(f"Step 4. Unable to create chain: {e}")
        return
    
    while True:
        user_input = input("Please ask your question: ")
        if user_input == "exit":
            return
        print("DocumentAssist: " + answeringQuestion(user_input, session_id, rag_chain))

if __name__ == "__main__":
    user_interface(file)
