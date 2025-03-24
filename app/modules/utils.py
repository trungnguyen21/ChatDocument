import time

from langchain_community.chat_message_histories import RedisChatMessageHistory

import app.config.config as config

redis_url = config.Config().REDIS_URL

class Utils:
    def __init__(self):
        """
        Initialize the Utils class.
        """
        pass

    def get_session_history(self, session_id: str):
        """
        Get the chat history of the session.
        """
        return RedisChatMessageHistory(session_id, redis_url)

    def log_chat_history(session_id: str, human_message, ai_message):
        """
        Log chat messages into our database.
        """
        try:
            message_log = RedisChatMessageHistory(session_id, redis_url)
            message_log.add_user_message(human_message)
            message_log.add_ai_message(ai_message)
        except Exception as e:
            print(f"Error in log_chat_history: {e}")
            raise

    def measure_time(func):
        """Decorator to measure the execution time of a function."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
            return result
        return wrapper