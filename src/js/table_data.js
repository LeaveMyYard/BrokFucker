const URL = "http://localhost:5000/api/v1/";

const lotTable = document.getElementById("lotTable");
const filterBtn = document.getElementById("filterBtn");
// const lotOptions = window.location.search.split("?")[1];
const orderBy = document.getElementById("order_by");
const orderType = document.getElementById("order_type");
const showOnly = document.getElementById("show_only");

const encData = function () {
  if (localStorage.getItem("email")) {
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

vocabulary = {
  cash: "Наличные",
  cashless: "Безналичные",
  any: "Любой",
  every_month: "Ежемесячно",
  term_end: "Окончание срока",
  other: "Другое",
};

function translate(data) {
  for (let word in vocabulary) {
    if (word == data) {
      return vocabulary[word];
    }
  }
}

// todo 75 line change currency to current selected order_by
// lock filterBtn for 2 sec after each filtration

const getLots = async () => {
  let options = {
    filter: {
      order_by: orderBy.value,
      order_type: orderType.value,
      // show_only: {
      //   currency: [showOnly.value ? showOnly.value : ""],
      // },
    },
  };
  try {
    const response = await fetch(URL + "lots/approved", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(options),
    });

    if (!response.ok) {
      return new Error("Unsuccessfull response");
    } else {
      const result = await response.json();
      console.log(result);
      const lotArr = [];
      result.forEach((item) => {
        item = `
      <tr class="lot-list_item">
      <td>${dateFix(item.date)}</td>
      <td><a class="linkToPage" href="${"lot.html?id=" + item.id}">${
          item.name
        }</a></td>
      <td>${item.user}</td>
      <td>${item.amount}</td>
      <td>${item.currency}</td>
      <td>${item.term}</td>
      <td>${translate(item.return_way)}</td>
      <td>${item.security}</td>
      <td>${item.percentage}</td>
      <td>${translate(item.form)}</td>
      <td>${item.security_checked ? "Да" : "Нет"}</td>
      <td>${item.guarantee_percentage}</td>
      </tr>`;
        lotArr.push(item);
      });

      lotTable.innerHTML += lotArr.join("");
      console.log(options);
    }
  } catch (error) {}
};

getLots();

function clearLots() {
  let lotItems = document.querySelectorAll(".lot-list_item");
  console.log(lotItems);

  lotItems.forEach((lot) => lot.remove());
}

filterBtn.addEventListener("click", () => {
  filterBtn.disabled = true;
  clearLots();
  getLots();
  setTimeout(() => {
    filterBtn.disabled = false;
  }, 1000);
});

function showOnlyValues() {
  if (orderBy.value === "currency") {
    showOnly.innerHTML = `
    <option value="UAH">UAH</option>
    <option value="USD">USD</option>
    <option value="EUR">EUR</option>
    <option value="BTC">BTC</option>
    <option value="ETH">ETH</option>
    `;
    showOnly.style.display = "inline-block";
  } else if (orderBy.value === "return_way") {
    showOnly.innerHTML = `
    <option value="every_month">Ежемесячно</option>
    <option value="term_end">Окончание срока</option>
    <option value="other">Другое</option>
    `;
    showOnly.style.display = "inline-block";
  } else if (orderBy.value === "form") {
    showOnly.innerHTML = `
    <option value="cash">Наличные</option>
    <option value="cashless">Безналичные</option>
    <option value="any">Любой</option>
    `;
    showOnly.style.display = "inline-block";
  } else {
    showOnly.style.display = "none";
  }
}

orderBy.addEventListener("change", showOnlyValues);
