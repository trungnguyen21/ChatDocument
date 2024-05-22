import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import 'bootstrap/dist/css/bootstrap.min.css';

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
    <div className="container">
      <div className="row">
        <div className="col-md-8 offset-md-2">
          <div className="card">
            <div className="card-body messages-container">
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
      </div>
    </div>
  );
};

export default Chat;
