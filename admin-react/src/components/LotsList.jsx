import React, { useContext } from "react";
import PropTypes from "prop-types";
import authService from "../services/Auth";
import Translate from "../services/Translate";
import { URL } from "../constants";
import { LotsPageTypeContext, lotsPageTypesEnum } from "./Sidebar";
import Modal from "./Modal";
import LotsItem from "./LotsItem";

export function LotsList({
  list,
  refreshList,

  onApprove,
  onRemove,
  isGuaranteeList,
  show,
}) {
  const lotsPageType = useContext(LotsPageTypeContext);

  return !list.length ? (
    <h1>По данному запросу нет лотов.</h1>
  ) : (
    <table className="lot-table" id="lotTable">
      <thead>
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
          {lotsPageType === lotsPageTypesEnum.UNAPPROVED && (
            <th>Подтвердить</th>
          )}
        </tr>
      </thead>
      <tbody>
        {list.map((lot, lotIndex) => (
          <LotsItem key={lot.id} lot={lot} refreshList={refreshList} />
        ))}
        {/* {list.map((lot, lotIndex) => (
          <tr key={lot.id}>
            <td>{dateFix(lot.date)}</td>
            <td>{lot.name}</td>
            <td>{lot.user}</td>
            <td>{lot.amount}</td>
            <td>{lot.currency}</td>
            <td>{lot.term}</td>
            <td>{Translate(lot.return_way)}</td>
            <td>{lot.security}</td>
            <td>{lot.percentage}</td>
            <td>{Translate(lot.form)}</td>
            <td>{lot.security_checked ? "Да" : "Нет"}</td>
            <td>
              {isGuaranteeList ? (
                <input
                  type="number"
                  value={lot.guarantee_percentage}
                  onChange={(event) =>
                    onLotGuaranteeChange(event, lot, lotIndex)
                  }
                ></input>
              ) : (
                lot.guarantee_percentage
              )}
            </td>
            <td>
              <button onClick={() => onApprove(lot)}>Approve</button>
              <button onClick={() => onRemove(lot)}>Remove</button>
            </td>
          </tr>
        ))} */}
      </tbody>
      {/* <Modal show={show} /> */}
    </table>
  );
}

LotsList.propTypes = {
  list: PropTypes.arrayOf(PropTypes.object).isRequired,
};

LotsList.defaultProps = {
  list: [],
};
