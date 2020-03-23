// const URL = "http://localhost:5000/api/v1/";
const host = window.location.host;
const URL = `/api/v1/`;

const regForm = document.getElementById("regForm");
const inputEmail = document.querySelector(".inputEmail");
const inputPsw = document.querySelector(".inputPsw");
const spinner = document.getElementById("spinner");

regForm.addEventListener("submit", async function(e) {
  e.preventDefault();
  const value = {
    email: inputEmail.value,
    password: inputPsw.value
  };
  try {
    spinner.style["display"] = "inline-block";
    const response = await fetch(URL + "register", {
      method: "POST",
      body: JSON.stringify(value),
      headers: {
        "Content-Type": "application/json"
      }
    });
    if (response.ok) {
      alert(`Успех! Письмо с подтверждением отослано на ${inputEmail.value}`);
      spinner.style["display"] = "none";
    } else throw new Error(error);
  } catch (error) {
    alert("Ошибка! Что-то пошло не так.");
    spinner.style["display"] = "none";
  }
});
