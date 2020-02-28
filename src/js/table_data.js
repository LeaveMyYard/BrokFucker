const URL = "http://localhost:5000/api/v1/";

const lotTable = document.getElementById("lotTable");

function dateFix(date) {
  let lotDate = new Date(date);
  let day = lotDate.getDate();
  let month = lotDate.getMonth();
  let year = lotDate.getFullYear() % 100;
  return `${day}/${month + 1}/${year}`;
}

const myFunc = async () => {
  try {
    const response = await fetch(URL + "lots/approved");

    if (!response.ok) {
      return Promise.reject(Error("Unsuccessfull response"));
    }

    const result = await response.json();
    console.log(result);
    const lotArr = [];
    result.forEach(item => {
      item = `
      <tr>
      <td>${dateFix(item.date)}</td>
      <td>${item.name}</td>
      <td>${item.user}</td>
      <td>${item.amount}</td>
      <td>${item.currency}</td>
      <td>${item.term}</td>
      <td>${item.return_way}</td>
      <td>${item.security}</td>
      <td>${item.percentage}</td>
      <td>${item.form}</td>
      <td>${item.security_checked}</td>
      <td>${item.guarantee_percentage}</td>
      </tr>`;
      lotArr.push(item);
    });
    console.log(lotArr);

    lotTable.innerHTML += lotArr.join("");
  } catch (error) {
    console.error(error);
  }
};

myFunc();
