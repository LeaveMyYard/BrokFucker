const URL = "http://localhost:5000/api/v1/";
const myLots = document.querySelector(".my-lots");
const modalCloseBtn = document.getElementById("modalCloseBtn");
const modalWindow = document.getElementsByClassName("modal")[0];
const createLotBtn = document.getElementById("createLot");
const createLotPublish = document.getElementById("createLotPublish");

// create lot form
const createLotName = document.getElementsByName("create_lot_name")[0];
const createLotAmount = document.getElementsByName("create_lot_reqsum")[0];
const createLotTerm = document.getElementsByName("create_lot_reqmonths")[0];
const createLotReturnWay = document.getElementsByName("create_lot_method")[0];
const createLotSecurity = document.getElementsByName("create_lot_security")[0];
const createLotCredForm = document.getElementsByName("create_lot_cred")[0];
const createLotCurrency = document.getElementsByName("create_lot_currency")[0];
const createLotDescription = document.getElementsByName("create_lot_desc")[0];
const createLotPercentage = document.getElementsByName(
  "create_lot_percentage"
)[0];

//get lots form
const lotName = document.getElementsByName("lot_name")[0];
const lotAmount = document.getElementsByName("lot_reqsum")[0];
const lotTerm = document.getElementsByName("lot_reqmonths")[0];
const lotReturnWay = document.getElementsByName("lot_method")[0];
const lotSecurity = document.getElementsByName("lot_security")[0];
const lotCredForm = document.getElementsByName("lot_cred")[0];
const lotCurrency = document.getElementsByName("lot_currency")[0];
const lotDescription = document.getElementsByName("lot_shortdesc")[0];
const lotPercentage = document.getElementsByName("lot_percentage")[0];

createLotBtn.addEventListener("click", function() {
  modalWindow.style.display = "block";
});

modalCloseBtn.addEventListener("click", function() {
  modalWindow.style.display = "none";
});

window.onclick = function(e) {
  if (e.target == modalWindow) {
    modalWindow.style.display = "none";
  }
};

const encData = window.btoa(
  localStorage.getItem("email") + ":" + localStorage.getItem("password")
);

function dateFix(date) {
  let givenDate = new Date(date);
  let day = givenDate.getDate();
  let month = givenDate.getMonth();
  let year = givenDate.getFullYear();
  return `${day}.${month + 1}.${year}`;
}

document.querySelector(".inputReqSum").addEventListener("input", e => {
  e.target.value = e.target.value.replace(/\D/g, "");
});

const profData = async () => {
  try {
    const response = await fetch(URL + "user", {
      method: "GET",
      headers: { Authorization: `Basic ${encData}` }
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();

    profilePic.style.backgroundImage = `url(${result["avatar"]})`;
    myprofEmail.innerText = result["email"];
    myprofRegDate.innerText = dateFix(result["registration_date"]);
  } catch (error) {
    console.error(error);
  }
};
profData();

const getMyLots = async () => {
  try {
    const response = await fetch(URL + "lots/personal", {
      method: "GET",
      headers: { Authorization: `Basic ${encData}` }
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();
    console.log(result);

    if (result.length == 0) {
      myLotsForm.style.display = "none";
      myLots.innerHTML += `<span>Похоже, что Вы ещё не создавали никаких лотов!</span>`;
    } else {
      let num = 0;
      const myLotsArr = [];
      myLots.innerHTML += `<div class="userLots">`;
      result.forEach(item => {
        num++;
        item = `
        <form id="myLotForm${num}">
        <p><strong>${num}</strong></p>
        <label class="label lot_field" for="lot_name"
            ><span>Название лота: </span>
            <input
              class="inputName"
              type="text"
              name="lot_name"
              value="${item.name}"
              required
            />
          </label>
          <label class="label lot_field" for="lot_reqsum"
            ><span>Необходимая сумма: </span>
            <input
              class="inputReqSum"
              type="text"
              name="lot_reqsum"
              value="${item.amount}"
              required
            />
          </label>
          <label class="label lot_field" for="lot_currency"
            ><span>Валюта: </span>
                <input 
                type="text"
                name="lot_currency"
                value="${item.currency}"
                required
                />
          </label>
          <label class="label lot_field" for="lot_reqmonths"
            ><span>Срок, месяцев: </span>
            <input
              class="inputReqMonths"
              type="text"
              name="lot_reqmonths"
              value="${item.term}"
              required
            />
          </label>
          <label class="label lot_field" for="lot_percentage"
            ><span>Ставка, годовых: </span>
            <input
              type="text"
              name="lot_percentage"
              value="${item.percentage}"
              required
            />
          </label>
          <label class="label lot_field" for="lot_method"
            ><span>Метод погашения: </span>
            <!-- fix -->
            <input
              type="text"
              name="lot_method"
              value="${item.return_way}"
              required
            />
          </label>
          <label class="label lot_field" for="lot_security"
            ><span>Обеспечение: </span>
            <input
              type="text"
              name="lot_security"
              value="${item.security}"
              required
            />
          </label>
          <label class="label lot_field" for="lot_cred"
            ><span>Форма кредитирования: </span>
            <input
              type="text"
              name="lot_cred"
              value="${item.form}"
              required
            />
          </label>
          <label class="label lot_field" for="lot_shortdesc"
            ><span>Короткое описание: </span>
            <textarea
              name="lot_shortdesc"
            >${item.commentary}
            </textarea>
          </label>
          <button class="btn" id="deleteLot${item.id}">Удалить</button>
          <button class="btn" id="editLot${item.id}">Изменить</button>
          </form>
        `;
        myLotsArr.push(item);
      });
      myLots.innerHTML += myLotsArr.join("");
      myLots.innerHTML += `</div>`;
    }
  } catch (error) {
    console.error(error);
  }
};

getMyLots();

function clearLots() {
  let userLots = document.getElementsByName("userLots");
  for (let lot of userLots) {
    lot.parentNode.removeChild(lot);
  }
}

createLotPublish.addEventListener("click", async function(e) {
  e.preventDefault();
  if (createLotDescription.value == undefined) {
    createLotDescription.value = "";
  }
  const value = {
    name: createLotName.value,
    amount: createLotAmount.value,
    currency: createLotCurrency.value,
    term: createLotTerm.value,
    return_way: createLotReturnWay.value,
    security: createLotSecurity.value,
    form: createLotCredForm.value,
    percentage: createLotPercentage.value,
    commentary: createLotDescription.value
  };
  try {
    const response = await fetch(URL + "lots/createNew", {
      method: "POST",
      body: JSON.stringify(value),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Basic ${encData}`
      }
    });
    if (response.ok) {
      clearLots();
      getMyLots();
      modalWindow.style.display = "none";
      createLotCurrency.value = "";
      createLotName.value = "";
      createLotAmount.value = "";
      createLotTerm.value = "";
      createLotReturnWay.value = "";
      createLotSecurity.value = "";
      createLotCredForm.value = "";
      createLotPercentage.value = "";
      createLotDescription.value = "";
    } else throw new Error(error);
  } catch (error) {
    alert("Ошибка! Что-то пошло не так.");
    console.log(error);
  }
});
