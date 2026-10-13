// Keep the last valid range while a student is partway through editing fields.
export function readCreditRange(minimumText, maximumText) {
  if (minimumText === "" || maximumText === "") return null;
  const minimum = Number(minimumText),
    maximum = Number(maximumText);
  return Number.isFinite(minimum) &&
    Number.isFinite(maximum) &&
    minimum >= 0 &&
    maximum <= 30 &&
    minimum <= maximum
    ? { min: minimum, max: maximum }
    : null;
}
