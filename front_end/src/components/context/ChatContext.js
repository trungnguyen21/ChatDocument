import React, { createContext, useReducer } from 'react';

const ChatContext = createContext();

const chatReducer = (state, action) => {
  switch (action.type) {
    case 'UPDATE_SESSION_ID':
      return { ...state, sessionId: action.payload };
    default:
      return state;
  }
};

export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, { sessionId: null });

  return (
    <ChatContext.Provider value={{ state, dispatch }}>
      {children}
    </ChatContext.Provider>
  );
};

export default ChatContext;
