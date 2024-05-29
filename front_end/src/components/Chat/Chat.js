import React, { useState, useRef, useEffect, useContext } from 'react';
import Message from './Message.js';
import axios from 'axios';
import ChatContext from '../context/ChatContext';
import './style.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);
  const { state } = useContext(ChatContext);

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    const fetchChatHistory = async () => {
      if (state.sessionId) {
        try {
          const response = await axios.get('http://localhost:8000/get_chat_history');
          console.log(response.data.message)
          const chatHistory = response.data.message.map((message) => ({
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

    try {
      const response = await axios.post('http://localhost:8000/get_response/', { question: text });
      const chatbotMessage = { text: response.data.message, sender: 'chatbot' };
      setMessages((prevMessages) => [...prevMessages, userMessage, chatbotMessage]);
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