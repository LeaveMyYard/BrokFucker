import React from "react";
import LotsPage from "./components/LotsPage";
import Sidebar from "./components/Sidebar";

const App = () => {
  return (
    <div className="App">
      <Sidebar props={user}></Sidebar>
      <LotsPage></LotsPage>
    </div>
  );
};

export default App;
