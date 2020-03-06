const URL = "http://localhost:5000/api/v1/";

const lotTable = document.getElementById("lotTable");

const encData = function() {
  if (localStorage.getItem("email")) {
    return window.btoa(
      localStorage.getItem("email") + ":" + localStorage.getItem("password")
    );
  } else {
    return window.btoa(
      sessionStorage.getItem("email") + ":" + sessionStorage.getItem("password")
    );
  }
};

function dateFix(date) {
  let lotDate = new Date(date);
  let day = lotDate.getDate();
  let month = lotDate.getMonth();
  let year = lotDate.getFullYear() % 100;
  return `${day}/${month + 1}/${year}`;
}

const myFunc = async () => {
  try {
    const response = await fetch(URL + "lots/approved", {
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
      <td><a href="${"lot" + item.id + ".html"}">${item.name}</a></td>
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

myFunc();
