export default function Translate(data) {
  const vocabulary = {
    cash: "Наличные",
    cashless: "Безналичные",
    any: "Любой",
    every_month: "Ежемесячно",
    term_end: "Окончание срока",
    other: "Другое",
  };

  return vocabulary[data];
}
