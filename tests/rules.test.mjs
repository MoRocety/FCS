import { test } from "node:test";
import assert from "node:assert/strict";
import {
  emptyRules,
  fromRequired,
  validateRules,
  ruleText,
} from "../static/rule-builder.js";
const keys = new Set(["CS:101", "CS:102"]);
const course = (key, present = true) => ({
  op: "course",
  course_key: key,
  present,
});
test("v1 required courses migrate to explicit AND predicates", () => {
  assert.deepEqual(fromRequired(["CS:101"]), {
    op: "and",
    children: [course("CS:101")],
  });
  assert.deepEqual(validateRules(emptyRules(), keys), emptyRules());
});
test("nested expression keeps grouping and absence semantics", () => {
  const rule = {
    op: "not",
    children: [
      { op: "or", children: [course("CS:101"), course("CS:102", false)] },
    ],
  };
  assert.deepEqual(validateRules(rule, keys), rule);
  assert.equal(
    ruleText(rule),
    "NOT ((CS 101 is in the schedule OR CS 102 is not in the schedule))",
  );
});
test("a missing shortlisted course is never silently removed", () => {
  assert.throws(
    () => validateRules(course("CS:102"), new Set(["CS:101"])),
    /shortlist/,
  );
});
test("incomplete editor drafts can restore but cannot generate", () => {
  const rule = { op: "and", children: [{ op: "or", children: [] }] };
  assert.deepEqual(validateRules(rule, keys, true), rule);
  assert.throws(() => validateRules(rule, keys), /empty group/);
});
test("NOT requires one child and block limits protect imports", () => {
  assert.throws(
    () =>
      validateRules(
        { op: "not", children: [course("CS:101"), course("CS:102")] },
        keys,
      ),
    /exactly one/,
  );
  assert.throws(
    () =>
      validateRules(
        { op: "and", children: Array(80).fill(course("CS:101")) },
        keys,
      ),
    /80 blocks/,
  );
  let deep = course("CS:101");
  for (let i = 0; i < 8; i++) deep = { op: "not", children: [deep] };
  assert.throws(() => validateRules(deep, keys), /8 levels/);
});
test("imported predicates must be typed data, with no executable fields", () => {
  assert.throws(
    () => validateRules({ ...course("CS:101"), present: "false" }, keys),
    /predicate/,
  );
  assert.throws(
    () => validateRules({ ...course("CS:101"), script: "x" }, keys),
    /predicate/,
  );
});
