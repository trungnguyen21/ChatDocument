import React, { useState, useEffect } from 'react';

import Chat from './components/Chat/Chat';
import FileUploader from './components/FileUpload/Upload';
import SectionSwitchBar from './components/Section/Section';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMoon } from '@fortawesome/free-solid-svg-icons';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div>
      <div className="row">
        <div className="col-4 d-flex">
          <button className='toggle-dark-mode' onClick={toggleDarkMode}>
            {darkMode ? <FontAwesomeIcon icon={faMoon} /> : <FontAwesomeIcon icon={faMoon} />}
          </button>
        </div>
        <h1 className="text-center text-logo col-8"> Chat Document</h1>
      </div>
      
      <div className="row">
        <div className="col-4">
          <div className="uploader ">
            <FileUploader />
            <SectionSwitchBar />
          </div>
        </div>

        <div className="col-8">
          <div className="bg-1">
            <Chat />
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
