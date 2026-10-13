import { test } from "node:test";
import assert from "node:assert/strict";
import {
  emptyRules,
  fromRequired,
  validateRules,
  ruleText,
  logicText,
  changeOperator,
  matchesRules,
  moveRule,
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

test("live draft preview follows nested logic without changing it", () => {
  const rule = {
    op: "and",
    children: [
      { op: "or", children: [course("CS:101"), course("CS:102")] },
      {
        op: "not",
        children: [
          { op: "and", children: [course("CS:101"), course("CS:102")] },
        ],
      },
    ],
  };
  assert.equal(matchesRules(rule, new Set(["CS:101"])), true);
  assert.equal(matchesRules(rule, new Set(["CS:101", "CS:102"])), false);
  assert.equal(matchesRules(rule, new Set()), false);
});
test("moving an existing subtree preserves its meaning and prevents cycles", () => {
  const rule = {
    op: "and",
    children: [course("CS:101"), { op: "or", children: [course("CS:102")] }],
  };
  const moved = moveRule(rule, [0], [1]);
  assert.deepEqual(moved, {
    op: "and",
    children: [{ op: "or", children: [course("CS:102"), course("CS:101")] }],
  });
  assert.equal(rule.children.length, 2);
  assert.throws(() => moveRule(rule, [1], [1]), /inside itself/);
  assert.throws(
    () =>
      moveRule(
        {
          op: "and",
          children: [
            course("CS:101"),
            { op: "not", children: [course("CS:102")] },
          ],
        },
        [0],
        [1],
      ),
    /another expression/,
  );
});
test("blank course pickers can save but cannot generate accidental constraints", () => {
  const draft = course("");
  assert.deepEqual(validateRules(draft, keys, true), draft);
  assert.throws(() => validateRules(draft, keys), /Choose a course/);
});

test("compact notation keeps nested grouping explicit", () => {
  const rule = {
    op: "and",
    children: [
      { op: "or", children: [course("CS:101"), course("CS:102")] },
      course("CS:101", false),
    ],
  };
  assert.equal(logicText(rule), "((CS 101 OR CS 102) AND NOT CS 101)");
});

test("negating an existing OR group preserves its original scope", () => {
  const original = { op: "or", children: [course("CS:101"), course("CS:102")] };
  const excluded = changeOperator(original, "not");
  assert.deepEqual(excluded, { op: "not", children: [original] });
  assert.equal(matchesRules(excluded, new Set(["CS:101"])), false);
  assert.equal(matchesRules(excluded, new Set()), true);
  assert.equal(original.op, "or");
});
