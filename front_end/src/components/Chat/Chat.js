import React, { useState, useRef, useEffect } from 'react';
import Message from './Message.js';
import axios from 'axios';
import './style.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (text) => {
    const userMessage = { text: text, sender: 'user', timestamp: new Date() };
    setMessages([...messages, userMessage]);

    try {
      const response = await axios.post('http://localhost:8000/get_response/', { question: text });
      const chatbotMessage = { text: response.data.message, sender: 'chatbot', timestamp: new Date() };
      setMessages([...messages, userMessage, chatbotMessage]);
    } catch (error) {
      console.error('Error getting response:', error);
    }
  };

  return (
    <div className="card chat-container">
      <div className = "card-body">
        <div className=" d-flex flex-column messages-container">
          {messages.map((message, index) => (
            <Message key={index} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </div>
        <div className="card-footer input-container">
          <input
            type="text"
            placeholder="Type a message..."
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.target.value.trim() !== '') {
                sendMessage(e.target.value);
                e.target.value = '';
              }
            }}
            className="form-control"
          />
        </div>
      </div>
    </div>
  );
};

export default Chat;