import React, { useState, useEffect } from "react";

import { LotsList } from "./LotsList";
import { URL } from "../constants";
import lotsService from "../services/Lots";
import authService from "../services/Auth";

const VerificationLots = () => {
  const [loading, setLoading] = useState(true);
  const [lots, setLots] = useState();

  const onVerifyApprove = async (lot) => {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + `lots/${lot.id}/approve`, {
        method: "PUT",
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

  const onVerifyRemove = async (lot) => {
    try {
      const authToken = authService.getAuthToken();

      const response = await fetch(URL + `lots/unapproved/${lot.id}`, {
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
      const lots = await lotsService.verificationLots();
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
          <h1 className="heading">Обеспечение</h1>
          <LotsList
            list={lots}
            refreshList={refreshList}
            onApprove={onVerifyApprove}
            onRemove={onVerifyRemove}
          />
        </div>
      )}
    </div>
  );
};

export default VerificationLots;
