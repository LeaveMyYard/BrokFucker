const URL = "http://localhost:5000/api/v1/";

const loginBtn = document.querySelector(".loginBtn");
const loginForm = document.querySelector("#loginForm");
const showPswButton = document.querySelector(".showPswIcon");
const pswInput = document.getElementsByName("psw");
const mailInput = document.getElementsByName("email");
const termsCheckbox = document.getElementById("terms");
const errorContainer = document.getElementById("errorContainer");
const pswReset = document.querySelector(".pswReset");

let errorMsg = document.createElement("p");

function onReady() {
  if (localStorage.getItem("email") || sessionStorage.getItem("email")) {
    location.href = "index.html";
  }
}

function storeLocalStorage() {
  localStorage.setItem("email", mailInput[0].value);
  localStorage.setItem("password", window.btoa(pswInput[0].value));
}

function storeSessionStorage() {
  sessionStorage.setItem("email", mailInput[0].value);
  sessionStorage.setItem("password", window.btoa(pswInput[0].value));
}

showPswButton.addEventListener("click", handleShowPsw);

function handleShowPsw() {
  if (pswInput[0].type === "password") {
    pswInput[0].type = "text";
  } else {
    pswInput[0].type = "password";
  }
}

const logIn = async () => {
  const userData = `${mailInput[0].value}:${pswInput[0].value}`;
  const encData = window.btoa(userData);
  try {
    const response = await fetch(URL + "user", {
      method: "GET",
      headers: { Authorization: `Basic ${encData}` },
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.msg);
    } else {
      if (termsCheckbox.checked == true) {
        storeLocalStorage();
      } else {
        storeSessionStorage();
      }
      location.href = "index.html";
    }
  } catch (error) {
    sessionStorage.setItem("email", mailInput[0].value);
    errorMsg.remove();
    errorMsg.classList.add("errorMsg");
    errorMsg.innerText = "Неправильные данные для входа.";
    errorContainer.prepend(errorMsg);
    console.error(error);
  }
};

document.querySelector(".inputEmail").addEventListener("input", (e) => {
  e.target.value = e.target.value.replace(/[^a-z, 0-9, \@, \. ]/i, "");
});

const validateForm = $(function () {
  $("#loginForm").validate({
    rules: {
      email: {
        required: true,
      },
      psw: {
        required: true,
      },
    },
    messages: {
      psw: "",
      email: "",
    },
  });
});

loginBtn.addEventListener("change", validateForm);

loginBtn.addEventListener("click", function (e) {
  e.preventDefault();
  if ($("#loginForm").valid() == false) {
    return;
  }
  logIn();
});

const resetPswContainer = document.querySelector("#resetPsw_container");

pswReset.addEventListener("click", async function (e) {
  e.preventDefault();
  const mail = () => {
    if (!sessionStorage.getItem("email")) {
      return mailInput[0].value;
    } else {
      return sessionStorage.getItem("email");
    }
  };
  try {
    const response = await fetch(URL + "user/restore/" + mail(), {
      method: "GET",
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.msg);
    } else {
      sessionStorage.removeItem("email");
      console.log("Success!");
      errorMsg.classList.add("successMsg");
      errorMsg.innerText = "Письмо с подтверждением отправлено на Вашу почту.";
      setTimeout(() => {
        errorMsg.innerText = "";
        errorMsg.classList.remove("successMsg");
      }, 7000);
    }
  } catch (error) {
    errorMsg.remove();
    errorMsg.classList.add("errorMsg");
    errorMsg.innerText =
      "Ошибка. Пожалуйста, введите Вашу почту и попробуйте снова.";
    errorContainer.prepend(errorMsg);
    console.error(error);
  }
});
