const loginBtn = document.querySelector(".loginBtn");
const loginForm = document.querySelector("#loginForm");
const showPswButton = document.querySelector(".showPswIcon");
const pswInput = document.getElementsByName("psw");
const mailInput = document.getElementsByName("email");

showPswButton.addEventListener("click", handleShowPsw);

function handleShowPsw() {
  if (pswInput[0].type === "password") {
    pswInput[0].type = "text";
  } else {
    pswInput[0].type = "password";
  }
}

function check() {
  let storedMail = localStorage.getItem("email");
  let storedPw = localStorage.getItem("password");

  if (mailInput[0].value != storedMail || pswInput[0].value != storedPw) {
    alert("Вы ввели неверные данные!");
  } else {
    location.href = "index.html";
  }
}

loginBtn.addEventListener("click", function(e) {
  e.preventDefault();
  check();
});
