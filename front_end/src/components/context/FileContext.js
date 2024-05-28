import React, { createContext, useState } from 'react';

const FileContext = createContext();

export const FileProvider = ({ children }) => {
  const [fileUploaded, setFileUploaded] = useState(false);

  const notifyFileUploaded = () => {
    setFileUploaded(prev => !prev); // Toggle state to trigger refresh
  };

  return (
    <FileContext.Provider value={{ fileUploaded, notifyFileUploaded }}>
      {children}
    </FileContext.Provider>
  );
};

export default FileContext;
