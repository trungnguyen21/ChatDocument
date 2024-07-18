import React, { createContext, useReducer } from 'react';

const ErrorContext = createContext();

const errorReducer = (state, action) => {
  switch (action.type) {
    case 'ERROR':
      return { ...state, error_type: action.payload };
    case 'CLEAR':
      return { ...state, error_type: null };
    default:
      return state;
  }
};

export const ErrorProvider = ({ children }) => {
  const [state, notify] = useReducer(errorReducer, { error_type: null });

  return (
    <ErrorContext.Provider value={{ state, notify }}>
      {children}
    </ErrorContext.Provider>
  );
};

export default ErrorContext;
