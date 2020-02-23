const registerBtn = document.querySelector(".registerBtn");
const inputTerms = document.querySelector("#terms");
const showPswButtons = document.querySelectorAll(".showPswIcon");
const pswInput = document.getElementsByName("psw");
const pswRepeatInput = document.getElementsByName("psw-repeat");

inputTerms.addEventListener("click", function() {
  if (inputTerms.checked) {
    registerBtn.classList.toggle("active");
    registerBtn.removeAttribute("disabled");
  } else {
    registerBtn.classList.toggle("active");
    registerBtn.setAttribute("disabled", "disabled");
  }
});

showPswButtons[0].addEventListener("click", handleShowPsw);
showPswButtons[1].addEventListener("click", handleShowPsw);

function handleShowPsw() {
  if (this === showPswButtons[0]) {
    if (pswInput[0].type === "password") {
      pswInput[0].type = "text";
    } else {
      pswInput[0].type = "password";
    }
  } else {
    if (pswRepeatInput[0].type === "password") {
      pswRepeatInput[0].type = "text";
    } else {
      pswRepeatInput[0].type = "password";
    }
  }
}

console.log(pswInput[0].value);

registerBtn.addEventListener("click", function() {
  if (pswInput[0].value != pswRepeatInput[0].value) {
    pswRepeatInput.setCustomValidity("Пароли не совпадают");
  } else {
    pswRepeatInput.setCustomValidity("");
  }
});
