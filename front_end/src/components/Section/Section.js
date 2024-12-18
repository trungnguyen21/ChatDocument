import React, { useEffect, useState, useContext } from 'react';
import ChatContext from '../context/ChatContext';
import FileContext from '../context/FileContext';
import ErrorContext from '../context/ErrorContext';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import './style.css';
import config from '../../config';

const SectionSwitchBar = ({ darkMode }) => {
  const [files, setFiles] = useState([]);
  const [isEmpty, setIsEmpty] = useState(true);
  const { state, dispatch } = useContext(ChatContext);
  const { fileUploaded } = useContext(FileContext);
  const { notify } = useContext(ErrorContext);
  const baseURL = config.baseURL;

  const changeSession = (sessionID) => {
    dispatch({ type: 'UPDATE_SESSION_ID', payload: sessionID });
  };

  const handleClick = async (fileId) => {
    console.log("File ID:", fileId);
    try {
      changeSession(fileId);
      console.log('Change section to: ', fileId);
      await axios.post(`${baseURL}/model_activation`, { session_id: fileId });
      console.log('Finish: ', fileId);
    } catch (error) {
      console.error('Error changing section:', error);

    }
  };

  const fetchFiles = () => {
    const fileMap = JSON.parse(localStorage.getItem('fileMap')) || {};
    const fileNames = Object.entries(fileMap).map(([fileId, fileName]) => ({ fileId, fileName }));
    setFiles(fileNames);
    setIsEmpty(Object.keys(fileMap).length === 0);
  };

  useEffect(() => {
    fetchFiles();
  }, [fileUploaded]);

  const deleteSection = async (fileId) => {
    console.log("Delete ", fileId);
    try {
      const fileMap = JSON.parse(localStorage.getItem('fileMap')) || {};  
      delete fileMap[fileId];
      localStorage.setItem('fileMap', JSON.stringify(fileMap));
      fetchFiles();

      await axios.delete(`${baseURL}/delete?file_id=${fileId}`);

      if (state.sessionId === fileId) {
        changeSession(null);
        fileId = null;
        window.location.reload();
      } 
      
      console.log('Finish deleting: ', fileId);
    } catch (error) {
      console.error('Error deleting section:', error);
      notify({ type: 'ERROR', payload: 'SERVER_ERROR' });
    }
  };

  return (
    <div className='container mt-3'>
      <div className='card'>
        <div className='card-body'>
          <h1 className='card-title'>Files</h1>
          {isEmpty && <p className='text-center'>No file to review yet.</p>}
          <div className='contained'>
            <div className="d-flex flex-column gap-2 mx-auto w-100">
              {files.map(({ fileName, fileId }) => (
                <div key={fileId} className="d-flex justify-content-between align-items-center">
                  <button
                    type="button"
                    className={`btn btn-label ${fileId === state.sessionId ? 
                      (darkMode ? 'btn-custom-darkmode' : 'btn-custom-lightmode') : 
                      (darkMode ? 'btn-outline-custom-darkmode' : 'btn-outline-custom-lightmode')}`}

                    onClick={() => handleClick(fileId)}
                  >
                    {fileName}
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline delete-btn"
                    data-toggle="tooltip"
                    title="Delete this file"
                    onClick={() => deleteSection(fileId)}
                  >
                    <i class="bi bi-x"></i>
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SectionSwitchBar;
