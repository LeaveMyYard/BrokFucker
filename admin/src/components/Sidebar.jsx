import React from "react";
import "../Admin.css";

const Sidebar = user => {
  return user === "admin" ? (
    <ul>
      <li>
        <div className="logoAdmin"></div>
      </li>
      <li>Неподтвержденные Лоты</li>
      <li>Модераторы</li>
    </ul>
  ) : (
    <ul>
      <li>
        <div className="logoAdmin"></div>
      </li>
      <li>Неподтвержденные Лоты</li>
    </ul>
  );
};

export default Sidebar;
