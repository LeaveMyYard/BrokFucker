import React from "react";
import { encData, URL } from "../constants";

const ModeratorsPage = () => {
  const handleMakeModerator = async () => {
    const modermail = document.getElementById("modermail").value;
    try {
      const response = await fetch(URL + "user/" + modermail + "/moderator", {
        method: "PUT",
        headers: { Authorization: `Basic ${encData}` },
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error("Ошибка.");
      } else {
        alert("Успешно!");
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleDeleteModerator = async () => {
    const modermail = document.getElementById("modermail").value;
    try {
      const response = await fetch(URL + "user/" + modermail + "/moderator", {
        method: "DELETE",
        headers: { Authorization: `Basic ${encData}` },
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error("Ошибка.");
      } else {
        alert("Успешно!");
      }
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div>
      <h1>Модерирование</h1>
      <h3>Введите почту пользователя в поле ниже и выберите действие.</h3>
      <input id="modermail" type="email"></input>
      <button id="makeModerator" onClick={handleMakeModerator}>
        СДЕЛАТЬ МОДЕРАТОРОМ
      </button>
      <button id="deleteModerator" onClick={handleDeleteModerator}>
        УБРАТЬ ПОЛНОМОЧИЯ
      </button>
    </div>
  );
};
export default ModeratorsPage;
