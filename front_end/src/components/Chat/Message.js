import React from 'react';
import './style.css';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const Message = ({ message, darkMode }) => {
  const { text, sender } = message;
  const isUser = sender === 'user';

  return (
    <div className={`message ${isUser ? 'user' : 'chatbot'} ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      <div className={`message-content ${darkMode ? 'dark-mode' : 'light-mode'}`}>
        <div className={`message-text ${darkMode ? 'dark-mode' : 'light-mode'}`}> 
          <Markdown remarkPlugins={[remarkGfm]}>{text}</Markdown>
        </div>
      </div>
    </div>
  );
};

export default Message;
