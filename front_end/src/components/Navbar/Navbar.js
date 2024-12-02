import React, { useState, useEffect, useContext } from 'react';
import { Navbar, Container, Nav } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import logo from '../../logo.png';
import './style.css';
import ChatContext from '../context/ChatContext';

const CustomNavbar = ({ darkMode, toggleDarkMode, footer, fileUploader, sectionSwitchBar }) => {
  const [isMobile, setIsMobile] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const { state } = useContext(ChatContext);
  const session_id = state.sessionId;

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
    if (isMobile) {
      setExpanded(true);
    }
  }, [isMobile]);


  useEffect(() => {
    if (session_id === state.sessionId) {
      setExpanded(false);
    }
  }, [session_id]);

  return (
    <Navbar
      variant={darkMode ? 'dark' : 'light'}
      expand="md"
      fixed="top"
      expanded={expanded}
      onToggle={(expanded) => setExpanded(expanded)}
      className={`${expanded ? 'navbar-expanded ' : ''}
                  ${darkMode ? 'dark-mode-navbar' : 'light-mode-navbar'}`}
    >
      <Container className="d-flex justify-content-between align-items-center">
        <Navbar.Brand className="d-flex align-items-center">
          <img src={logo} width={24} height={24} alt='website logo' className="mx-2" />
          <div>ChatDocument</div>
        </Navbar.Brand>

        <Nav className="d-flex align-items-center d-none d-md-flex">
          <Nav.Link onClick={toggleDarkMode} className="me-3" data-toggle="tooltip" title="Select light/dark mode">
            {darkMode ? <><i className="bi bi-moon"></i> Light</> : <><i className="bi bi-moon-fill"></i> Dark</>}
          </Nav.Link>
        </Nav>

        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav" className="navbar-collapse-overlay">
          <Nav className="ms-auto d-md-none mt-2 mb-3 container">
            <Nav.Link onClick={toggleDarkMode} className="me-3">
              {darkMode ? <><i className="bi bi-moon"></i> Light</> : <><i className="bi bi-moon-fill"></i> Dark</>}
            </Nav.Link>
          </Nav>
          <Nav className="ms-auto d-md-none mt-2 mb-3">
            {fileUploader && (
              <>{fileUploader}</>
            )}
            {sectionSwitchBar && (
              <>{sectionSwitchBar}</>
            )}
            {footer && (
              <>{footer}</>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;
