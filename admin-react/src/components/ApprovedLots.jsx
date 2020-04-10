import React, { useState, useEffect } from "react";

import Translate from "../services/Translate";
import { URL } from "../constants";
import lotsService from "../services/Lots";
import authService from "../services/Auth";

const ApprovedLots = () => {
  const [loading, setLoading] = useState(true);
  const [lots, setLots] = useState();

  const onSubscriptionDecline = async (id) => {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + `lots/subscription/${id}/unapprove`, {
        method: "GET",
        headers: {
          Authorization: `Basic ${authToken}`,
        },
      });

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }

      return await response.json();
    } catch (error) {
    } finally {
      await refreshList();
    }
  };

  const refreshList = async () => {
    setLoading(true);

    try {
      const lots = await lotsService.getApprovedSubscriptions();
      setLots(lots);
      console.log(lots);
    } catch (error) {
      setLots();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshList();
  }, []);

  return (
    <div className="lots-page">
      {loading ? (
        <h1 className="heading">Loading...</h1>
      ) : lots.lots.length !== 0 ? (
        <div>
          <h1 className="heading">Подтвержденные подписки</h1>
          <table className="lot-table">
            <tr>
              <th>№</th>
              {/* <th>Страница</th> */}
              <th>Сообщение</th>
              <th>Тип</th>
              <th>Подписчик</th>
              <th>Убрать подписку</th>
            </tr>
            {lots.lots.map((lot, index) => (
              <tr>
                <td>{index + 1}</td>
                {/* <td>
                  <a href={`lot.html?id=${lot.lot}`}>Страница лота</a>
                </td> */}
                <td>{lot.message ? lot.message : "Не указано"}</td>
                <td>{Translate(lot.type)}</td>
                <td>{lot.user}</td>
                <td>
                  <button onClick={() => onSubscriptionDecline(lot.id)}>
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </table>
        </div>
      ) : (
        <h2>Не найдено лотов по запросу</h2>
      )}
    </div>
  );
};

export default ApprovedLots;
