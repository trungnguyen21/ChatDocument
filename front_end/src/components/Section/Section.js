import React, { useEffect, useState, useContext } from 'react';
import ChatContext from '../Context/ChatContext';
import FileContext from '../Context/FileContext';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import './style.css';
import config from '../../config';

const SectionSwitchBar = () => {
  const [files, setFiles] = useState([]);
  const [isEmpty, setIsEmpty] = useState(true); 
  const { state, dispatch } = useContext(ChatContext);
  const { fileUploaded } = useContext(FileContext);
  const baseURL = config.baseURL;

    const changeSession = (sessionID) => {
      dispatch({ type: 'UPDATE_SESSION_ID', payload: sessionID });
    };

    const handleClick = async (fileId) => {
      console.log("File ID:", fileId);
      try {
        changeSession(fileId);
        console.log('Change section to: ', fileId);
        await axios.post(baseURL+'/model_activation', { session_id: fileId });
        console.log('Finish: ', fileId);
      } catch (error) {
        console.error('Error changing section:', error);
      }
    };

    useEffect(() => {
      const fetchFiles = () => {
        const fileMap = JSON.parse(localStorage.getItem('fileMap')) || {};
        const fileNames = Object.entries(fileMap).map(([fileId, fileName]) => ({ fileId, fileName }));
        setFiles(fileNames);
        setIsEmpty(Object.keys(fileMap).length === 0);
      };

      fetchFiles();
    }, [fileUploaded]);

    return (
      <div className='container mt-3'>
        <div className='card'>
          <div className='card-body'>
            <h1 className='card-title'>Files</h1>
            {isEmpty && <h6 className='text-center'>No files uploaded yet.</h6>}
            <div className='contained'>
              <div className="d-flex flex-column gap-2 mx-auto w-100">
                {files.map(({ fileName, fileId }) => (
                  <div>
                    <button
                      key={fileId}
                      type="button"
                      className={`btn-label ${fileId === state.sessionId ? 'btn btn-secondary' : 'btn btn-outline-secondary'}`}
                      onClick={() => handleClick(fileId)}
                    >
                      {fileName}
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
