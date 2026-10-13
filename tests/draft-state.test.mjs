import { test } from "node:test";
import assert from "node:assert/strict";
import { readCreditRange } from "../static/draft-state.js";
test("half-edited empty credit fields do not replace the last valid saved range", () => {
  assert.equal(readCreditRange("", "18"), null);
  assert.equal(readCreditRange("12", ""), null);
});
test("temporary reversed and out-of-bounds ranges are rejected without damaging a draft", () => {
  for (const range of [
    ["22", "18"],
    ["-1", "18"],
    ["12", "31"],
    ["NaN", "18"],
    ["12", "Infinity"],
  ])
    assert.equal(readCreditRange(...range), null);
});
test("valid zero and fractional credit ranges are preserved", () => {
  assert.deepEqual(readCreditRange("0", "0"), { min: 0, max: 0 });
  assert.deepEqual(readCreditRange("12.5", "18.5"), { min: 12.5, max: 18.5 });
});
