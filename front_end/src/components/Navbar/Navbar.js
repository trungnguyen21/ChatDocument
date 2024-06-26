import React, { useState, useEffect } from 'react';
import { Navbar, Container, Nav } from 'react-bootstrap';
import { useContext } from 'react';
import FileContext from '../Context/FileContext';
import ChatContext from '../Context/ChatContext';
import 'bootstrap/dist/css/bootstrap.min.css';
import logo from '../../logo.png';
import './style.css';

const CustomNavbar = ({ darkMode, toggleDarkMode, flushRedis, fileUploader, sectionSwitchBar }) => {
  const [isMobile, setIsMobile] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const { fileUploaded } = useContext(FileContext);
  const { dispatch } = useContext(ChatContext);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    handleResize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  useEffect(() => {
    setExpanded(false);
  }, [fileUploaded, dispatch]);

  useEffect(() => {
    if (isMobile) {
      setExpanded(true);
    }
  }, [isMobile]);

  return (
    <Navbar
      bg={darkMode ? 'dark' : 'light'}
      variant={darkMode ? 'dark' : 'light'}
      expand="lg"
      fixed="top"
      expanded={expanded}
      onToggle={(expanded) => setExpanded(expanded)}
      className={expanded ? 'navbar-expanded' : ''}
    >
      <Container>
        <Navbar.Brand className="d-flex align-items-center">
          <img src={logo} width={24} height={24} alt='website logo' className="mx-2"></img>
          <div>ChatDocument</div>
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav" className="navbar-collapse-overlay">
          <div className="container">
          <Nav className="ms-auto">
              <Nav.Link onClick={toggleDarkMode} className="me-3">
                {darkMode ? <><i className="bi bi-moon"></i> Light</> : <><i className="bi bi-moon-fill"></i> Dark</>}
              </Nav.Link>
              <Nav.Link onClick={flushRedis} className="me-3">
                {darkMode ? <><i className="bi bi-trash"></i> Flush</> : <><i className="bi bi-trash-fill"></i> Flush</>}
              </Nav.Link>

              <div className="container d-md-none mt-2 mb-3 size-upload">
                {fileUploader && (
                  <>{fileUploader}</>
                )}
                {sectionSwitchBar && (
                  <>{sectionSwitchBar}</>
                )}
              </div>
            </Nav>
          </div>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;
