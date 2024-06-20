import React, { useState, useEffect } from 'react';
import { ChatProvider } from './components/context/ChatContext';
import { FileProvider } from './components/context/FileContext';
import Chat from './components/Chat/Chat';
import FileUploader from './components/FileUpload/Upload';
import SectionSwitchBar from './components/Section/Section';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import config from './config';
import axios from 'axios';

function App() {
  const baseURL = config.baseURL;
  console.log('Base URL:', baseURL);

  const [darkMode, setDarkMode] = useState(() => {
    // Retrieve the theme from localStorage if it exists, otherwise default to true
    const savedTheme = localStorage.getItem('darkMode');
    return savedTheme !== null ? JSON.parse(savedTheme) : true;
  });

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    // Save the theme preference to localStorage
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const flushRedis = async () => {
    await axios.delete(baseURL+"/flush")
    // clear local storage file_map
    localStorage.removeItem('fileMap');
    window.location.reload();
  }

  return (
    <ChatProvider>
      <FileProvider>
        <div>
          <div className="row">
            <div className="col-md-4 col-sm-0 d-flex justify-content-center ps-5">
              <button className='toggle' onClick={toggleDarkMode}>
                {darkMode ? <i class="bi bi-moon"></i> : <i class="bi bi-moon-fill"></i>}
              </button>
              <button className='toggle' onClick={flushRedis}>
                {darkMode ? <i class="bi bi-trash"></i> : <i class="bi bi-trash-fill"></i>}
              </button>
            </div>
            <h1 className="text-center text-logo col-md-8 col-sm-12"> Chat with your Document </h1>
          </div>
          
          <div className="row">
            <div className="col-md-4 col-sm-0">
              <div className="uploader">
                <FileUploader />
                <SectionSwitchBar />
              </div>
            </div>

            <div className="col-md-8 col-sm-12">
              <div className="bg-1">
                <Chat />
              </div>
            </div>

          </div>
        </div>
      </FileProvider>
    </ChatProvider>
  );
}

export default App;
