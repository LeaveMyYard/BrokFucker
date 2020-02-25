// const loginBtn = document.querySelector(".loginBtn");
const showPswButton = document.querySelector(".showPswIcon");
const pswInput = document.getElementsByName("psw");

showPswButton.addEventListener("click", handleShowPsw);

function handleShowPsw() {
  if (pswInput[0].type === "password") {
    pswInput[0].type = "text";
  } else {
    pswInput[0].type = "password";
  }
}
