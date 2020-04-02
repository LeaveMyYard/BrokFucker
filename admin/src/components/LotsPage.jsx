import React, { useState, useEffect } from "react";
import { LotsList } from "./LotsList";
import { getLots } from "../actions/getLots";

const createMockLots = () => {
  const mockLot = {
    id: 1,
    date: "date",
    name: "testname",
    user: "test@gmail.com",
    amount: 12345,
    currency: "USD",
    term: 0,
    return_way: 2,
    security: "house",
    percentage: "0",
    form: 1,
    security_checked: false,
    guarantee_percentage: 90
  };

  let it = 1;

  const mockLots = Array(10)
    .fill(null)
    .map(() => {
      const mockItem = { ...mockLot };

      mockItem.id += it;
      mockItem.date += it;
      mockItem.name += it;
      mockItem.user += it;
      mockItem.amount += it;
      mockItem.currency += it;
      mockItem.term += it;
      mockItem.return_way += it;
      mockItem.security += it;
      mockItem.percentage += it;
      mockItem.form += it;
      mockItem.security_checked += it;
      mockItem.guarantee_percentage += it;

      it++;

      return mockItem;
    });

  return mockLots;
};

function LotsPage() {
  const [loading, setLoading] = useState(true);
  const [lots, setLots] = useState();

  const refreshList = async () => {
    setLoading(true);

    try {
      const lots = await getLots();

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
    <div className="App">
      {loading ? (
        "Loading..."
      ) : (
        <LotsList list={lots} refreshList={refreshList} />
      )}
    </div>
  );
}

export default LotsPage;
