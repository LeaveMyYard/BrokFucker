import React from "react";
import LoginForm from "LoginForm";

const LoginPage = props => {
  const submit = user =>
    api.users
      .login(user)
      .then(token => props.login(token))
      .then(() => props.history.push("/films"));

  return (
    <div>
      <div>
        <LoginForm submit={submit} />
      </div>
    </div>
  );
};

export default LoginPage;
