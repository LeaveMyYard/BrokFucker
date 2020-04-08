import React from "react";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import LotsPage from "./LotsPage";
import VerificationLots from "./VerificationLots";
import GuaranteeLots from "./GuaranteeLots";
import ModeratorsPage from "./ModeratorsPage";
import AuthService from "../services/Auth";
import "../Admin.css";
import logo from "../letter-a.png";
/**
 * TODO: restruct all `Route`s and `history` usage as following
 * https://reacttraining.com/react-router/web/example/nesting
 */

const Sidebar = (props) => {
  const handleLogout = () => {
    AuthService.logout();
    window.location.reload();
  };
  const user = localStorage.getItem("role");

  return user === "admin" ? (
    <Router>
      <div className="sidebar_container">
        <div className="sidebar">
          <div className="sidebar-header">
            <img className="sidebar__logo" src={logo} alt="BrokAdmin"></img>
          </div>
          <Link to="/admin/dashboard/lots/unapproved">Лоты</Link>
          <Link to="/admin/dashboard/moderators">Модераторы</Link>
          <Link to="/admin/dashboard/guarantee">Гарантия</Link>
          <Link to="/admin/dashboard/verification">Обеспечение</Link>
          <button onClick={handleLogout}>Выйти</button>
        </div>
        <Switch>
          <Route
            exact
            path="/admin/dashboard/lots/unapproved"
            component={LotsPage}
          ></Route>
          <Route
            path="/admin/dashboard/moderators"
            component={ModeratorsPage}
          ></Route>
          <Route
            path="/admin/dashboard/guarantee"
            component={GuaranteeLots}
          ></Route>
          <Route
            path="/admin/dashboard/verification"
            component={VerificationLots}
          ></Route>
        </Switch>
      </div>
    </Router>
  ) : (
    <Router>
      <div className="sidebar_container">
        <div className="sidebar">
          <div className="sidebar-header">
            <img className="sidebar__logo" src={logo} alt="BrokAdmin"></img>
          </div>
          <Link to="/admin/dashboard/lots/unapproved">Лоты</Link>
          <Link to="/admin/dashboard/guarantee">Гарантия</Link>
          <Link to="/admin/dashboard/verification">Обеспечение</Link>
          <button onClick={handleLogout}>Выйти</button>
        </div>
        <Switch>
          <Route
            exact
            path="/admin/dashboard/lots/unapproved"
            component={LotsPage}
          ></Route>
          <Route
            path="/admin/dashboard/guarantee"
            component={GuaranteeLots}
          ></Route>
          <Route
            path="/admin/dashboard/verification"
            component={VerificationLots}
          ></Route>
        </Switch>
      </div>
    </Router>
  );
};

export default Sidebar;
