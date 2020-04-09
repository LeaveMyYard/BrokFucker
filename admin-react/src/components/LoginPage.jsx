import React, { useState, useEffect } from "react";
import { Redirect, useHistory } from "react-router-dom";
import { Button, FormGroup, FormControl, FormLabel } from "react-bootstrap";

import "../Login.css";
import authService from "../services/Auth";

export default function Login(props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const history = useHistory();

  if (authService.isAuthenticated()) {
    return <Redirect to="/dashboard" />;
  }

  function validateForm() {
    return email.length > 0 && password.length > 7;
  }

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      await authService.login({ email, password });
      history.push("/dashboard/lots/unapproved");
    } catch (error) {
      console.error(error);
      setError("У вас нет прав для входа.");
    }
  }

  return (
    <div className="Login">
      <h1 className="login_heading">Login</h1>
      <form onSubmit={handleSubmit}>
        <FormGroup controlId="email">
          <FormLabel>Email</FormLabel>
          <FormControl
            autoFocus
            type="text"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </FormGroup>
        <FormGroup controlId="password">
          <FormLabel>Password</FormLabel>
          <FormControl
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
          />
        </FormGroup>
        <Button
          className="login-btn"
          block
          disabled={!validateForm()}
          type="submit"
        >
          Login
        </Button>
      </form>
      {error && <p className="login_error-msg">{error}</p>}
    </div>
  );
}
