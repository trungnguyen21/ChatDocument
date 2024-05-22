import React from 'react';

const Message = ({ message }) => {
  const { text, sender, timestamp } = message;
  const isUser = sender === 'user';

  return (
    <div className={`message ${isUser ? 'user' : 'chatbot'}`}>
      {!isUser && <div className = "avatar" />}
      <div className = "message-content">
        <div className = "message-text" style = {{ paddingRight: '1vw' }}> {text} </div>
        <div className = "message-time"> {new Date(timestamp).toLocaleTimeString()} </div>
      </div>
      {isUser && <div className = "avatar" />}
    </div>
  );
};

export default Message;