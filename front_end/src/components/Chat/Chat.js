import React, { useState, useRef, useEffect, useContext } from 'react';
import Message from './Message.js';
import axios from 'axios';
import ChatContext from '../context/ChatContext.js';
import ErrorContext from '../context/ErrorContext.js';
import './style.css';
import config from '../../config';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [isActive, setActive] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const { state } = useContext(ChatContext);
  const { notify } = useContext(ErrorContext);
  const session_id = state.sessionId;
  const baseURL = config.baseURL;

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
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
          const response = await axios.get(baseURL + '/chat_history', {
            params: { session_id: state.sessionId },
          });
          const chatHistory = response.data.message;
          if (chatHistory.length === 0) {
            setMessages([
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
      const response = await fetch(
        `${baseURL}/chat_completion/?session_id=${session_id}&question=${text}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let chatbotMessage = { text: '', sender: 'chatbot' };

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        chatbotMessage.text += decoder.decode(value, { stream: true });
        setMessages((prevMessages) => {
          const updatedMessages = [...prevMessages];
          updatedMessages[prevMessages.length - 1] = { ...chatbotMessage };
          return updatedMessages;
        });
      }

      setMessages((prevMessages) => [...prevMessages, chatbotMessage]);
    } catch (error) {
      console.error('Error getting response:', error);
      const errorMessage = {
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'chatbot',
      };
      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages];
        updatedMessages[prevMessages.length - 1] = errorMessage;
        return updatedMessages;
      });
    }
  };

  const handleInput = () => {
    const input = inputRef.current;
    if (input) {
      input.style.height = 'auto'; // Reset height to calculate new height
      input.style.height = `${Math.min(input.scrollHeight, 96)}px`; // Max height for 4 lines
    }
  };

  const handleSendClick = () => {
    if (isActive && inputRef.current.value.trim() !== '') {
      sendMessage(inputRef.current.value);
      inputRef.current.value = '';
      inputRef.current.style.height = 'auto'; // Reset height after sending
    }
  };

  return (
    <div className="chat-wrapper">
      <div className="messages-container d-flex flex-column">
        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-container">
        <textarea
          ref={inputRef}
          className="chat-input"
          placeholder={isActive ? 'Type a message...' : 'Please upload or select a file.'}
          onInput={handleInput} // Adjust height dynamically
          onKeyDown={(e) => {
            if (isActive && e.key === 'Enter' && e.target.value.trim() !== '') {
              e.preventDefault(); // Prevent new line
              handleSendClick();
            }
          }}
        />
        <button onClick={handleSendClick} className="btn-send">
          <i className="bi bi-send"></i>
        </button>
      </div>
    </div>
  );
};

export default Chat;