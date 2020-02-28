const URL = "http://localhost:5000/api/v1/";

const regForm = document.getElementById("regForm");
const inputEmail = document.querySelector(".inputEmail");
const inputPsw = document.querySelector(".inputPsw");

regForm.addEventListener("submit", async function(e) {
  e.preventDefault();
  const value = {
    email: inputEmail.value,
    password: inputPsw.value
  };
  try {
    const response = await fetch(URL + "register", {
      // credentials: 'include',  // cookies
      method: "POST", // или 'PUT'
      body: JSON.stringify(value),
      headers: {
        "Content-Type": "application/json"
      }
    });
    if (response.ok) {
      alert(`Успех! Письмо с подтверждение отослано на ${inputEmail.value}`);
    } else throw new Error(error);
  } catch (error) {
    alert("Ошибка! Что-то пошло не так.");
  }
});
