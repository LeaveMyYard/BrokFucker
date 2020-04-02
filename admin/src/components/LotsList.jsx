import React from "react";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import PropTypes from "prop-types";

function dateFix(date) {
  let givenDate = new Date(date.replace(/ /g, "T"));
  let day = givenDate.getDate();
  let month = givenDate.getMonth();
  let year = givenDate.getFullYear();
  return `${day}.${month + 1}.${year}`;
}

export function LotsList({ list, refreshList }) {
  const onLotApprove = async lot => {
    try {
      // ... await api request
    } catch (error) {
    } finally {
      await refreshList();
    }
  };

  const onLotRemove = async lot => {
    try {
      // ... await api request
    } catch (error) {
    } finally {
      await refreshList();
    }
  };

  return !list.length ? (
    "No lots found"
  ) : (
    <table id="lotTable">
      <tr>
        <th>Дата</th>
        <th>Название лота</th>
        <th>Имя</th>
        <th>Сумма</th>
        <th>Валюта</th>
        <th>Срок, мес.</th>
        <th>Метод погашения</th>
        <th>Обеспечение</th>
        <th>Ставка годовых</th>
        <th>Форма кредитирования</th>
        <th>Проверенное Обеспечение</th>
        <th>Гарантия клуба</th>
        <th>Подтвердить</th>
      </tr>
      {list.map(item => (
        <tr>
          <td>{dateFix(item.date)}</td>
          <td>{item.name}</td>
          <td>{item.user}</td>
          <td>{item.amount}</td>
          <td>{item.currency}</td>
          <td>{item.term}</td>
          <td>{item.return_way}</td>
          <td>{item.security}</td>
          <td>{item.percentage}</td>
          <td>{item.form}</td>
          <td>{item.security_checked ? "Да" : "Нет"}</td>
          <td>{item.guarantee_percentage}</td>
          <td>
            <button onClick={() => onLotApprove(item)}>Approve</button>
          </td>
          <td>
            <button onClick={() => onLotRemove(item)}>Remove</button>
          </td>
        </tr>
      ))}
    </table>
  );
}

LotsList.propTypes = {
  list: PropTypes.arrayOf(PropTypes.object).isRequired
};

LotsList.defaultProps = {
  list: []
};
