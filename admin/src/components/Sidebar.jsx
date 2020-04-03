import React from "react";
import { Router, Switch, Route, Link } from "react-router-dom";
import { LotsPage } from "LotsPage";
import "../Admin.css";

const Sidebar = (user) => {
  return user === "admin" ? (
    <Router>
      <ul>
        <li>
          <Link to="/">
            <div className="logoAdmin"></div>
          </Link>
        </li>
        <li>
          <Link to="/lots/unapproved">Неподтвержденные Лоты</Link>
        </li>
        <li>
          <Link to="/moderators">Модераторы</Link>
        </li>
      </ul>
      <Switch>
        <Route path="/lots/unapproved">
          <LotsPage />
        </Route>
        <Route path="/moderators">
          <Moderators />
        </Route>
      </Switch>
    </Router>
  ) : (
    <Router>
      <ul>
        <li>
          <Link to="/">
            <div className="logoAdmin"></div>
          </Link>
        </li>
        <li>
          <Link to="/lots/unapproved">Неподтвержденные Лоты</Link>
        </li>
      </ul>
      <Switch>
        <Route path="/lots/unapproved">
          <LotsPage />
        </Route>
      </Switch>
    </Router>
  );
};

export default Sidebar;
