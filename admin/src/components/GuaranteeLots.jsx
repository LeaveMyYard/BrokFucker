import React, { useState, useEffect } from "react";

import { LotsList } from "./LotsList";
import { URL } from "../constants";
import lotsService from "../services/Lots";
import authService from "../services/Auth";

const GuaranteeLots = () => {
  const [loading, setLoading] = useState(true);
  const [lots, setLots] = useState();

  const onGuaranteeApprove = async (lot) => {
    try {
      const authToken = authService.getAuthToken();
      const guarantee = {
        guarantee: document.querySelector("#guaranteeValue").value,
      };
      const response = await fetch(URL + `lots/${lot.id}/guarantee`, {
        method: "PUT",
        headers: {
          Authorization: `Basic ${authToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(guarantee),
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

  const onGuaranteeRemove = async (lot) => {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + `lots/${lot.id}/guarantee`, {
        method: "DELETE",
        headers: {
          Authorization: `Basic ${authToken}`,
          "Content-Type": "application/json",
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
      const lots = await lotsService.guaranteeLots();
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
          <h1 className="heading">Гарантия</h1>
          <LotsList
            list={lots}
            refreshList={refreshList}
            onApprove={onGuaranteeApprove}
            onRemove={onGuaranteeRemove}
            isGuaranteeList={true}
          />
        </div>
      )}
    </div>
  );
};

export default GuaranteeLots;
