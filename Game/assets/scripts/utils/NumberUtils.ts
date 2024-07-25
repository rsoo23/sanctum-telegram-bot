/*
billions: 2 d.p.
hundred / ten millions: 1 d.p.
millions: 2 d.p.
*/

function formatNumber(number: number): string {
  const sign = number < 0 ? "-" : "";
  const absNumber = Math.abs(number);

  if (absNumber >= 999999999) {
    const formattedNumber = (absNumber / 1000000000)
      .toFixed(2)
      .replace(".", ".");
    return sign + formattedNumber + "B";
  } else if (absNumber >= 9999999) {
    const formattedNumber = (absNumber / 1000000).toFixed(1).replace(".", ".");
    return sign + formattedNumber + "M";
  } else if (absNumber >= 999999) {
    const formattedNumber = (absNumber / 1000000).toFixed(2).replace(".", ".");
    return sign + formattedNumber + "M";
  } else if (absNumber >= 99999) {
    const formattedNumber = (absNumber / 1000).toFixed(0).replace(".", ".");
    return sign + formattedNumber + "K";
  } else if (absNumber >= 10000) {
    const formattedNumber = (absNumber / 1000).toFixed(1).replace(".", ".");
    return sign + formattedNumber + "K";
  } else if (absNumber >= 1000) {
    return sign + absNumber.toLocaleString("en-US");
  } else {
    return sign + absNumber.toString();
  }
}

export { formatNumber };
