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
          <th>Страница лота</th>
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
