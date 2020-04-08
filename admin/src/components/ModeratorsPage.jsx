import React, { useState } from "react";
import { encData, URL } from "../constants";
import authService from "../services/Auth";
import Spinner from "react-bootstrap/Spinner";

const ModeratorsPage = () => {
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const authToken = authService.getAuthToken();

  const handleMakeModerator = async () => {
    const modermail = document.getElementById("modermail").value;
    setLoading(true);
    try {
      const response = await fetch(URL + "user/" + modermail + "/moderator", {
        method: "POST",
        headers: {
          Authorization: `Basic ${authToken}`,
          "Content-Type": "application/json",
        },
      });
      const result = await response.json();
      if (!response.ok) {
        if (result.type === "UserNotExists") {
          throw new Error("UserNotExists");
        } else throw new Error("Fetch fail");
      } else {
        alert("Успешно!");
      }
    } catch (error) {
      console.error(error);
      error.message === "UserNotExists"
        ? setErrorMsg("Ошибка! Такого пользователя не существует.")
        : setErrorMsg("Ошибка! Проверьте подключение к интернету.");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteModerator = async () => {
    const modermail = document.getElementById("modermail").value;
    setLoading(true);
    try {
      const response = await fetch(URL + "user/" + modermail + "/moderator", {
        method: "DELETE",
        headers: {
          Authorization: `Basic ${authToken}`,
          "Content-Type": "application/json",
        },
      });
      const result = await response.json();
      if (!response.ok) {
        if (result.type === "UserNotExists") {
          throw new Error("UserNotExists");
        } else throw new Error("Fetch fail");
      } else {
        alert("Успешно!");
      }
    } catch (error) {
      console.error(error);
      error.message === "UserNotExists"
        ? setErrorMsg("Ошибка! Такого пользователя не существует.")
        : setErrorMsg("Ошибка! Проверьте подключение к интернету.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="moderators-page_container">
      <h1 className="heading">Модерирование</h1>
      <h3>Введите почту пользователя в поле ниже и выберите действие.</h3>
      <input className="form-control mt-4" id="modermail" type="email"></input>
      <div className="moderators-page_btns">
        <button
          className="btn btn-primary moderator-btn"
          id="makeModerator"
          onClick={handleMakeModerator}
        >
          {loading ? (
            <Spinner size="sm" animation="border" />
          ) : (
            "СДЕЛАТЬ МОДЕРАТОРОМ"
          )}
        </button>
        <button
          className="btn btn-primary moderator-btn ml-1"
          id="deleteModerator"
          onClick={handleDeleteModerator}
        >
          {loading ? (
            <Spinner size="sm" animation="border" />
          ) : (
            "УБРАТЬ ПОЛНОМОЧИЯ"
          )}
        </button>
      </div>
      {errorMsg && <p className="errorMsg">{errorMsg}</p>}
    </div>
  );
};
export default ModeratorsPage;
