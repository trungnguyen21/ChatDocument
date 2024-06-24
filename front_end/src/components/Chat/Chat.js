import React, { useState, useRef, useEffect, useContext } from 'react';
import Message from './Message.js';
import axios from 'axios';
import ChatContext from '../Context/ChatContext.js';
import './style.css';
import config from '../../config';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [isActive, setActive] = useState(false);
  const messagesEndRef = useRef(null);
  const { state } = useContext(ChatContext);
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
          const chatHistory = await response.data.message.map((message) => ({
            text: message.content,
            sender: message.type === 'human' ? 'user' : 'chatbot',
          }));
          setMessages(chatHistory);
        } catch (error) {
          console.error('Error fetching chat history:', error);
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
      console.log('Session ID at Chat.js:', session_id);
      const response = await axios.post(baseURL + '/chat_completion/', { question: text, session_id: session_id });
      const chatbotMessage = { text: response.data.message, sender: 'chatbot' };
      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages];
        const loadingMessageIndex = updatedMessages.findIndex(
          (message) => message.sender === 'chatbot' && message.text === 'Generating a response...'
        );
        if (loadingMessageIndex !== -1) {
          updatedMessages.splice(loadingMessageIndex, 1, chatbotMessage);
        }
        return updatedMessages;
      });
    } catch (error) {
      console.error('Error getting response:', error);
    }
  };

  return (
    <div className="card chat-container">
      <div className="card-body d-flex flex-column messages-container">
        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="card-footer input-container">
        <input
          type="text"
          placeholder={isActive ? "Type a message..." : "Please upload a file or select a section"}
          onKeyDown={(e) => {
            if (isActive && e.key === 'Enter' && e.target.value.trim() !== '') {
              sendMessage(e.target.value);
              e.target.value = '';
            }
          }}
          className="form-control shadow-none"
          disabled={!isActive}
        />
      </div>
    </div>
  );
};

export default Chat;
