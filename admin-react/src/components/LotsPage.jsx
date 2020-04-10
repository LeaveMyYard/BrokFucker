import React, { useState, useEffect } from "react";

import { LotsList } from "./LotsList";
import { URL } from "../constants";
import lotsService from "../services/Lots";
import authService from "../services/Auth";

const LotsPage = () => {
  const [loading, setLoading] = useState(true);
  const [lots, setLots] = useState();

  // const onLotApprove = async (lot) => {
  //   try {
  //     const authToken = authService.getAuthToken();

  //     const response = await fetch(URL + `lots/${lot.id}/approve`, {
  //       method: "PUT",
  //       headers: {
  //         Authorization: `Basic ${authToken}`,
  //         "Content-Type": "application/json",
  //       },
  //     });

  //     if (!response.ok) {
  //       throw new Error("Unsuccessfull response");
  //     }

  //     return await response.json();
  //   } catch (error) {
  //   } finally {
  //     await refreshList();
  //   }
  // };

  // const onLotRemove = async (lot) => {
  //   try {
  //     const authToken = authService.getAuthToken();
  //     // const reason = document.getElementById("declineReason").value;
  //     const reason = { reason: "Лот не подходит под стандарты." };
  //     const response = await fetch(URL + `lots/unapproved/${lot.id}`, {
  //       method: "DELETE",
  //       headers: {
  //         Authorization: `Basic ${authToken}`,
  //         "Content-Type": "application/json",
  //       },
  //       body: JSON.stringify(reason),
  //     });

  //     if (!response.ok) {
  //       throw new Error("Unsuccessfull response");
  //     }

  //     return await response.json();
  //   } catch (error) {
  //   } finally {
  //     await refreshList();
  //   }
  // };

  const refreshList = async () => {
    setLoading(true);

    try {
      const lots = await lotsService.getLots();
      setLots(lots);
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
      ) : (
        <div>
          <h1 className="heading">Лоты</h1>
          <LotsList list={lots} refreshList={refreshList} />
        </div>
      )}
    </div>
  );
};

export default LotsPage;
