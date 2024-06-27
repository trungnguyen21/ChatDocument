import React, { useState, useEffect } from 'react';
import { Navbar, Container, Nav } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import logo from '../../logo.png';
import './style.css';

const CustomNavbar = ({ darkMode, toggleDarkMode, flushRedis, fileUploader, sectionSwitchBar }) => {
  const [isMobile, setIsMobile] = useState(false);
  const [expanded, setExpanded] = useState(false);

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
      <Container className="d-flex justify-content-between align-items-center">
        <Navbar.Brand className="d-flex align-items-center">
          <img src={logo} width={24} height={24} alt='website logo' className="mx-2" />
          <div>ChatDoc</div>
        </Navbar.Brand>
        <Nav className="d-flex align-items-center">
          <Nav.Link onClick={toggleDarkMode} className="me-3">
            {darkMode ? <><i className="bi bi-moon"></i> Light</> : <><i className="bi bi-moon-fill"></i> Dark</>}
          </Nav.Link>
          <Nav.Link onClick={flushRedis} className="me-3">
            {darkMode ? <><i className="bi bi-trash"></i> Flush</> : <><i className="bi bi-trash-fill"></i> Flush</>}
          </Nav.Link>
        </Nav>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav" className="navbar-collapse-overlay">
          <Nav className="ms-auto d-md-none mt-2 mb-3 size-upload">
            {fileUploader && (
              <>{fileUploader}</>
            )}
            {sectionSwitchBar && (
              <>{sectionSwitchBar}</>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;
