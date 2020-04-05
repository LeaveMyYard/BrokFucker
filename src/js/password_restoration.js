const URL = "http://localhost:5000/api/v1/";

const verification = window.location.search.split("code=")[1];

let errorValue = 0;

async function pswRestoration() {
  try {
    const response = await fetch(URL + "user/password/verify/" + verification, {
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
    if (error.message == "") {
      errorValue = 3;
    }
    location.href = `registration.html?error=${errorValue}`;
  }
}

pswRestoration();
