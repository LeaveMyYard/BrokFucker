const URL = "http://localhost:5000/api/v1/";
const myLotsBtn = document.getElementById("myLotsBtn");
const myprofEmail = document.getElementById("myprofEmail");
const myprofPhone = document.getElementById("myprofPhone");
const myprofName = document.getElementById("myprofName");
const myprofRegDate = document.getElementById("myprofRegDate");
const profilePic = document.getElementById("profilePic");

const encData = window.btoa(
  localStorage.getItem("email") + ":" + localStorage.getItem("password")
);

function dateFix(date) {
  let givenDate = new Date(date);
  let day = givenDate.getDate();
  let month = givenDate.getMonth();
  let year = givenDate.getFullYear();
  return `${day}.${month + 1}.${year}`;
}

myLotsBtn.addEventListener("click", function() {
  location.href = "my_lots.html";
});

const profData = async () => {
  try {
    const response = await fetch(URL + "user", {
      method: "GET",
      headers: { Authorization: `Basic ${encData}` }
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();

    profilePic.style.backgroundImage = `url(${result["avatar"]})`;
    myprofEmail.innerText = result["email"];
    myprofRegDate.innerText = dateFix(result["registration_date"]);
    myprofName.value = result["name"];
    myprofPhone.value = result["phone_number"];
  } catch (error) {
    console.error(error);
  }
};
profData();

const uploadProfPic = async () => {
  const formData = new FormData();
  const fileField = document.querySelector('input[type="file"]');

  formData.append("avatar", fileField.files[0]);

  try {
    const response = await fetch(URL + "user/avatar", {
      method: "POST",
      headers: { Authorization: `Basic ${encData}` },
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

document.querySelector(".inputPhone").addEventListener("input", e => {
  let x = e.target.value
    .replace(/\D/g, "")
    .match(/(\d{0,3})(\d{0,3})(\d{0,4})/);

  e.target.value = !x[2]
    ? x[1]
    : "( " + x[1] + " ) " + x[2] + (!x[3] ? "" : " - " + x[3]);
});
