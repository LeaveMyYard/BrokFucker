const URL = "/api/v1/";

let verification = window.location.search.split("code=")[1];

let errorValue = 0;

async function pswRestoration() {
  try {
    const response = await fetch(URL + "user/restore/verify/" + verification, {
      method: "GET",
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.msg);
    } else {
      location.href = "login.html?psw=success";
    }
  } catch (error) {
    location.href = `login.html?psw=error`;
  }
}

pswRestoration();