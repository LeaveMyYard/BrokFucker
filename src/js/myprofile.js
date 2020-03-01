const URL = "http://localhost:5000/api/v1/";
const myLotsBtn = document.getElementById("myLotsBtn");
const myprofEmail = document.getElementById("myprofEmail");
const myprofPhone = document.getElementById("myprofPhone");
const myprofName = document.getElementById("myprofName");
const myprofRegDate = document.getElementById("myprofRegDate");

myLotsBtn.addEventListener("click", function() {
  location.href = "my_lots.html";
});

const myFunc = async () => {
  try {
    const response = await fetch(URL + "user");

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();
    myprofEmail.innerText = result[0];
    myprofRegDate.innerText = result[2];
    myprofName.placeholder = result[3];
    myprofPhone.placeholder = result[4];
  } catch (error) {
    console.error(error);
  }
};

myFunc();
