import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useHistory,
} from "react-router-dom";
import LotsPage from "./LotsPage";
import VerificationLots from "./VerificationLots";
import GuaranteeLots from "./GuaranteeLots";
import ModeratorsPage from "./ModeratorsPage";
import AuthService from "../services/Auth";
import "../Admin.css";
import logo from "../letter-a.png";
import ApprovedLots from "./ApprovedLots";
import UnapprovedLots from "./UnapprovedLots";

const Sidebar = (props) => {
  const history = useHistory();
  const handleLogout = () => {
    AuthService.logout();
    history.push("/login");
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
          <Link to="/admin/dashboard/subscriptions/unapproved">
            Неподтвержденные<p>Подписки</p>
          </Link>
          <Link to="/admin/dashboard/subscriptions/approved">
            Подтвержденные<p>Подписки</p>
          </Link>
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
          <Route
            path="/admin/dashboard/subscriptions/approved"
            component={ApprovedLots}
          ></Route>
          <Route
            path="/admin/dashboard/subscriptions/unapproved"
            component={UnapprovedLots}
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
          <Link to="/admin/dashboard/subscriptions/unapproved">
            Неподтвержденные<p>Подписки</p>
          </Link>
          <Link to="/admin/dashboard/subscriptions/approved">
            Подтвержденные<p>Подписки</p>
          </Link>
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
          <Route
            path="/admin/dashboard/subscriptions/approved"
            component={ApprovedLots}
          ></Route>
          <Route
            path="/admin/dashboard/subscriptions/unapproved"
            component={UnapprovedLots}
          ></Route>
        </Switch>
      </div>
    </Router>
  );
};

export default Sidebar;