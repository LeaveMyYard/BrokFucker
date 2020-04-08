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

// TODO: in Auth change 'user' to 'admin' when ready
// TODO: change 'user' to 'admin' in Sidebar return
function App() {
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
