import React, { useState, useEffect } from "react";

import { LotsList } from "./LotsList";
import { URL } from "../constants";
import lotsService from "../services/Lots";
import authService from "../services/Auth";

const LotsPage = () => {
  const [loading, setLoading] = useState(true);
  const [lots, setLots] = useState();

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
