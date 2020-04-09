import React from "react";

export default function Modal(show, handleApprove) {
  return (
    <div className="modal">
      <h1 className="heading">Причина</h1>
      <br />
      <textarea id="declineReason"></textarea>
      <button onClick={handleApprove} id="unapproveLotBtn">
        ОТПРАВИТЬ
      </button>
    </div>
  );
}
