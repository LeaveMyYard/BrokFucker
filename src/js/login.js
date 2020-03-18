const URL = "http://localhost:5000/api/v1/";
// const URL = `${window.location.host}/`;

const loginBtn = document.querySelector(".loginBtn");
const loginForm = document.querySelector("#loginForm");
const showPswButton = document.querySelector(".showPswIcon");
const pswInput = document.getElementsByName("psw");
const mailInput = document.getElementsByName("email");
const termsCheckbox = document.getElementById("terms");

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
      headers: { Authorization: `Basic ${encData}` }
    });

    if (!response.ok) {
      throw new Error("Wrong User Data");
    } else {
      if (termsCheckbox.checked == true) {
        storeLocalStorage();
      } else {
        storeSessionStorage();
      }
      location.href = "index.html";
    }
  } catch (error) {
    console.error(error);
  }
};

loginBtn.addEventListener("click", function(e) {
  e.preventDefault();
  logIn();
});
