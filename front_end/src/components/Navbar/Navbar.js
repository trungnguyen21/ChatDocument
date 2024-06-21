import React from 'react';
import { Navbar, Container, Nav, NavDropdown } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

const CustomNavbar = ({ darkMode, toggleDarkMode, flushRedis, fileUploader, sectionSwitchBar }) => {
  return (
    <Navbar bg={darkMode ? 'dark' : 'light'} variant={darkMode ? 'dark' : 'light'} expand="lg" fixed="top">
      <Container>
        <Navbar.Brand href="#home">Document Chat App</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            <Nav.Link onClick={toggleDarkMode} className="me-3">
              {darkMode ? <><i className="bi bi-moon"></i> Light Mode</> : <><i className="bi bi-moon-fill"></i> Dark Mode</>}
            </Nav.Link>
            <Nav.Link onClick={flushRedis} className="me-3">
              {darkMode ? <><i className="bi bi-trash"></i> Flush</> : <><i className="bi bi-trash-fill"></i> Flush</>}
            </Nav.Link>

            <Nav.Link className="d-md-none container">
              {fileUploader && (
                <NavDropdown.Item>
                  {fileUploader}
                </NavDropdown.Item>
              )}
              {sectionSwitchBar && (
                <NavDropdown.Item>
                  {sectionSwitchBar}
                </NavDropdown.Item>
              )}
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;
