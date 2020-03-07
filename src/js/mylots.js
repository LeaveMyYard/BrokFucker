const URL = "http://localhost:5000/api/v1/";

const myLotsHeading = document.getElementById("myLotsHeading");
const lotProfilePic = document.getElementById("lotProfilePic");
const myLotsContainer = document.querySelector(".my-lots");
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

function onReady() {
  if (!localStorage.getItem("email") && !sessionStorage.getItem("email")) {
    location.href = "login.html";
  }
}
onReady();

lotProfilePic.addEventListener("click", function() {
  location.href = "my_profile.html";
});

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
      headers: { Authorization: `Basic ${encData()}` }
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();

    lotProfilePic.style.backgroundImage = `url(${result["avatar"]})`;
    myprofEmail.innerText = result["email"];
    myprofRegDate.innerText = dateFix(result["registration_date"]);
  } catch (error) {
    console.error(error);
  }
};
profData();

const createLotAndListeners = async (
  lot,
  index,
  { parent: myLotsContainer, onLotRemove }
) => {
  const lotEl = $(`
        <div class="userLots" data-id="myLotForm__${index + 1}">
          <form>
          <p><strong>${index + 1}</strong></p>
          <label class="label lot_field" for="lot_name"
              ><span>Название лота: </span>
              <input
                class="inputName"
                type="text"
                name="lot_name"
                value="${lot.name}"
                required
              />
            </label>
            <label class="label lot_field" for="lot_reqsum"
              ><span>Необходимая сумма: </span>
              <input
                class="inputReqSum"
                type="text"
                name="lot_reqsum"
                value="${lot.amount}"
                required
              />
            </label>
            <label class="label lot_field" for="lot_currency"
              ><span>Валюта: </span>
                  <input
                  type="text"
                  name="lot_currency"
                  value="${lot.currency}"
                  required
                  />
            </label>
            <label class="label lot_field" for="lot_reqmonths"
              ><span>Срок, месяцев: </span>
              <input
                class="inputReqMonths"
                type="text"
                name="lot_reqmonths"
                value="${lot.term}"
                required
              />
            </label>
            <label class="label lot_field" for="lot_percentage"
              ><span>Ставка, годовых: </span>
              <input
                type="text"
                name="lot_percentage"
                value="${lot.percentage}"
                required
              />
            </label>
            <label class="label lot_field" for="lot_method"
              ><span>Метод погашения: </span>
              <!-- fix -->
              <input
                type="text"
                name="lot_method"
                value="${lot.return_way}"
                required
              />
            </label>
            <label class="label lot_field" for="lot_security"
              ><span>Обеспечение: </span>
              <input
                type="text"
                name="lot_security"
                value="${lot.security}"
                required
              />
            </label>
            <label class="label lot_field" for="lot_cred"
              ><span>Форма кредитирования: </span>
              <input
                type="text"
                name="lot_cred"
                value="${lot.form}"
                required
              />
            </label>
            <label class="label lot_field" for="lot_shortdesc"
              ><span>Короткое описание: </span>
              <textarea
                name="lot_shortdesc"
              >${lot.commentary}
              </textarea>
            </label>
            </form>
            <button class="deleteLotBtn btn">Remove</button>
            <button class="editLotBtn btn">Update</button>
            </div>
  `).get(0);

  $(lotEl)
    .find(".deleteLotBtn")
    .on("click", async function(event) {
      try {
        const response = await fetch(URL + `lots/${lot.id}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Basic ${encData()}`
          }
        });
        if (response.ok) {
          onLotRemove(lot, lotEl, index);
        } else throw new Error(error);
      } catch (error) {
        alert("Ошибка! Что-то пошло не так.");
        console.log(error);
      }
    });

  $(lotEl)
    .find(".editLotBtn")
    .on("click", async function(event) {
      const value = {
        name: $(lotEl).find("input[name=lot_name]")[0].value,
        amount: $(lotEl).find("input[name=lot_reqsum]")[0].value,
        currency: $(lotEl).find("input[name=lot_currency]")[0].value,
        term: $(lotEl).find("input[name=lot_reqmonths]")[0].value,
        return_way: $(lotEl).find("input[name=lot_method]")[0].value,
        security: $(lotEl).find("input[name=lot_security]")[0].value,
        form: $(lotEl).find("input[name=lot_cred]")[0].value,
        percentage: $(lotEl).find("input[name=lot_percentage]")[0].value,
        commentary: $(lotEl).find("textarea[name=lot_shortdesc]")[0].value
      };
      try {
        const response = await fetch(URL + `lots/${lot.id}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Basic ${encData()}`
          },
          body: JSON.stringify(value)
        });
        if (response.ok) {
          console.log(response);

          window.location.reload();
        } else throw new Error(error);
      } catch (error) {
        alert("Ошибка! Что-то пошло не так.");
        console.log(error);
      }
    });

  return lotEl;
};

const createLotEls = async (lots, { onLotRemove }) => {
  const lotEls = await Promise.all(
    lots.map(
      async (lot, index) =>
        await createLotAndListeners(lot, index, {
          parent: myLotsContainer,
          onLotRemove
        })
    )
  );

  return lotEls;
};

const manageLots = async sourceLots => {
  const lots = [...sourceLots];

  let lotEls = await createLotEls(lots, { onLotRemove });

  async function onLotRemove(lot, lotEl, i) {
    lots.splice(i, 1);
    lotEls.forEach(lotElToBeRemoved =>
      myLotsContainer.removeChild(lotElToBeRemoved)
    );

    lotEls = await createLotEls(lots, { onLotRemove });
    lotEls.forEach(lotEl => myLotsContainer.appendChild(lotEl));
  }

  lotEls.forEach(lotEl => myLotsContainer.appendChild(lotEl));
};

const getMyLots = async () => {
  try {
    const response = await fetch(URL + "lots/personal", {
      method: "GET",
      headers: { Authorization: `Basic ${encData()}` }
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();
    if (result.length == 0) {
      myLotsHeading.innerText = `Похоже, что у Вас ещё нет лотов!`;
    } else {
      manageLots(result);
    }
  } catch (error) {
    console.error(error);
  }
};

getMyLots();

async function clearLots() {
  let userLots = document.getElementsByClassName("userLots");

  [...userLots].forEach(lot => {
    lot.parentNode.removeChild(lot);
  });
}

createLotPublish.addEventListener("click", async function(e) {
  e.preventDefault();
  if ($("#createLotForm").valid() == false) {
    return;
  }
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
        Authorization: `Basic ${encData()}`
      }
    });
    if (response.ok) {
      clearLots();
      getMyLots();
      myLotsHeading.innerHTML = `<strong>Мои лоты:</strong>`;
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

const validateForm = $(function() {
  $("#createLotForm").validate({
    rules: {
      create_lot_name: {
        required: true
      },
      create_lot_reqsum: {
        required: true,
        number: true
      },
      create_lot_currency: {
        required: true
      },
      create_lot_reqmonths: {
        required: true,
        number: true
      },
      create_lot_percentage: {
        required: true,
        number: true
      },
      create_lot_method: {
        required: true
      },
      create_lot_security: {
        required: true
      },
      create_lot_cred: {
        required: true
      }
    }
  });
});

createLotPublish.addEventListener("change", validateForm);
