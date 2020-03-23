// const URL = "http://localhost:5000/api/v1/";
const host = window.location.host;
const URL = `/api/v1/`;

const verification = window.location.search.split("code=")[1];

async function emailVerification() {
  try {
    const response = await fetch(URL + "register/verify/" + verification, {
      method: "GET"
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.msg);
    } else {
      location.href = "index.html";
    }
  } catch (error) {
    console.error(error);
    alert(error);
    location.href = "registration.html";
  }
}

emailVerification();
