import React, { useState, useEffect, useContext } from 'react';
import { ChatProvider } from './components/context/ChatContext.js';
import { FileProvider } from './components/context/FileContext.js';
import ErrorContext from './components/context/ErrorContext.js';
import Chat from './components/Chat/Chat';
import FileUploader from './components/FileUpload/Upload';
import SectionSwitchBar from './components/Section/Section';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import Navbar from './components/Navbar/Navbar.js';
import ErrorPopup from './components/ErrorPopup/ErrorPopup.js';
import Footer from './components/Footer/Footer.js';

function App() {
  const { state } = useContext(ErrorContext); 

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

  return (
    <ChatProvider>
      <FileProvider>
        <ErrorPopup message={state.error_type} showReloadButton={true} />
        <div>
          <Navbar classname="nav-template" 
           className="navbar"
           darkMode={darkMode} toggleDarkMode={toggleDarkMode}
           footer={<Footer />}
           fileUploader={<FileUploader />}
           sectionSwitchBar={<SectionSwitchBar darkMode={darkMode}/>} />

          <div className="mt-3">
            <div className="row no-gutter">
              <div className="col-md-4 d-none d-md-block">
                <div className="uploader">
                  <FileUploader />
                  <SectionSwitchBar darkMode={darkMode}/>
                  <Footer />
                </div>
              </div>

              <div className="col-md-8 col-sm-12 ">
                <div className="bg-1">
                  <Chat darkMode={darkMode} />
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
