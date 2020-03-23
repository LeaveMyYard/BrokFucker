const URL = "http://localhost:5000/api/v1/";
// const URL = `${window.location.host}/api/v1/`;

const myLotsHeading = document.getElementById("myLotsHeading");
const lotProfilePic = document.getElementById("lotProfilePic");
const myLotsContainer = document.querySelector(".my-lots");
const modalCloseBtn = document.getElementById("modalCloseBtn");
const modalWindow = document.getElementsByClassName("modal")[0];
const createLotBtn = document.getElementById("createLot");
const createLotPublish = document.getElementById("createLotPublish");
const myLotsBtn = document.getElementById("myLotsButton");
const archiveLotsBtn = document.getElementById("archiveLotsButton");
const myArchiveLotsContainer = document.querySelector(".my-lots-archived");

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
    location.href = "login.html";
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

const currencySelect = document.getElementById("currencySelect");
const currencySelectOptions = [];

async function currencyOptions() {
  try {
    const response = await fetch(URL + "lots/settings", {
      method: "GET",
      headers: { Authorization: `Basic ${encData()}` }
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }
    const result = await response.json();
    console.log(result);

    result.currency.forEach(
      curr =>
        (currencySelect.innerHTML += `<option value="${curr}">${curr}</option>`)
    );

    result.currency.forEach(curr => currencySelectOptions.push(curr));
  } catch (error) {
    console.error(error);
  }
}
currencyOptions();

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

    lotProfilePic.innerHTML = `<img src="${result["avatar"]}" style="width: 60%; height: 100%; margin-left: 20%"/>`;
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
          <a class="linkToLotPage" href="lot.html?id=${
            lot.id
          }">Страница лота</a>
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
                type="number"
                name="lot_reqsum"
                value="${lot.amount}"
                required
              />
            </label>
            <label class="label lot_field" for="lot_currency"
              ><span>Валюта: </span>
                  <select id="selectLotCurrency">
                    ${currencySelectOptions.map(curr => {
                      if (lot.currency == curr) {
                        return `<option selected value="${curr}">${curr}</option>`;
                      } else {
                        return `<option value="${curr}">${curr}</option>`;
                      }
                    })}
                  </select>
                  
            </label>
            <label class="label lot_field" for="lot_reqmonths"
              ><span>Срок, месяцев: </span>
              <input
                class="inputReqMonths"
                type="number"
                name="lot_reqmonths"
                value="${lot.term}"
                required
              />
            </label>
            <label class="label lot_field" for="lot_percentage"
              ><span>Ставка, годовых: </span>
              <input
                type="number"
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
            <div class="lot_photo">
            ${lot.photos.photos
              .map(photo => {
                return `<img height="300" src="${photo}"></img>`;
              })
              .join("")}  
            </div>
            <button class="deleteLotBtn btn">Remove</button>
            <button class="editLotBtn btn">Update</button>
            </div>
  `).get(0);
  console.log(lot.photos.photos.map(photo => console.log(photo)));

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
        currency: $(lotEl).find("#selectLotCurrency")[0].value,
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

const createArchiveLotAndListeners = async (
  lot,
  index,
  { parent: myArchiveLotsContainer, onLotRemove }
) => {
  const archiveLotEl = $(`
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
                type="number"
                name="lot_reqsum"
                value="${lot.amount}"
                required
              />
            </label>
            <label class="label lot_field" for="lot_currency"
              ><span>Валюта: </span>
                  <select id="selectLotCurrency">
                    ${currencySelectOptions.map(curr => {
                      if (lot.currency == curr) {
                        return `<option selected value="${curr}">${curr}</option>`;
                      } else {
                        return `<option value="${curr}">${curr}</option>`;
                      }
                    })}
                  </select>
                  
            </label>
            <label class="label lot_field" for="lot_reqmonths"
              ><span>Срок, месяцев: </span>
              <input
                class="inputReqMonths"
                type="number"
                name="lot_reqmonths"
                value="${lot.term}"
                required
              />
            </label>
            <label class="label lot_field" for="lot_percentage"
              ><span>Ставка, годовых: </span>
              <input
                type="number"
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
            <div class="lot_photo">
            ${lot.photos.photos
              .map(photo => {
                return `<img height="300" src="${photo}"></img>`;
              })
              .join("")}  
            </div>
            <button class="postLotBtn btn">Restore</button>
            </div>
  `).get(0);

  $(archiveLotEl)
    .find(".postLotBtn")
    .on("click", async function(event) {
      try {
        const response = await fetch(URL + `lots/${lot.id}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Basic ${encData()}`
          }
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

  return archiveLotEl;
};

const createArchiveLotEls = async (lots, { onLotRemove }) => {
  const lotEls = await Promise.all(
    lots.map(
      async (lot, index) =>
        await createArchiveLotAndListeners(lot, index, {
          parent: myArchiveLotsContainer,
          onLotRemove
        })
    )
  );

  return lotEls;
};

const manageArchiveLots = async sourceLots => {
  const lots = [...sourceLots];

  let lotEls = await createArchiveLotEls(lots, { onLotRemove });

  async function onLotRemove(lot, lotEl, i) {
    lots.splice(i, 1);
    lotEls.forEach(lotElToBeRemoved =>
      myArchiveLotsContainer.removeChild(lotElToBeRemoved)
    );

    lotEls = await createArchiveLotEls(lots, { onLotRemove });
    lotEls.forEach(lotEl => myArchiveLotsContainer.appendChild(lotEl));
  }

  lotEls.forEach(lotEl => myArchiveLotsContainer.appendChild(lotEl));
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
  try {
    const response = await fetch(URL + "lots/personal/deleted", {
      method: "GET",
      headers: { Authorization: `Basic ${encData()}` }
    });

    if (!response.ok) {
      throw new Error("Unsuccessfull response");
    }

    const result = await response.json();
    if (result.length == 0) {
      myLotsHeading.innerText = `Похоже, что у Вас нет архивных лотов!`;
    } else {
      manageArchiveLots(result);
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
  currencyOptionsFill();
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

  let newLotID = 0;
  const formData = new FormData();
  const photos = document.querySelector('input[type="file"][multiple]');
  for (let i = 0; i < photos.files.length; i++) {
    formData.append(
      `file${(Math.random() * 100000).toFixed(0)}`,
      photos.files[i]
    );
  }
  try {
    const response = await fetch(URL + "lots", {
      method: "POST",
      body: JSON.stringify(value),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Basic ${encData()}`
      }
    });
    if (response.ok) {
      const result = await response.json();
      newLotID = result["lot_id"];
      clearLots();
      myLotsHeading.innerHTML = `<strong>Мои лоты:</strong>`;
      modalWindow.style.display = "none";
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
  try {
    const response = await fetch(URL + "lots/" + newLotID + "/photos", {
      method: "POST",
      body: formData,
      headers: {
        Authorization: `Basic ${encData()}`
      }
    });
    for (let key of formData.keys()) {
      formData.delete(key);
    }
    getMyLots();
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

archiveLotsBtn.addEventListener("click", function(e) {
  e.preventDefault();
  myLotsBtn.classList.remove("btnActive");
  archiveLotsBtn.classList.add("btnActive");
  myLotsContainer.style.display = "none";
  myArchiveLotsContainer.style.display = "block";
});

myLotsBtn.addEventListener("click", function(e) {
  e.preventDefault();
  archiveLotsBtn.classList.remove("btnActive");
  myLotsBtn.classList.add("btnActive");
  myLotsContainer.style.display = "block";
  myArchiveLotsContainer.style.display = "none";
});
