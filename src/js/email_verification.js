const URL = "http://localhost:5000/api/v1/";

let verification = window.location.search.split("code=")[1];

let errorValue = 0;

async function emailVerification() {
  try {
    const response = await fetch(URL + "register/verify/" + verification, {
      method: "GET",
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.msg);
    } else {
      location.href = "login.html";
    }
  } catch (error) {
    console.error(error);
    if (error.message == "Email is already in use.") {
      errorValue = 1;
    }
    location.href = `registration.html?error=${errorValue}`;
  }
}

emailVerification();
