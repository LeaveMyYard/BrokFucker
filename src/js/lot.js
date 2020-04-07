const URL = "http://localhost:5000/api/v1/";

const lotSubMsg = document.getElementById("lotSubMsg");
const lotProfilePic = document.getElementById("lotProfilePic");
const lotPhotos = document.getElementsByClassName("lotPhotos")[0];
const clubGuarantee = document.getElementById("clubGuarantee");
const clubProven = document.getElementById("clubProven");
const lotCallback = document.getElementById("LotCallback");
const modalCloseBtn = document.getElementById("modalCloseBtn");
const modalWindow = document.getElementsByClassName("modal")[0];
const lotSubCommentary = document.getElementById("lotSubCommentary");
const selectSub = document.getElementById("select");
const lotSubBtn = document.getElementById("lotSubBtn");

const lotID = window.location.search.split("=")[1];

const encData = function () {
  if (localStorage.getItem("email")) {
    return window.btoa(
      localStorage.getItem("email") +
        ":" +
        window.atob(localStorage.getItem("password"))
    );
  } else {
    return window.btoa(
      sessionStorage.getItem("email") +
        ":" +
        window.atob(sessionStorage.getItem("password"))
    );
  }
};

function logOut() {
  localStorage.clear();
  sessionStorage.clear();
  location.reload();
}

lotCallback.addEventListener("click", function () {
  modalWindow.style.display = "block";
});

modalCloseBtn.addEventListener("click", function () {
  modalWindow.style.display = "none";
});

window.onclick = function (e) {
  if (e.target == modalWindow) {
    modalWindow.style.display = "none";
  }
};

const lotSubValue = document.getElementById("lotSubValue");
selectSub.value = "email";
if (localStorage.getItem("email")) {
  lotSubValue.value = localStorage.getItem("email");
} else if (sessionStorage.getItem("email")) {
  lotSubValue.value = sessionStorage.getItem("email");
}

selectSub.addEventListener("change", function () {
  if (this.value == "email") {
    lotSubValue.disabled = true;
    if (localStorage.getItem("email")) {
      lotSubValue.value = localStorage.getItem("email");
    } else if (sessionStorage.getItem("email")) {
      lotSubValue.value = sessionStorage.getItem("email");
    }
  } else {
    if (sessionStorage.getItem("phone") == "") {
      lotSubValue.value = "";
      lotSubValue.disabled = false;
    } else {
      lotSubValue.disabled = true;
      lotSubValue.value = sessionStorage.getItem("phone");
    }
  }
});

async function onReady() {
  if (!localStorage.getItem("email") && !sessionStorage.getItem("email")) {
    location.href = "login.html";
  } else {
    try {
      const response = await fetch(URL + "user", {
        method: "GET",
        headers: { Authorization: `Basic ${encData()}` },
      });

      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }
      const result = await response.json();
      console.log(result);
      sessionStorage.setItem("phone", result["phone_number"]);
    } catch (error) {
      console.error(error);
      localStorage.removeItem("email");
      localStorage.removeItem("password");
      sessionStorage.removeItem("email");
      sessionStorage.removeItem("password");
    }
  }
}
onReady();

vocabulary = {
  cash: "Наличные",
  cashless: "Безналичные",
  any: "Любой",
  every_month: "Ежемесячно",
  term_end: "Окончание срока",
  other: "Другое",
};

function translate(data) {
  for (let word in vocabulary) {
    if (word == data) {
      return vocabulary[word];
    }
  }
}

lotProfilePic.addEventListener("click", function () {
  location.href = "my_profile.html";
});

const getTheLot = async () => {
  try {
    const response = await fetch(URL + `lots/${lotID}`, {
      method: "GET",
      headers: { Authorization: `Basic ${encData()}` },
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();
    console.log(result);

    lotProfilePic.innerHTML = `<img src="${result["user_avatar"]}" style="width: 60%; height: 100%; margin-left: 20%"/>`;
    lotSubMsg.innerText = `Вы собираетесь спонсировать ${result["name"]}.
    Для того, чтобы подтвердить вашу подписку, укажите, как Вы хотите,
    чтобы с вами связался наш модератор и (не обязательно) оставьте комментарий.`;
    document.getElementById("profName").innerText = result["user_display_name"];
    document.getElementById("lotName").innerText = result["name"];
    document.getElementsByName("lot_date")[0].value = dateFix(result["date"]);
    document.getElementsByName("lot_reqsum")[0].value = result["amount"];
    document.getElementsByName("lot_currency")[0].value = result["currency"];
    document.getElementsByName("lot_reqmonths")[0].value = result["term"];
    document.getElementsByName("lot_method")[0].value = translate(
      result["return_way"]
    );
    document.getElementsByName("lot_security")[0].value = result["security"];
    document.getElementsByName("lot_cred")[0].value = translate(result["form"]);
    document.getElementsByName("lot_desc")[0].innerText = result["commentary"];
    document.getElementsByName("lot_percentage")[0].value =
      result["percentage"];
    clubGuarantee.innerText = result["guarantee_percentage"];
    clubProven.innerText = result["security_checked"] == false ? "Нет" : "Да";

    result["photos"]["photos"].map((photo) => {
      ` <div class="lot_photo">
            <img height="300" src="${photo}" />
        </div>`;
    });
  } catch (error) {
    console.error(error);
  }
};

getTheLot();

document
  .getElementById("LotToFav")
  .addEventListener("click", async function () {
    try {
      const response = await fetch(URL + `lots/favorites/${lotID}`, {
        method: "PUT",
        headers: {
          Authorization: `Basic ${encData()}`,
          "Content-Type": "application/json",
        },
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

lotSubBtn.addEventListener("click", async function () {
  const value = {
    type: selectSub.value == "email" ? "Email" : "PhoneCall",
    message: lotSubCommentary.innerText,
  };
  if (value.type == "PhoneCall") {
    const upd = {
      phone: lotSubValue.value,
    };
    try {
      const response = await fetch(URL + `user`, {
        method: "PUT",
        headers: {
          Authorization: `Basic ${encData()}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(upd),
      });
      if (!response.ok) {
        throw new Error("Unsuccessfull response");
      }
      sessionStorage.removeItem("phone");
    } catch (error) {
      console.error(error);
    }
  } else {
    sessionStorage.removeItem("phone");
  }
  try {
    const response = await fetch(URL + `lots/subscription/${lotID}`, {
      method: "PUT",
      headers: {
        Authorization: `Basic ${encData()}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(value),
    });
    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }
    console.log(response);
    const result = await response.json();
    if (result.msg == "You are already subscribed") {
      alert("Вы уже подписаны на этот лот!");
    }
  } catch (error) {
    console.error(error);
  }
});
