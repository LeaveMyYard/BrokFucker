const URL = "/api/v1/";

const myLotsBtn = document.getElementById("myLotsBtn");
const myprofEmail = document.getElementById("myprofEmail");
const myprofPhone = document.getElementById("myprofPhone");
const myprofName = document.getElementById("myprofName");
const myprofRegDate = document.getElementById("myprofRegDate");
const profilePic = document.getElementById("profilePic");
const docMessage = document.querySelector("#doc_message");
const docMessageInfo = document.querySelector("#doc_message_info");

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

function onReady() {
  if (!localStorage.getItem("email") && !sessionStorage.getItem("email")) {
    location.href = "login.html";
  } else {
    async () => {
      try {
        const response = await fetch(URL + "user", {
          method: "GET",
          headers: { Authorization: `Basic ${encData()}` },
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

myLotsBtn.addEventListener("click", function () {
  location.href = "my_lots.html";
});

const profData = async () => {
  try {
    const response = await fetch(URL + "user", {
      method: "GET",
      headers: { Authorization: `Basic ${encData()}` },
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();

    profilePic.innerHTML = `<img src="${result["avatar"]}" style="width: 60%; height: 100%; margin-left: 20%" />`;
    myprofEmail.innerText = result["email"];
    myprofRegDate.innerText = dateFix(result["registration_date"]);
    myprofName.value = result["name"];
    myprofPhone.value = result["phone_number"];
  } catch (error) {
    console.error(error);
  }
};
profData();

const myprofPsw = document.querySelector("#myprofPsw");

const updateProfData = async () => {
  const value = {
    name: myprofName.value,
    phone: myprofPhone.value,
  };
  const pswValue = {
    password: myprofPsw.value,
  };
  try {
    const response = await fetch(URL + "user", {
      method: "PUT",
      headers: {
        Authorization: `Basic ${encData()}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(value),
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    } else {
      if (myprofPsw.value.length === 0) {
        docMessageInfo.innerHTML = `<p class="myprof_successMsg">Данные обновлены!</p>`;
        setTimeout(() => {
          docMessageInfo.innerHTML = "";
        }, 5000);
      }
    }
  } catch (error) {
    console.error(error);
    return;
  }
  if (
    myprofPsw.value !== "" &&
    myprofPsw.value.length >= 8 &&
    myprofPsw.value.length <= 32
  ) {
    try {
      const response = await fetch(URL + "user/password", {
        method: "PUT",
        headers: {
          Authorization: `Basic ${encData()}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(pswValue),
      });
      if (!response.ok) {
        throw new Error("Не удалось сменить пароль.");
      } else {
        docMessage.innerHTML = `<p class="myprof_successMsg">Письмо с подтверждением отправлено на Вашу почту</p>`;
        setTimeout(() => {
          docMessage.innerHTML = "";
        }, 5000);
      }
    } catch (error) {
      console.error(error.message);
      docMessage.innerHTML = `<p class="myprof_errorMsg">${error.message}</p>`;
    }
  } else {
    if (myprofPsw.value.length !== 0 && myprofPsw.value.length < 8) {
      docMessage.innerHTML = `<p class="myprof_errorMsg">Пароль не может быть меньше 8 символов!</p>`;
    } else if (myprofPsw.value.length !== 0 && myprofPsw.value.length > 32) {
      docMessage.innerHTML = `<p class="myprof_errorMsg">Пароль не может быть больше 32 символов!</p>`;
    }
    setTimeout(() => {
      docMessage.innerHTML = "";
    }, 5000);
    return;
  }
};

document.getElementById("updateData").addEventListener("click", updateProfData);

const uploadProfPic = async () => {
  const formData = new FormData();
  const fileField = document.querySelector('input[type="file"]');
  const file = fileField.files[0];

  formData.append("file", file);

  try {
    const response = await fetch(URL + "user/avatar", {
      method: "POST",
      headers: { Authorization: `Basic ${encData()}` },
      body: formData,
    });

    const result = await response.json();
    console.log("Успех:", JSON.stringify(result));

    location.reload();
  } catch (error) {
    console.error("Ошибка:", error);
  }
};

const deleteProfPic = async () => {
  try {
    const response = await fetch(URL + "user/avatar", {
      method: "DELETE",
      headers: { Authorization: `Basic ${encData()}` },
    });

    const result = await response.json();
    console.log("Успех:", JSON.stringify(result));
    location.reload();
  } catch (error) {
    console.error("Ошибка:", error);
  }
};

document
  .getElementById("deleteAvatar")
  .addEventListener("click", deleteProfPic);

document
  .getElementById("uploadProfPic")
  .addEventListener("change", uploadProfPic);
