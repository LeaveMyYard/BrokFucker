const menuNotLogged = document.getElementById("menuIfNotLogged");
const menuLogged = document.getElementById("menuIfLogged");
const logOutBtn = document.querySelector(".fixed-header__menu-item_exit");

logOutBtn.addEventListener("click", logOut);

function logOut() {
  localStorage.clear();
  sessionStorage.clear();
  location.reload();
}

function checkIfLogged() {
  if (localStorage.getItem("email") || sessionStorage.getItem("email")) {
    menuNotLogged.style.display = "none";
    menuLogged.style.display = "block";
  } else {
    menuLogged.style.display = "none";
    menuNotLogged.style.display = "block";
  }
}
checkIfLogged();
