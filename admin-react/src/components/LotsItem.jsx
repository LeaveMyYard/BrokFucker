import React, { useState, useContext } from "react";

import lotsService from "../services/Lots";
import translateService from "../services/Translate";
import dateFix from "../utils/dateFix";
import { LotsPageTypeContext, lotsPageTypesEnum } from "./Sidebar";

export default function LotsItem({
  lot,
  refreshList: refreshListParent,
  lotIndex,
}) {
  const [guarantee, setGuarantee] = useState(lot.guarantee_percentage);
  const lotsPageType = useContext(LotsPageTypeContext);

  const onApprove = async () => {
    try {
      await lotsService.approve(lot);
    } catch (error) {
      console.error(error);
    } finally {
      await refreshListParent();
    }
  };

  const onRemove = async () => {
    try {
      await lotsService.remove(lot);
    } catch (error) {
      console.error(error);
    } finally {
      await refreshListParent();
    }
  };

  const onGuaranteeSet = async () => {
    try {
      await lotsService.guaranteeApprove(lot);
    } catch (error) {
      console.error(error);
    } finally {
      await refreshListParent();
    }
  };

  const onGuaranteeRemove = async () => {
    try {
      lot.guarantee_percentage = 0;

      await lotsService.guaranteeRemove(lot);
    } catch (error) {
      console.error(error);
    } finally {
      await refreshListParent();
    }
  };

  const onSecurityCheckApprove = async () => {
    try {
      await lotsService.securityCheckApprove(lot);
    } catch (error) {
      console.error(error);
    } finally {
      await refreshListParent();
    }
  };

  const onSecurityCheckDecline = async () => {
    try {
      await lotsService.securityCheckDecline(lot);
    } catch (error) {
      console.error(error);
    } finally {
      await refreshListParent();
    }
  };

  const onGuaranteeChange = (event, lot, lotIndex) => {
    let result = parseInt(event.target.value);

    if (isNaN(result)) {
      result = undefined;
    }

    lot.guarantee_percentage = result;
    setGuarantee(lot.guarantee_percentage);
  };

  return (
    <tr key={lot.id}>
      <td>{dateFix(lot.date)}</td>
      <td>{lot.name}</td>
      <td>
        <a href={`/lot.html?id=${lot.id}`}>Страница лота</a>
      </td>
      {lotsPageType === lotsPageTypesEnum.ARCHIVE && <td>Archive Link</td>}
      <td>{lot.user}</td>
      <td>{lot.amount}</td>
      <td>{lot.currency}</td>
      <td>{lot.term}</td>
      <td>{translateService(lot.return_way)}</td>
      <td>{lot.security}</td>
      <td>{lot.percentage}</td>
      <td>{translateService(lot.form)}</td>
      <td>
        {lotsPageType === lotsPageTypesEnum.VERIFICATION ? (
          <div>
            <button onClick={() => onSecurityCheckApprove(lot)}>Approve</button>
            <button onClick={() => onSecurityCheckDecline(lot)}>Decline</button>
          </div>
        ) : lot.security_checked ? (
          "Да"
        ) : (
          "Нет"
        )}
      </td>
      <td>
        {lotsPageType === lotsPageTypesEnum.GUARANTEE ? (
          <div>
            <input
              type="number"
              min="0"
              max="100"
              value={guarantee}
              onChange={(event) => onGuaranteeChange(event, lot, lotIndex)}
            ></input>
            <div>
              <button onClick={() => onGuaranteeSet(lot)}>Set</button>
              <button onClick={() => onGuaranteeRemove(lot)}>Remove</button>
            </div>
          </div>
        ) : (
          lot.guarantee_percentage
        )}
      </td>
      {lotsPageType === lotsPageTypesEnum.UNAPPROVED && (
        <td>
          <button onClick={() => onApprove(lot)}>Approve</button>
          <button onClick={() => onRemove(lot)}>Remove</button>
        </td>
      )}
    </tr>
  );
}
