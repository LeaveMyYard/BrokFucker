const URL = "http://localhost:5000/api/v1/";
// const Http = new XMLHttpRequest();
// const registerBtn = document.querySelector(".registerBtn");
const data = { email: "example", password: "test" };
const regForm = document.getElementById("regForm");
const inputEmail = document.querySelector(".inputEmail");
const inputPsw = document.querySelector(".inputPsw");

regForm.addEventListener("submit", async function(e) {
  e.preventDefault();
  const value = {
    email: inputEmail.value,
    password: inputPsw.value
  };
  try {
    const response = await fetch(URL + "register", {
      // credentials: 'include',  // cookies
      method: "POST", // или 'PUT'
      body: value, // данные могут быть 'строкой' или {объектом}!
      headers: {
        "Content-Type": "application/json"
      }
    });
    const json = await response.json();
    alert("Успех: " + JSON.stringify(json));
  } catch (error) {
    alert("Ошибка: " + error);
  }
});

// fetch(URL + "register")
//   .then(response => {
//     if (!response.ok) {
//       return Promise.reject(Error("Unsuccessfull response"));
//     }
//     return response.json().then(alert(msg));
//   })

//   //onReject
//   .catch(err => {
//     console.log(err);
//     output.innerText = "Error";
//   })
//   .finally(() => {
//     //since 2018  resolve & reject
//     spinner.remove();
//   });
