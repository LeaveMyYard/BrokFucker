const URL = "http://localhost:5000/api/v1/";

const myLotsHeading = document.getElementById("myLotsHeading");
const lotProfilePic = document.getElementById("lotProfilePic");
const myLotsContainer = document.querySelector(".my-lots");
const modalCloseBtn = document.getElementById("modalCloseBtn");
const modalWindow = document.getElementsByClassName("modal")[0];
const createLotBtn = document.getElementById("createLot");
const createLotPublish = document.getElementById("createLotPublish");

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

document.querySelector(".inputReqSum").addEventListener("input", e => {
  e.target.value = e.target.value.replace(/\D/g, "");
});
document.querySelector(".inputReqMonths").addEventListener("input", e => {
  e.target.value = e.target.value.replace(/\D/g, "");
});
document.querySelector(".inputReqPercentage").addEventListener("input", e => {
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
            <div class="lot_photo" style="background-image: url(${
              lot.photos.photos
            })">
            </div>
            <button class="deleteLotBtn btn">Удалить из избранных</button>
            </div>
  `).get(0);
  console.log(lot.photos.photos.forEach(photo => console.log(photo)));

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
        // photo: $(lotEl).find('input[name=file]')[0]
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

const getMyFavLots = async () => {
  try {
    const response = await fetch(URL + "lots/favorites", {
      method: "GET",
      headers: { Authorization: `Basic ${encData()}` }
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();
    if (result.length == 0) {
      myLotsHeading.innerText = `Похоже, что у Вас нет избранных лотов!`;
    } else {
      manageLots(result);
    }
  } catch (error) {
    console.error(error);
  }
};

getMyFavLots();

async function clearLots() {
  let userLots = document.getElementsByClassName("userLots");

  [...userLots].forEach(lot => {
    lot.parentNode.removeChild(lot);
  });
}
