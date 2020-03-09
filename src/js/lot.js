const URL = "http://localhost:5000/api/v1/";

const lotProfilePic = document.getElementById("lotProfilePic");
const lotPhotos = document.getElementsByClassName("lotPhotos")[0];
const clubGuarantee = document.getElementById("clubGuarantee");
const clubProven = document.getElementById("clubProven");

const lotID = window.location.search.split("=")[1];

const encData = function() {
  if (localStorage.getItem("email")) {
    return (
      window.btoa(localStorage.getItem("email") + ":") +
      localStorage.getItem("password")
    );
  } else {
    return (
      window.btoa(sessionStorage.getItem("email") + ":") +
      sessionStorage.getItem("password")
    );
  }
};

function dateFix(date) {
  let lotDate = new Date(date);
  let day = lotDate.getDate();
  let month = lotDate.getMonth();
  let year = lotDate.getFullYear() % 100;
  return `${day}/${month + 1}/${year}`;
}

function onReady() {
  if (!localStorage.getItem("email") && !sessionStorage.getItem("email")) {
    location.href = "login.html";
  } else {
    async () => {
      try {
        const response = await fetch(URL + "user", {
          method: "GET",
          headers: { Authorization: `Basic ${encData()}` }
        });

        if (!response.ok) {
          throw new Error("Unsuccessfull response");
        }
      } catch (error) {
        console.error(error);
        localStorage.removeItem("email");
        localStorage.removeItem("password");
        sessionStorage.removeItem("email");
        sessionStorage.removeItem("password");
      }
    };
  }
}
onReady();

const getTheLot = async () => {
  try {
    const response = await fetch(URL + `lots/${lotID}`, {
      method: "GET",
      headers: { Authorization: `Basic ${encData()}` }
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();
    console.log(result);
    lotProfilePic.style.backgroundImage = `url(${result["user_avatar"]})`;
    document.getElementById("profName").innerText = result["user_display_name"];
    document.getElementById("lotName").innerText = result["name"];
    document.getElementsByName("lot_date")[0].value = dateFix(result["date"]);
    document.getElementsByName("lot_reqsum")[0].value = result["amount"];
    document.getElementsByName("lot_currency")[0].value = result["currency"];
    document.getElementsByName("lot_reqmonths")[0].value = result["term"];
    document.getElementsByName("lot_method")[0].value = result["return_way"];
    document.getElementsByName("lot_security")[0].value = result["security"];
    document.getElementsByName("lot_cred")[0].value = result["form"];
    document.getElementsByName("lot_desc")[0].innerText = result["commentary"];
    document.getElementsByName("lot_percentage")[0].value =
      result["percentage"];
    clubGuarantee.innerText = result["guarantee_percentage"];
    clubProven.innerText = result["security_checked"] == false ? "Нет" : "Да";

    result["photos"]["photos"].forEach(photo => {
      lotPhotos.innerHTML += `<img>${photo}</img>`;
    });
  } catch (error) {
    console.error(error);
  }
};

getTheLot();

document.getElementById("LotToFav").addEventListener("click", async function() {
  try {
    const response = await fetch(URL + `lots/favorites/${lotID}`, {
      method: "PUT",
      headers: { Authorization: `Basic ${encData()}` }
    });
    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    } else {
      alert("Лот добавлен в избранные!");
    }
  } catch (error) {
    console.error(error);
  }
});
