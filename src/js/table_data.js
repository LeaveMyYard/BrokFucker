const URL = "http://localhost:5000/api/v1/";
// const URL = `${window.location.host}/api/v1/`;

const lotTable = document.getElementById("lotTable");

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

async function onReady() {
  if (!localStorage.getItem("email") && !sessionStorage.getItem("email")) {
    return;
  } else {
    try {
      const response = await fetch(URL + "user", {
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
  }
}
onReady();

const getLots = async () => {
  try {
    const response = await fetch(URL + "lots", {
      method: "GET"
      // headers: { Authorization: `Basic ${encData()}` }
    });

    if (!response.ok) {
      return new Error("Unsuccessfull response");
    } else {
      const result = await response.json();
      const lotArr = [];
      result.forEach(item => {
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
    console.error(error);
  }
};

getLots();
