import React from "react";
import { Link, NavLink } from "react-router-dom";
import { Navbar, Nav, Container } from "react-bootstrap";
import './index.css'

export default function NavigationBar() {
  return (
    <Navbar expand="lg" className="custom-navbar">
      <Container className="cont">
        {/* Logo */}
        <Navbar.Brand as={Link} to="/">
          <img src="https://webfiles.amrita.edu/2024/04/ZvmNQEuB-amrita-vishwa-vidyapeetham-university-logo-white-version.svg" alt="Amrita Logo" className="nav-logo" />
        </Navbar.Brand>

        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            <NavLink exact to="https://www.amrita.edu/" className="nav-link" activeClassName="active">Home</NavLink>
            <NavLink to="https://www.amrita.edu/about/" className="nav-link" activeClassName="active">About</NavLink>
            <NavLink to="https://www.amrita.edu/academics/" className="nav-link" activeClassName="active">Academics</NavLink>
            <NavLink to="https://www.amrita.edu/research/" className="nav-link" activeClassName="active">Research</NavLink>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}
