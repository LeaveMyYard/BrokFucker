import React from "react";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import LotsPage from "./LotsPage";
import ModeratorsPage from "./ModeratorsPage";
import "../Admin.css";

/**
 * TODO: restruct all `Route`s and `history` usage as following
 * https://reacttraining.com/react-router/web/example/nesting
 */
const Sidebar = (user) => {
  return user === "admin" ? (
    <Router>
      <ul>
        <li>
          <div className="logoAdmin"></div>
        </li>
        <li>
          <Link to="/lots/unapproved">Неподтвержденные Лоты</Link>
        </li>
        <li>
          <Link to="/moderators">Модераторы</Link>
        </li>
      </ul>
      <Switch>
        <Route exact path="/lots/unapproved" component={LotsPage}></Route>
        <Route path="/moderators" component={ModeratorsPage}></Route>
      </Switch>
    </Router>
  ) : (
    <Router>
      <ul>
        <li>
          <div className="logoAdmin"></div>
        </li>
        <li>
          <Link to="/lots/unapproved">Неподтвержденные Лоты</Link>
        </li>
      </ul>
      <Switch>
        <Route exact path="/lots/unapproved" component={LotsPage}></Route>
      </Switch>
    </Router>
  );
};

export default Sidebar;
