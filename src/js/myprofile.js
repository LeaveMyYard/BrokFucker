// const URL = "http://localhost:5000/api/v1/";
const URL = `${window.location.host}/api/v1/`;

const myLotsBtn = document.getElementById("myLotsBtn");
const myprofEmail = document.getElementById("myprofEmail");
const myprofPhone = document.getElementById("myprofPhone");
const myprofName = document.getElementById("myprofName");
const myprofRegDate = document.getElementById("myprofRegDate");
const profilePic = document.getElementById("profilePic");

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

function onReady() {
  if (!localStorage.getItem("email") && !sessionStorage.getItem("email")) {
    location.href = "login.html";
  } else {
    async () => {
      try {
        const response = await fetch("/api/v1/" + "user", {
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

myLotsBtn.addEventListener("click", function() {
  location.href = "my_lots.html";
});

const profData = async () => {
  try {
    const response = await fetch("/api/v1/" + "user", {
      method: "GET",
      headers: { Authorization: `Basic ${encData()}` }
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

const updateProfData = async () => {
  const value = {
    name: myprofName.value,
    phone: myprofPhone.value
  };
  try {
    const response = await fetch("/api/v1/" + "user", {
      method: "PUT",
      headers: {
        Authorization: `Basic ${encData()}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(value)
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    } else {
      location.reload();
    }
  } catch (error) {
    console.error(error);
  }
};

document.getElementById("updateData").addEventListener("click", updateProfData);

const uploadProfPic = async () => {
  const formData = new FormData();
  const fileField = document.querySelector('input[type="file"]');
  const file = fileField.files[0];

  formData.append("file", file);

  try {
    const response = await fetch("/api/v1/" + "user/avatar", {
      method: "POST",
      headers: { Authorization: `Basic ${encData()}` },
      body: formData
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
    const response = await fetch("/api/v1/" + "user/avatar", {
      method: "DELETE",
      headers: { Authorization: `Basic ${encData()}` }
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
