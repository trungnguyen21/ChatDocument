from langchain_cohere import ChatCohere
from langchain_cohere.embeddings import CohereEmbeddings
from langchain_community.document_loaders.llmsherpa import LLMSherpaFileLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

import os, config

os.environ["COHERE_API_KEY"] = config.cohere_api_key
file = "data/sample.pdf"

# local host redis db
# docker run -d -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
# REDIS_URL = "redis://localhost:6379/0"

# redis cloud db for ChatHistory
REDIS_URL = os.environ.get("REDIS_URL")

# Configure the LLM Model to use
llm = ChatCohere(temperature=0.9)
cohere_embeddings = CohereEmbeddings()

# Prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
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
                                  embeddings=cohere_embeddings, 
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
        strategy='chunks'
    )
    docs = loader.load()
    print("Step 1. Successfully loaded the document.")

    # Ingest the document into vectorstore
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)
    vector = FAISS.from_documents(documents, cohere_embeddings)

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
def agent_init(file_path):
    # Creating an Agent where LLM will decide what steps to take
    try:
        retriever = vectorDocuments(file_path)
    except Exception as e:
        print("Error creating the retriever: ", e)
        raise Exception("Error creating the retriever")

    retriever_tool = create_retriever_tool(retriever, "DocumentAssistant", "Ask anything about the document")
    tools = [retriever_tool]

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    agent_executor_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history=get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    print("Step 3. Created agent success")
    return agent_executor_with_chat_history

# Answer the question
def answeringQuestion(question, session_id, file_path):
    # Invoking the agent with the question, also keep track of the chat history automatically
    try:
        agent_executor_with_chat_history = agent_init(file_path)
    except Exception as e:
        return f"Step 3. Unable to create agent: {e}"

    output = agent_executor_with_chat_history.invoke(
        {
        'input': question,
        },
        config={"configurable": {"session_id": session_id}},
    )

    print("Step 4. Successfully generated an output")
    return output["output"]

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
    
    

        
