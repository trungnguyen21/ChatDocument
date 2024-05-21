from langchain_experimental.text_splitter import SemanticChunker

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

REDIS_URL = config.REDIS_URL

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



def vectorDocuments(file_path):
    """
    Indexing document, returns VectorStoreRetriever
    """
    vectorstore_file = f"{file_path.split("/")[-1]}_vectorstore" # sample.pdf_vectorstore
    cur_path = vector_path + vectorstore_file

    # Check if the vectorstore for this document exist
    print("Operating filepath: ", vector_path)
    print("Checking vectorstore file at: ", cur_path)

    # if os.path.exists(cur_path):
    #     print(f"Step 2. File '{vectorstore_file}' already exists. Using indexed file.")
    #     vector = FAISS.load_local(folder_path=cur_path, 
    #                               embeddings=embeddings, 
    #                               index_name=vectorstore_file,
    #                               allow_dangerous_deserialization=True)
    #     retriever = vector.as_retriever()
    
    # Load the document
    # Only allows PDFs, handle in client side
    # else: 
    loader = LLMSherpaFileLoader(
        file_path=file_path,
        new_indent_parser=True,
        apply_ocr=True,
        strategy = 'chunks'
    )
    docs = loader.load()
    print("Step 1. Successfully loaded the document.")

    # Ingest the document into vectorstore
    text_splitter = SemanticChunker(embeddings)
    documents = text_splitter.split_documents(docs)
    vector = FAISS.from_documents(documents, embeddings)

    # vector.save_local(folder_path=cur_path, index_name=f"{vectorstore_file}")
    print("Step 1.5. Saved the vectorstore file at:", cur_path)

    # Creating a retrieval chain to retrieve data from the document, 
    # feed it to the LLM model and ask the original question
    retriever = vector.as_retriever()

    print("Step 2. Successfully created a retriever")
    return retriever



def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Get the chat history of the session
    """
    return RedisChatMessageHistory(session_id, REDIS_URL)



def init_chain_with_history(retriever):
    """
    Create history chain
    String -> Chain
    """
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    print("Step 3. Created agent success")
    rag_chain_with_history = RunnableWithMessageHistory(
        rag_chain,
        get_session_history = get_session_history,
        input_messages_key = "input",
        history_messages_key = "chat_history",
    )
    
    return rag_chain_with_history



def answeringQuestion(question, session_id, rag_chain_with_history):
    """
    Answer the given question, session_id and file_path
    String String chain -> String
    """
    output = rag_chain_with_history.invoke(
        {
        'input': question,
        }, config={"configurable": {"session_id": session_id}},
    )

    print("Step 4. Successfully generated an output")
    return str(output["answer"])



## Testing
def user_interface(file):
    print("Initializing the chatbot...")

    session_id = input("Please enter your session id: ")
    try:
        retriever = vectorDocuments(file)
        rag_chain = init_chain_with_history(retriever)
    except Exception as e:
        return f"Step 3. Unable to create agent: {e}"
    
    while True:
        user_input = input("Please ask your question: ")
        if user_input == "exit":
            return
        print("DocumentAssist: " + answeringQuestion(user_input, session_id, rag_chain))

if __name__ == "__main__":
    user_interface(file)
    
    

        
