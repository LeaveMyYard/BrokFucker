const URL = "http://localhost:5000/api/v1/";

const lotTable = document.getElementById("lotTable");

const encData = function () {
  if (localStorage.getItem("email")) {
<<<<<<< HEAD
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
=======
    return (
      window.btoa(localStorage.getItem("email") + ":" +
      window.atob(localStorage.getItem("password")))
    );
  } else {
    return (
      window.btoa(sessionStorage.getItem("email") + ":" +
      window.atob(sessionStorage.getItem("password")))
>>>>>>> 212370d1b1f0c4d99837c9bbc714aa6f0cd36a75
    );
  }
};

async function onReady() {
  if (!localStorage.getItem("email") && !sessionStorage.getItem("email")) {
    return;
  } else {
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
  }
}
onReady();

const getLots = async () => {
  try {
    const response = await fetch(URL + "lots", {
      method: "GET",
      // headers: { Authorization: `Basic ${encData()}` }
    });

    if (!response.ok) {
      return new Error("Unsuccessfull response");
    } else {
      const result = await response.json();
      const lotArr = [];
      result.forEach((item) => {
        item = `
      <tr>
      <td>${dateFix(item.date)}</td>
      <td><a class="linkToPage" href="${"lot.html?id=" + item.id}">${
          item.name
        }</a></td>
      <td>${item.user}</td>
      <td>${item.amount}</td>
      <td>${item.currency}</td>
      <td>${item.term}</td>
      <td>${item.return_way}</td>
      <td>${item.security}</td>
      <td>${item.percentage}</td>
      <td>${item.form}</td>
      <td>${item.security_checked ? "Да" : "Нет"}</td>
      <td>${item.guarantee_percentage}</td>
      </tr>`;
        lotArr.push(item);
      });

      lotTable.innerHTML += lotArr.join("");
    }
  } catch (error) {
    errorMsg.remove();
    errorMsg.classList.add("errorMsg");
    errorMsg.innerText = "Неправильные данные для входа.";
    errorContainer.prepend(errorMsg);
    console.error(error);
  }
};

getLots();
