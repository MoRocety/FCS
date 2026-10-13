# Nested schedule rules

The shortlist is the pool of possible sections. Rules describe which courses a generated schedule must or must not contain. All existing credit, duplicate-section, and time-clash rules still apply.

## Build an expression

- Add a course condition, choose a shortlisted course, and choose “is in schedule” or “is not in schedule.” A course predicate matches any shortlisted section of that course.
- AND requires all child expressions to match.
- OR requires at least one child expression to match. It permits both; exactly one is expressible as `(A OR B) AND NOT (A AND B)`.
- NOT reverses one expression. To negate several conditions, put an AND or OR group inside it. Switching a multi-condition group to NOT keeps its previous AND/OR operator inside the negation, so the whole original pattern is inverted.
- Add nested groups at any group level. Drag blocks into another group to move them, or use arrows to reorder siblings. Touch/keyboard users can create conditions directly inside the desired group.
- “Reads as” shows the expression with parentheses. Empty groups show an error and cannot be used for generation. An empty root AND means no additional course rules.

For example, `(COMP 102 OR MATH 100) AND NOT (BIOL 100 AND PSYC 100)` asks for at least one of the first two courses and excludes schedules containing both of the latter two.

Removing a course from the shortlist does not silently delete its rules. Those blocks remain visible with a missing-shortlist label. Restore an option for the course, change the rule, or remove the block before generating.

## Representation and evaluation

The expression is typed JSON, never an executable expression string:

```json
{
  "op": "and",
  "children": [
    {"op": "or", "children": [
      {"op": "course", "course_key": "COMP:102", "present": true},
      {"op": "course", "course_key": "MATH:100", "present": true}
    ]},
    {"op": "course", "course_key": "BIOL:100", "present": false}
  ]
}
```

`POST /api/v1/schedules/generate` accepts this under `rules`. The API checks structure, operators, course references, and limits of 8 levels and 80 blocks. Legacy `required_course_keys` continues to work; if both fields are sent, both sets of conditions apply.

The solver uses three-valued evaluation during backtracking: true, false, or undecided. A branch is discarded only when the expression is definitely false. Pending courses remain undecided, including under NOT. At completed schedules, all predicates have a definite value.

Browser storage retains its existing per-term key so prior drafts can be found. Version 1 drafts migrate their required courses into an AND group. New exports and saved drafts use version 2 and preserve the expression tree under `rules`. Incomplete editor groups can be saved and restored but cannot be submitted for generation.

The leaf type currently covers course membership. Future predicate types can cover specific sections, instructors, time windows, or workload without replacing the Boolean group model. Each new leaf type will need matching validation, UI, and scheduling semantics.

The refined editor includes explicit course placeholders, live current-week matching, compact notation, Undo/Redo, named destination groups, and a keyboard move menu. See [the UI design rationale](RULE_EDITOR_DESIGN.md).
