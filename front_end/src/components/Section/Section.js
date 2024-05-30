import React, { useEffect, useState, useContext } from 'react';
import ChatContext from '../context/ChatContext';
import FileContext from '../context/FileContext';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import './style.css';

const SectionSwitchBar = () => {
  const [files, setFiles] = useState([]);
  const { dispatch } = useContext(ChatContext);
  const { fileUploaded } = useContext(FileContext);

  const changeSession = (sessionID) => {
    dispatch({ type: 'UPDATE_SESSION_ID', payload: sessionID });
  };

  const handleClick = async (fileId) => {
    console.log("File ID:", fileId);
    try {
      await axios.post('http://localhost:8000/change_section/', { section_id: fileId });
      changeSession(fileId);
      console.log('Change section to: ', fileId);
      await axios.post('http://localhost:8000/initialize_model/');
      console.log('Finish: ', fileId);
    } catch (error) {
      console.error('Error changing section:', error);
    }
  };

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await axios.get('http://localhost:8000/get_files/');
        const filesData = response.data.message;
        console.log(filesData);
        const fileNames = Object.values(filesData).map(file => {
          const parts = file.split('_');
          const fileId = parts.shift();
          const fileName = parts.join('_');
          return { fileName, fileId };
        });
        setFiles(fileNames);
      } catch (error) {
        console.error('Error fetching files:', error);
      }
    };

    fetchFiles();
  }, [fileUploaded]);

  return (
    <div className='container mt-3'>
      <div className='card'>
        <div className='card-body'>
          <h1 className='card-title'>Files</h1>
          <div className='contained'>
            <div className="d-flex flex-column gap-2 mx-auto w-100">
              {files.map(({ fileName, fileId }) => (
                <button key={fileName} type="button" 
                        className="btn btn-outline-secondary" 
                        onClick={() => handleClick(fileId)}>
                  {fileName}
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
