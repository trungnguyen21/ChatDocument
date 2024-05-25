import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useEffect, useState } from 'react';
import axios from 'axios';
import './style.css'


const SectionSwitchBar = ({ sections, activeSection, setActiveSection }) => {
  const [files, setFiles] = useState([]);

  useEffect(() => { 
    const fetchFiles = async () => {
      try {
        const response = await axios.get('http://localhost:8000/get_files/');
        // console.log(typeof(response.data.message))
        console.log(Object.values(response.data.message))
        setFiles(Object.values(response.data.message));
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
              <div class="d-flex flex-column gap-2 mx-auto w-100">
                {files.map((file) => (
                    <button type="button" className="btn btn-outline-secondary">
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