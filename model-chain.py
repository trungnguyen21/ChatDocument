# from langchain_cohere import ChatCohere
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cohere.embeddings import CohereEmbeddings
from langchain_community.document_loaders.llmsherpa import LLMSherpaFileLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

import os, config

os.environ["COHERE_API_KEY"] = config.cohere_api_key
os.environ["GOOGLE_API_KEY"] = config.GOOGLE_GEMINI_API_KEY
file = "data/files/sample.pdf"

# local host redis db
# docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
# REDIS_URL = "redis://localhost:6379/0"

# redis cloud db for ChatHistory
# REDIS_URL = os.environ.get("REDIS_URL")
REDIS_URL = config.REDIS_URL

# Configure the LLM Model to use
# llm = ChatCohere(temperature=0.9)
# genai.configure(api_key=config.GOOGLE_GEMINI_API_KEY)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
embeddings = CohereEmbeddings()

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

# Indexing document, returns VectorStoreRetriever
def vectorDocuments(file_path):
    vectorstore_file = f"{file_path.split("/")[-1]}_vectorstore" # sample.pdf_vectorstore
    cur_path = vector_path + vectorstore_file

    # Check if the vectorstore for this document exist
    print("Operating filepath: ", vector_path)
    print("Checking vectorstore file at: ", cur_path)
    if os.path.exists(cur_path):
        print(f"Step 2. File '{vectorstore_file}' already exists. Using indexed file.")
        vector = FAISS.load_local(folder_path=cur_path, 
                                  embeddings=embeddings, 
                                  index_name=vectorstore_file,
                                  allow_dangerous_deserialization=True)
        retriever = vector.as_retriever()
        return retriever
    
    # Load the document
    # Only allows PDFs, handle in client side
    loader = LLMSherpaFileLoader(
        file_path=file_path,
        new_indent_parser=True,
        apply_ocr=True,
        strategy = 'chunks'
    )
    docs = loader.load()
    print("Step 1. Successfully loaded the document.")

    # Ingest the document into vectorstore
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)
    vector = FAISS.from_documents(documents, embeddings)

    vector.save_local(folder_path=cur_path, index_name=f"{vectorstore_file}")
    print("Step 1.5. Saved the vectorstore file at:", cur_path)

    # Creating a retrieval chain to retrieve data from the document, 
    # feed it to the LLM model and ask the original question
    retriever = vector.as_retriever()
    # retriever = rds.as_retriever(search_type="similarity", search_kwargs={
    #     "k": 5, 
    #     "distance_threshold": 0.1,
    # })
    print("Step 2. Successfully created a retriever")
    return retriever

# Get the chat history of the session
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    return RedisChatMessageHistory(session_id, REDIS_URL)

# Create an agent to interact with the user
def init_chain_with_history(file_path):
    # Creating an Agent where LLM will decide what steps to take
    try:
        retriever = vectorDocuments(file_path)
    except Exception as e:
        print("Error creating the retriever: ", e)
        raise Exception("Error creating the retriever")

    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    print("Step 3. Created agent success")
    return rag_chain

# Answer the question
def answeringQuestion(question, session_id, file_path):
    # Invoking the agent with the question, also keep track of the chat history automatically
    try:
        rag_chain = init_chain_with_history(file_path)
    except Exception as e:
        return f"Step 3. Unable to create agent: {e}"

    rag_chain_with_history = RunnableWithMessageHistory(
        rag_chain,
        get_session_history=get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    output = rag_chain_with_history.invoke(
        {
        'input': question,
        }, config={"configurable": {"session_id": session_id}},
    )

    print("Step 4. Successfully generated an output")
    return str(output["answer"])

# For testing purposes
def user_interface(file):
    print("Initializing the chatbot...")

    session_id = input("Please enter your session id: ")
    while True:
        user_input = input("Please ask your question: ")
        if user_input == "exit":
            return
        print("DocumentAssist: " + answeringQuestion(user_input, session_id, file)) # new session = new chat


if __name__ == "__main__":
    user_interface(file)
    
    

        
