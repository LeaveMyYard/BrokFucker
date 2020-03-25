const registerBtn = document.querySelector(".registerBtn");
const inputTerms = document.querySelector("#terms");
const showPswButtons = document.querySelectorAll(".showPswIcon");
const pswInput = document.getElementsByName("psw");
const mailInput = document.getElementsByName("email");
const pswRepeatInput = document.getElementsByName("psw_repeat");
const errorContainer = document.getElementById("errorContainer");

let errorMsg = document.createElement("p");

const errorReg = window.location.search.split("error=")[1];

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

const validateForm = $(function() {
  $("#regForm").validate({
    rules: {
      email: {
        required: true,
        email: true
      },
      psw: {
        required: true,
        minlength: 8
      },
      psw_repeat: {
        equalTo: "#psw"
      }
    },
    // Specify validation error messages
    messages: {
      psw: {
        required: "Это обязательное поле!",
        minlength: "Пароль не может быть меньше 8 символов"
      },
      email: "Пожалуйста, укажите действительный email"
    }
  });
});

registerBtn.addEventListener("change", validateForm());
