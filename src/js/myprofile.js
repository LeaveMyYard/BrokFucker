const URL = "http://localhost:5000/api/v1/";
const myLotsBtn = document.getElementById("myLotsBtn");
const myprofEmail = document.getElementById("myprofEmail");
const myprofPhone = document.getElementById("myprofPhone");
const myprofName = document.getElementById("myprofName");
const myprofRegDate = document.getElementById("myprofRegDate");
const profilePic = document.getElementById("profilePic");

myLotsBtn.addEventListener("click", function() {
  location.href = "my_lots.html";
});

const profData = async () => {
  try {
    const response = await fetch(URL + "user");

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();
    myprofEmail.innerText = result[0];
    myprofRegDate.innerText = result[2];
    myprofName.value = result[3];
    myprofPhone.value = result[4];
  } catch (error) {
    console.error(error);
  }
};

profData();

const profPic = async () => {
  try {
    const response = await fetch(URL + "user/avatar");

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();
    profilePic.style.backgroundImage = `url(${result})`;
  } catch (error) {
    console.error(error);
  }
};

profPic();

const uploadProfPic = async () => {
  const formData = new FormData();
  const fileField = document.querySelector('input[type="file"]');

  formData.append("avatar", fileField.files[0]);

  try {
    const response = await fetch(URL + "user/avatar", {
      method: "POST",
      //   enctype: "multipart/form-data",
      body: formData
    });
    const result = await response.json();
    console.log("Успех:", JSON.stringify(result));
  } catch (error) {
    console.error("Ошибка:", error);
  }
};

profilePic.addEventListener("click", uploadProfPic);
