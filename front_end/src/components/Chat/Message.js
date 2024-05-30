import React from 'react';
import './style.css';

const Message = ({ message }) => {
  const { text, sender } = message;
  const isUser = sender === 'user';

  return (
    <div className={`message ${isUser ? 'user' : 'chatbot'}`}>
      {!isUser && <div className="avatar" />}
      <div className="message-content">
        <div className="message-text" style={{ paddingRight: '1vw' }}> {text} </div>
      </div>
      {isUser && <div className="avatar" />}
    </div>
  );
};

export default Message;
