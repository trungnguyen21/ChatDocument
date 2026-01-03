from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables import Runnable

import logging

from app.modules.prompts import *
from app.modules.utils import Utils
from app.config.config import Config

config = Config()
helpers = Utils()

llm = config.LLM_MODEL

class RagChat:
    def __init__(self) -> None:
        pass

    def init_chain_with_history(self, retriever):
        """
        Create history chain.
        """
        try:
            history_aware_retriever = create_history_aware_retriever(
                llm, 
                retriever, 
                contextualize_q_prompt
            )
            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
            logging.info("Step 3. Created chain success")

            return rag_chain
        except Exception as e:
            logging.error(f"Error in init_chain_with_history: {e}")
            raise

    async def output_generation(self, question: str, session_id: str, chain: Runnable):
        """
        Answer the given question.
        """
        try:
            answer = []
            async for chunk in chain.astream(
                {
                'input': question,
                'chat_history': helpers.get_session_history(session_id).messages
                }
            ):
                for key in chunk:
                    if key == "answer":
                        answer.append(chunk[key])
                        yield chunk[key]
        except Exception as e:
            logging.error(f"Error in output_generation: {e}")
            raise
        finally:
            helpers.log_chat_history(session_id, question, "".join(answer))

    async def chat_completion(self, question: str):
        """
        Get response.
        """
        full = []
        try:
            async for chunks in llm.astream(question):
                full += chunks.content
                yield chunks
        except Exception as e:
            logging.error(f"Error in chat_completion: {e}")
            raise
        finally:
            logging.info("".join(full))
