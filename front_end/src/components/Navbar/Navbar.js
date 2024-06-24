import React from 'react';
import { Navbar, Container, Nav } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import logo from '../../logo.png';
import './style.css';

const CustomNavbar = ({ darkMode, toggleDarkMode, flushRedis, fileUploader, sectionSwitchBar }) => {
  return (
    <Navbar bg={darkMode ? 'dark' : 'light'} variant={darkMode ? 'dark' : 'light'} expand="lg" fixed="top">
      <Container>
        <Navbar.Brand className="d-flex align-items-center">
          <img src={logo} width={24} height={24} alt='website logo' className="mx-2"></img>
          <div>ChatDoc</div>
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav" className="collapse">
          <Nav className="ms-auto">
            <Nav.Link onClick={toggleDarkMode} className="me-3">
              {darkMode ? <><i className="bi bi-moon"></i> Light</> : <><i className="bi bi-moon-fill"></i> Dark</>}
            </Nav.Link>
            <Nav.Link onClick={flushRedis} className="me-3">
              {darkMode ? <><i className="bi bi-trash"></i> Flush</> : <><i className="bi bi-trash-fill"></i> Flush</>}
            </Nav.Link>

            <div className="container d-md-none mt-2 mb-2">
              {fileUploader && (
                <>{fileUploader}</>
              )}
              {sectionSwitchBar && (
                <>{sectionSwitchBar}</>
              )}
            </div>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;
