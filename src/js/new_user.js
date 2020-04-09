const URL = "http://localhost:5000/api/v1/";

const regForm = document.getElementById("regForm");
const inputEmail = document.querySelector(".inputEmail");
const inputPsw = document.querySelector(".inputPsw");
const spinner = document.getElementById("spinner");
const errorContainer = document.getElementById("errorContainer");

let errorMsg = document.createElement("p");

const errorReg = window.location.search.split("error=")[1];

if (errorReg == 1) {
  errorMsg.classList.add("errorMsg");
  errorMsg.innerText = "Этот email уже используется!";
  errorContainer.append(errorMsg);
}

document.querySelector(".inputEmail").addEventListener("input", (e) => {
  e.target.value = e.target.value.replace(/[^a-z, 0-9, \@, \. ]/i, "");
});

regForm.addEventListener("submit", async function (e) {
  e.preventDefault();
  if ($("#regForm").valid() == false) {
    return;
  }
  const value = {
    email: inputEmail.value,
    password: inputPsw.value,
  };
  try {
    spinner.style["display"] = "inline-block";
    const response = await fetch(URL + "register", {
      method: "POST",
      body: JSON.stringify(value),
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (response.ok) {
      alert(`Успех! Письмо с подтверждением отослано на ${inputEmail.value}`);
      spinner.style["display"] = "none";
    } else throw new Error("Ошибка! Проверьте корректность введённых данных.");
  } catch (error) {
    errorMsg.remove();
    errorContainer.append(errorMsg);
    errorMsg.classList.add("errorMsg");
    errorMsg.innerText = error.message;
    spinner.style["display"] = "none";
  }
});
