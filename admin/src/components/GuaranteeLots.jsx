import React, { useState, useEffect } from "react";

import { LotsList } from "./LotsList";
import lotsService from "../services/Lots";

const GuaranteePage = () => {
  const [loading, setLoading] = useState(true);
  const [lots, setLots] = useState();

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
        <LotsList list={lots} refreshList={refreshList} />
      )}
    </div>
  );
};

export default GuaranteePage;
