import React, { useState, useRef, useEffect } from 'react';
import Message from './Message.js';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = (text) => {
    const userMessage = { text: 'User: ' + text, sender: 'user', timestamp: new Date() };
    const echoMessage = { text: 'Echo: ' + text, sender: 'chatbot', timestamp: new Date() };
    setMessages([...messages, userMessage, echoMessage]);
  };

  return (
    <div className = "chat-container">
      <div className = "messages-container">
        {messages.map((message, index) => (
          <Message key = {index} message = {message} />
        ))}
        <div ref = {messagesEndRef} />
      </div>
      <div className = "input-container">
        <input
          type = "text"
          placeholder = "Type a message..."
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
  );
};

export default Chat;
