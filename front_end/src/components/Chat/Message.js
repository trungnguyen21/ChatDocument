import React from 'react';
import './style.css';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const Message = ({ message }) => {
  const { text, sender } = message;
  const isUser = sender === 'user';

  return (
    <div className={`message ${isUser ? 'user' : 'chatbot'}`}>
      <div className="message-content">
        <div className="message-text"> 
          <Markdown remarkPlugins={[remarkGfm]}>{text}</Markdown>
        </div>
      </div>

    </div>
  );
};

export default Message;
