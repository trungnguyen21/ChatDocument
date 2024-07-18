import React, { useState, useEffect, useContext } from 'react';
import { ChatProvider } from './components/Context/ChatContext.js';
import { FileProvider } from './components/Context/FileContext.js';
import ErrorContext from './components/Context/ErrorContext.js';
import Chat from './components/Chat/Chat';
import FileUploader from './components/FileUpload/Upload';
import SectionSwitchBar from './components/Section/Section';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import config from './config';
import axios from 'axios';
import Navbar from './components/Navbar/Navbar.js';
import ErrorPopup from './components/ErrorPopup/ErrorPopup.js';

function App() {
  const baseURL = config.baseURL;
  const { state, notify } = useContext(ErrorContext); 

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
      notify({ type: 'ERROR', payload: 'SERVER_ERROR' });
      console.error('Error flushing Redis:', error);
    }
  };

  return (
    <ChatProvider>
      <FileProvider>
        <ErrorPopup message={state.error_type} showReloadButton={true} />
        <div>
          <Navbar classname="nav-template" darkMode={darkMode} toggleDarkMode={toggleDarkMode}
           flushRedis={flushRedis} className="navbar"
           fileUploader={<FileUploader />}
            sectionSwitchBar={<SectionSwitchBar darkMode={darkMode}/>} />

          <div className="mt-3">
            <div className="row no-gutter">
              <div className="col-md-4 d-none d-md-block">
                <div className="uploader">
                  <FileUploader />
                  <SectionSwitchBar darkMode={darkMode}/>
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
