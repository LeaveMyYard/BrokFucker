import React, { useState, createContext } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useLocation,
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
import ArchivePage from "./ArchivePage";

export const lotsPageTypesEnum = {
  UNAPPROVED: "UNAPPROVED",
  VERIFICATION: "VERIFICATION",
  GUARANTEE: "GUARANTEE",
  ARCHIVE: "ARCHIVE",
};

export const LotsPageTypeContext = createContext(lotsPageTypesEnum.UNAPPROVED);

const Sidebar = (props) => {
  const location = useLocation();
  const [lotsPageTypes, setLotsPageTypes] = useState(
    location.pathname.includes("/lots/unapproved")
      ? lotsPageTypesEnum.UNAPPROVED
      : location.pathname.includes("/guarantee")
      ? lotsPageTypesEnum.GUARANTEE
      : location.pathname.includes("/verification")
      ? lotsPageTypesEnum.VERIFICATION
      : location.pathname.includes("/lots/archive")
      ? lotsPageTypesEnum.ARCHIVE
      : undefined
  );
  const history = useHistory();
  const handleLogout = () => {
    AuthService.logout();
    history.push("/login");
  };
  const user = localStorage.getItem("role");

  const changeLotsPageType = (lpt) => {
    setLotsPageTypes(lpt);
  };

  return (
    <LotsPageTypeContext.Provider value={lotsPageTypes}>
      {user === "admin" ? (
        <Router>
          <div className="sidebar_container">
            <div className="sidebar">
              <div className="sidebar-header">
                <img className="sidebar__logo" src={logo} alt="BrokAdmin"></img>
              </div>
              <Link
                onClick={() => changeLotsPageType(lotsPageTypesEnum.UNAPPROVED)}
                to="/admin/dashboard/lots/unapproved"
              >
                Лоты
              </Link>
              <Link
                onClick={() => changeLotsPageType(lotsPageTypesEnum.ARCHIVE)}
                to="/admin/dashboard/lots/archive"
              >
                Архивные <p>лоты</p>
              </Link>
              <Link to="/admin/dashboard/moderators">Модераторы</Link>
              <Link
                onClick={() => changeLotsPageType(lotsPageTypesEnum.GUARANTEE)}
                to="/admin/dashboard/guarantee"
              >
                Гарантия
              </Link>
              <Link
                onClick={() =>
                  changeLotsPageType(lotsPageTypesEnum.VERIFICATION)
                }
                to="/admin/dashboard/verification"
              >
                Обеспечение
              </Link>
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
                exact
                path="/admin/dashboard/lots/archive"
                component={ArchivePage}
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
              <Link
                onClick={() => changeLotsPageType(lotsPageTypesEnum.UNAPPROVED)}
                to="/admin/dashboard/lots/unapproved"
              >
                Лоты
              </Link>
              <Link
                onClick={() => changeLotsPageType(lotsPageTypesEnum.ARCHIVE)}
                to="/admin/dashboard/lots/archive"
              >
                Архивные <p>лоты</p>
              </Link>
              <Link
                onClick={() => changeLotsPageType(lotsPageTypesEnum.GUARANTEE)}
                to="/admin/dashboard/guarantee"
              >
                Гарантия
              </Link>
              <Link
                onClick={() =>
                  changeLotsPageType(lotsPageTypesEnum.VERIFICATION)
                }
                to="/admin/dashboard/verification"
              >
                Обеспечение
              </Link>
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
                exact
                path="/admin/dashboard/lots/archive"
                component={ArchivePage}
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
      )}
    </LotsPageTypeContext.Provider>
  );
};

export default Sidebar;
