import React from 'react';
import './style.css';

const Message = ({ message }) => {
  const { text, sender, timestamp } = message;
  const isUser = sender === 'user';

  const formattedTime = new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div className={`message ${isUser ? 'user' : 'chatbot'}`}>
      {!isUser && <div className="avatar" />}
      <div className="message-content">
        <div className="message-text" style={{ paddingRight: '1vw' }}> {text} </div>
        <div className="message-time">{formattedTime} </div>
      </div>
      {isUser && <div className="avatar" />}
    </div>
  );
};

export default Message;
