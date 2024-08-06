import React, { useState, useRef, useEffect, useContext } from 'react';
import Message from './Message.js';
import axios from 'axios';
import ChatContext from '../Context/ChatContext.js';
import ErrorContext from '../Context/ErrorContext.js';
import './style.css';
import config from '../../config';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [isActive, setActive] = useState(false);
  const messagesEndRef = useRef(null);
  const { state } = useContext(ChatContext);
  const { notify } = useContext(ErrorContext);
  const session_id = state.sessionId;
  const baseURL = config.baseURL;

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (session_id === null) {
      setActive(false);
    } else {
      setActive(true);
    }
  }, [session_id]);

  useEffect(() => {
    const fetchChatHistory = async () => {
      if (state.sessionId) {
        try {
          const response = await axios.get(baseURL + '/chat_history', { params: { session_id: state.sessionId } });
          const chatHistory = response.data.message;
          if (chatHistory.length === 0) {
            // clear all previous messages
            setMessages([]);
            setMessages((prevMessages) => [
              ...prevMessages,
              {
                text: 'Welcome! How can I help you today?',
                sender: 'chatbot',
              },
            ]);
          } else {
            const message_history = chatHistory.map((message) => ({
              text: message.content,
              sender: message.type === 'human' ? 'user' : 'chatbot',
            }));
            setMessages(message_history);
          }
        } catch (error) {
          console.error('Error fetching chat history:', error);
          notify({ type: 'ERROR', payload: 'SERVER_ERROR' });
        }
      }
    };

    fetchChatHistory();
    // eslint-disable-next-line
  }, [state.sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (text) => {
    const userMessage = { text: text, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, userMessage]);

    const loadingMessage = { text: 'Generating a response...', sender: 'chatbot' };
    setMessages((prevMessages) => [...prevMessages, loadingMessage]);

    try {
      console.log('Session ID at Chat.js:', session_id);

      const response = await fetch(baseURL + `/chat_completion/?session_id=${session_id}&question=${text}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let chatbotMessage = { text: '', sender: 'chatbot' };
      let loadingMessageIndex = messages.length + 1;  // Index of the loading message in the state

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        chatbotMessage.text += decoder.decode(value, { stream: true });
        setMessages((prevMessages) => {
          const updatedMessages = [...prevMessages];
          updatedMessages[loadingMessageIndex] = { ...chatbotMessage };
          return updatedMessages;
        });
      }

      // Remove loading message once streaming is complete
      setMessages((prevMessages) => prevMessages.filter((_, index) => index !== loadingMessageIndex));

      // Add final chatbot message
      setMessages((prevMessages) => [...prevMessages, chatbotMessage]);

    } catch (error) {
      console.error('Error getting response:', error);
      const errorMessage = { text: 'Sorry, I encountered an error. Please try again. If the error is persistent, please reload the page.', sender: 'chatbot' };
      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages];
        const loadingMessageIndex = updatedMessages.findIndex(
          (message) => message.sender === 'chatbot' && message.text === 'Generating a response...'
        );
        if (loadingMessageIndex !== -1) {
          updatedMessages.splice(loadingMessageIndex, 1, errorMessage);
        }
        return updatedMessages;
      });
    }
  };

  const handleSendClick = (inputRef) => {
    if (isActive && inputRef.current.value.trim() !== '') {
      sendMessage(inputRef.current.value);
      inputRef.current.value = '';
    }
  };

  const inputRef = useRef(null);

  return (
    <div className="card chat-container">
      <div className="card-body d-flex flex-column messages-container">
        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="card-footer input-container d-flex">
        <input
          ref={inputRef}
          type="text"
          placeholder={isActive ? "Type a message..." : "Please upload or select a file."}
          onKeyDown={(e) => {
            if (isActive && e.key === 'Enter' && e.target.value.trim() !== '') {
              sendMessage(e.target.value);
              e.target.value = '';
            }
          }}
          className="form-control shadow-none"
          disabled={!isActive}
        />
        <button
          onClick={() => handleSendClick(inputRef)}
          className="btn btn-send"
          disabled={!isActive}
        >
          <i className="bi bi-send"></i>
        </button>
      </div>
    </div>
  );
};

export default Chat;
