import React from 'react';
import Chat from './components/Chat';
import FileUploader from './components/FileUpload/Upload';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  return (
    <div>
      <div className = "row">
        <div className = "col-8">
          <div className = "bg-1">
            <h1 className = "text-center mt-5 text-logo"> Chat Document</h1>
            <Chat />
          </div>
        </div>

        <div className = "col-4">
          <div className = "uploader">
          <FileUploader />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;