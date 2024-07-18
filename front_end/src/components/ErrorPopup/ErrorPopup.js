import React, { useEffect } from 'react';
import ErrorContext from '../Context/ErrorContext';
import './styles.css';

const ErrorPopup = ({ message, showReloadButton }) => {
    const { state } = React.useContext(ErrorContext);
    useEffect(() => {
        const errorBackground = document.querySelector('.error-background');
        if (errorBackground) {
            if (state.error_type === null) {
                errorBackground.style.display = 'none';
            } else {
                errorBackground.style.display = 'block';
            }
        }
    }, [state]);

    const handleClose = () => {
        const errorBackground = document.querySelector('.error-background');
        if (errorBackground) {
            errorBackground.style.display = 'none';
        }
    };

    const handleReload = () => {
        window.location.reload();
    };

    const errorTypes = {
        CONNECTION_ERROR: 'There is a connection error. Please check your internet connection and try again.',
        SERVER_ERROR: 'Server error due to high demand. Please try again later.',
        TIMEOUT_ERROR: 'Server timeout. Please try again later.',
        FILE_TOO_LARGE: 'We currently support PDF files < 3MB. Please try again with a smaller file.',
    };
    return (
        <div className='error-background'>
            <div className='error-popup'>
                <div className="card text-center">
                    <div className="card-header mt-1">
                        <h3>An error occured 😢</h3>
                    </div>
                    <div className="card-body">{errorTypes[message]}</div>
                    <div className="card-buttons">
                        <button className="btn btn-primary btn-error" onClick={handleClose}>
                            I understand
                        </button>
                        {showReloadButton && (
                            <button className="btn btn-outline-secondary btn-error" onClick={handleReload}>
                            Reload
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ErrorPopup;
