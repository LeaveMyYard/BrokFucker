import React from "react";
import {
  BrowserRouter,
  Route,
  Switch,
  Redirect,
  useHistory,
} from "react-router-dom";

import PrivateRoute from "./components/PrivateRoute";
import IndexPage from "./components/IndexPage";
import LoginPage from "./components/LoginPage";
import Sidebar from "./components/Sidebar";
import LotsPage from "./components/LotsPage";
import { BASE_HREF } from "./constants";

function App() {
  const user = localStorage.getItem("role");

  return (
    <BrowserRouter basename={BASE_HREF}>
      <Switch>
        <PrivateRoute path="/dashboard">
          <Sidebar />
        </PrivateRoute>
        <Route exact path="/login">
          <LoginPage />
        </Route>
        <Route path="/">
          <IndexPage />
        </Route>
      </Switch>
    </BrowserRouter>
  );
}

export default App;
