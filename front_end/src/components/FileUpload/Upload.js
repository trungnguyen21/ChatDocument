import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './style.css';
import axios from 'axios';

const FileUploader = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('http://localhost:8000/uploadfile/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('File ID:', response.data.file_id);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const startChat = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/initialize_model/', {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log("Complete");
    } catch (error) {
      console.error('Error Chain file:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container mt-5">
      <div className="card">
        <div className="card-body">
          <h5 className="card-title">Upload Your File</h5>
          <input
            type="file"
            onChange={handleFileChange}
            className="form-control-file mb-3"
          />
          <button
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={!selectedFile || loading}
          >
            Upload
          </button>

          <button
            className="btn btn-primary"
            onClick={startChat}
            disabled={!selectedFile || loading}
          >
            {loading ? 'Starting...' : 'Start!'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default FileUploader;
