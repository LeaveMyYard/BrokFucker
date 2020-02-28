const URL = "http://localhost:5000/api/v1/";
const lotTable = document.getElementById("lotTable");

fetch(URL + "lots/approved")
  .then(response => {
    if (!response.ok) {
      return Promise.reject(Error("Unsuccessfull response"));
    }
    return response.json().then(({ results: lots }) => {
      // lotTable.innerHTML = getLots(lots);
      console.log(lots);
    });
  })

  //onReject
  .catch(err => {
    console.log(err);
  });

// function queryApi(endpoint) {
//   return fetch(URL + endpoint).then(response => {
//     return response.ok
//       ? response.json()
//       : Promise.reject(Error(`Unsuccessfull response`));
//   });
// }
// Promise.all([queryApi("films"), queryApi("planets")])
//   .then(([{ results: films }, { results: planets }]) => {
//     output.textContent = `${films.length} films, ${planets.length} planets`;
//   })
//   .catch(error => {
//     console.log(error);
//     output.innerHTML = ":)";
//   })
