import React, { useState, useRef, useEffect, useContext } from 'react';
import Message from './Message.js';
import axios from 'axios';
import ChatContext from '../context/ChatContext.js';
import './style.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);
  const { state } = useContext(ChatContext);
  const session_id = state.sessionId

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    const fetchChatHistory = async () => {
      if (state.sessionId) {
        try {
          const response = await axios.get('http://localhost:8000/chat_history/', { params: { session_id: state.sessionId } });
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
    // Add user's message first
    const userMessage = { text: text, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
  
    // Add loading message
    const loadingMessage = { text: 'Generating a response...', sender: 'chatbot' };
    setMessages((prevMessages) => [...prevMessages, loadingMessage]);
  
    try {
      console.log('Session ID at Chat.js:', session_id);
      const response = await axios.post('http://localhost:8000/chat_completion/', {question: text, session_id: session_id});
      // Replace loading message with chatbot's response
      const chatbotMessage = { text: response.data.message, sender: 'chatbot' };
      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages];
        // Find index of loading message and replace it with chatbot's response
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
      // Optionally, handle error here
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
          placeholder="Type a message..."
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.target.value.trim() !== '') {
              sendMessage(e.target.value);
              e.target.value = '';
            }
          }}
          className="form-control shadow-none"
        />
      </div>
    </div>
  );
};

export default Chat;