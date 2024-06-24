import React, { useState, useEffect } from 'react';
import { ChatProvider } from './components/Context/ChatContext.js';
import { FileProvider } from './components/Context/FileContext.js';
import Chat from './components/Chat/Chat';
import FileUploader from './components/FileUpload/Upload';
import SectionSwitchBar from './components/Section/Section';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import config from './config';
import axios from 'axios';
import Navbar from './components/Navbar/Navbar.js';

function App() {
  const baseURL = config.baseURL;
  console.log('Base URL:', baseURL);

  const [darkMode, setDarkMode] = useState(() => {
    const savedTheme = localStorage.getItem('darkMode');
    return savedTheme !== null ? JSON.parse(savedTheme) : true;
  });

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const flushRedis = async () => {
    try {
      await axios.delete(`${baseURL}/flush`);
      localStorage.removeItem('fileMap');
      window.location.reload();
    } catch (error) {
      console.error('Error flushing Redis:', error);
      // Handle error gracefully, e.g., show a toast or alert
    }
  };

  return (
    <ChatProvider>
      <FileProvider>
        <div>
          <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode}
           flushRedis={flushRedis} className="navbar"
           fileUploader={<FileUploader />}
            sectionSwitchBar={<SectionSwitchBar />} />

          <div className="mt-4">
            <div className="row">
              <div className="col-md-4 d-none d-md-block">
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
        </div>
      </FileProvider>
    </ChatProvider>
  );
}

export default App;
