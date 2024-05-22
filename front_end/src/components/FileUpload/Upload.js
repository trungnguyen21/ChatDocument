import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './style.css';
import axios from 'axios';

const FileUploader = () => {
  const [selectedFile, setSelectedFile] = useState([]);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files);
  };

  const handleUpload = async () => {
    const formData = {
      file : selectedFile
    }

    try {
      console.log(formData)
      const response = await axios.post
      ('http://localhost:8000/uploadfile/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('File ID:', response.data.file_id);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div className="container mt-5">
      <div className="card">
        <div className="card-body">
          <h5 className="card-title">Upload Your Files</h5>
          <input
            type="file"
            multiple
            onChange={handleFileChange}
            className="form-control-file mb-3"
          />
          <button
            className="btn btn-primary btn-primary"
            onClick={handleUpload}
            disabled={selectedFile.length === 0}
          >
            Upload
          </button>
        </div>
      </div>
    </div>
  );
};

export default FileUploader;
