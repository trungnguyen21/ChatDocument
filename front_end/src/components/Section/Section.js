import React, { useEffect, useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import './style.css'

const SectionSwitchBar = ({ sections, activeSection, setActiveSection }) => {
  const [files, setFiles] = useState([]);

  const handleClick = (file) => {
    console.log("File name:", file);
  };

  useEffect(() => { 
    const fetchFiles = async () => {
      try {
        const response = await axios.get('http://localhost:8000/get_files/');
        const filesData = response.data.message;
        console.log(filesData);
        // Extract file names
        const fileNames = Object.values(filesData).map(file => {
          const parts = file.split('_');
          parts.shift(); // Remove the first part (file_id)
          return parts.join('_'); // Remaining parts form the file name
        });
        setFiles(fileNames);
      } catch (error) {
        console.error('Error fetching files:', error);
      }
    };

    fetchFiles();
  }, []);

  return (
    <div className='container mt-3'>
      <div className='card'>
        <div className='card-body'>
          <h1 className='card-title'>Files</h1>
          <div className='contained'>
            <div className="d-flex flex-column gap-2 mx-auto w-100">
              {files.map((file) => (
                <button key={file} type="button" className="btn btn-outline-secondary" onClick={() => handleClick(file)}>
                  {file}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SectionSwitchBar;
