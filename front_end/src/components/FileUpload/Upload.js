import React, { useState, useContext } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './style.css';
import FileContext from '../context/FileContext';
import ChatContext from '../context/ChatContext';
import config from '../../config';

const FileUploader = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const { notifyFileUploaded } = useContext(FileContext);
  const { dispatch } = useContext(ChatContext);
  const baseURL = config.baseURL;

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setDone(false);
  };

  const changeSession = (sessionID) => {
    dispatch({ type: 'UPDATE_SESSION_ID', payload: sessionID });
  }

  const handleUpload = async () => {
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
            accept=".pdf,.doc,.docx,.xls,.xlsx"
          />
          <div className="text-center">
            <button
              className="btn btn-primary"
              onClick={handleUpload}
              disabled={!selectedFile || loading}
            >
              {loading ? 'Uploading...' : (done ? 'Done' : 'Upload')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUploader;
