import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './style.css';

const FileUploader = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);

  const handleFileChange = (e) => {
    setSelectedFiles(Array.from(e.target.files));
  };

  const handleUpload = () => {
    console.log(selectedFiles);
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
          <button className="btn btn-primary" onClick={handleUpload}>
            Upload
          </button>
        </div>  
      </div>
    </div>
  );
};

export default FileUploader;
