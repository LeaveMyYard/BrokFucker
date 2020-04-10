export default function dateFix(date) {
  let givenDate = new Date(date.replace(/ /g, "T"));
  let day = givenDate.getDate();
  let month = givenDate.getMonth();
  let year = givenDate.getFullYear();
  return `${day}.${month + 1}.${year}`;
}
