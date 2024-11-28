import React, { useState, useContext } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './style.css';
import FileContext from '../context/FileContext';
import ChatContext from '../context/ChatContext';
import ErrorContext from '../context/ErrorContext';
import config from '../../config';

const FileUploader = () => {
  const MAX_FILE_SIZE = 3 * 1024 * 1024; // 3MB

  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const { notifyFileUploaded } = useContext(FileContext);
  const { dispatch } = useContext(ChatContext);
  const { notify } = useContext(ErrorContext);
  const baseURL = config.baseURL;

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setDone(false);
  };

  const changeSession = (sessionID) => {
    dispatch({ type: 'UPDATE_SESSION_ID', payload: sessionID });
  }

  const handleUpload = async () => {
    if (selectedFile.size > MAX_FILE_SIZE) {
      notify({ type: 'ERROR', payload: 'FILE_TOO_LARGE' });
      setSelectedFile(null);
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(baseURL+'/upload/', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      console.log('File ID:', data.file_id);

      // Update local storage with new file
      const fileMap = JSON.parse(localStorage.getItem('fileMap')) || {};
      fileMap[data.file_id] = selectedFile.name;
      localStorage.setItem('fileMap', JSON.stringify(fileMap));

      notifyFileUploaded();
      changeSession(data.file_id);
      setDone(true);
    } catch (error) {
      console.error('Error uploading file:', error);
      notify({ type: 'ERROR', payload: 'CONNECTION_ERROR' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <div className="card-body">
          <h5 className="card-title">Upload Your File</h5>
          <input
            type="file"
            onChange={handleFileChange}
            className="form-control-file mb-3"
            accept="application/pdf"
          />
          <div className="text-center">
            <button
              type='button'
              className="btn btn-primary always-white"
              data-toggle="tooltip"
              data-placement="top"
              title="Upload your file to start, max 3MB."
              onClick={handleUpload}
              disabled={!selectedFile || loading}
            >
              {loading ? 'Uploading...' : (done ? 'Done' : 'Review!')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUploader;
