# Making a flexible Boolean editor understandable

## The mental model

A student selects a pool of sections. A condition asks whether one course is present. A group decides how its conditions connect. Nested groups describe a choice inside a larger choice. That is the explanation users need before they need the term “Boolean.”

Preserve one expression tree as the source of truth. The visual blocks, exact-logic preview, draft evaluation, saved JSON, and solver must refer to the same tree. Do not implement a simplified editor with an unrelated advanced syntax mode: two versions of a rule would eventually disagree.

## Vocabulary that exposes the important distinctions

| User-facing language | Operator | Meaning |
| --- | --- | --- |
| All of these | AND | Every child must match |
| At least one | OR | One or more children must match; both are allowed |
| Exclude this pattern | NOT | The enclosed expression must fail |
| Course is included | Positive leaf | Any shortlisted section of the course is present |
| Course is left out | Negative leaf | No section of the course is present |

Avoid “must take A” on a leaf inside an OR group. A is one way to satisfy the choice, not independently required. Avoid “either/or” without explaining whether both are allowed. Avoid calling NOT “exclude these courses”: NOT(A AND B) excludes taking them together, while NOT(A OR B) excludes either course individually.

AND and OR are symmetric, and their children can be reordered without changing meaning. Moving a child across a group boundary can change meaning, so the current-week feedback must refresh immediately and the operation must be undoable.

## Information hierarchy

1. Clear, colored group boundaries show scope. Layout, labels, and nesting explain structure without relying on color alone.
2. Short labels say what a group does; a sentence directly under each header explains it.
3. Course rows expose the selected course and included/left-out condition.
4. Live badges show whether a condition/group matches the current week. The overall preview explicitly names that week.
5. A compact parenthesized formula exposes exact logic for inspection.
6. Examples and block-management controls are available on demand, reducing always-visible machinery.

A mismatch is not a syntax error and does not mean no solution exists. The current week is one example schedule. Use separate feedback for unfinished blocks, absent shortlist references, and a valid rule that the example week does not satisfy. Do not label the preview “rules satisfied” without identifying the schedule being checked.

## Construction and reversibility

New course rows start with an explicit picker rather than silently requiring the first course. A group palette offers AND, OR, and an exclusion combination. The exclusion shortcut builds NOT(AND(...)); the inner operator remains editable to OR or any further nesting.

Block actions live in a menu: reorder, move into a group, or remove. Dragging remains available, with a destination highlight, but keyboard and touch users can move existing blocks through the menu. Disallow cycles and inserting a second expression directly into NOT. Students can first create an AND/OR container when they need multiple conditions under negation.

“Group the whole expression” permits wrapping any expression in AND, OR, or NOT. This matters when the root is already NOT or when an imported root is a single course. Without wrapping, the editor would expose the underlying operators but still make some valid trees difficult or impossible to construct.

Undo/Redo remembers the last 20 edits in this session, including resets and moves. It does not cross a reload or an imported draft boundary. Undo is necessary because changing a group operator or moving a subtree can affect many schedules at once.

## Full flexibility, with explainable limits

Keep arbitrary combinations of AND, OR, NOT, and positive/negative course leaves. Nesting remains available to 8 levels with 80 blocks, protecting imports and bounded search. These are resource limits, not a restriction to a flat rule form.

Do not flatten nested negation just because it looks complicated. It is valid and may be intentional. Future optional simplification can show an equivalent preview before an explicit user action, with undo. Do not automatically switch inclusive OR to exclusive OR.

Exactly one of A and B remains expressible as `(A OR B) AND NOT (A AND B)`. A future “exactly one” shortcut should behave as a clearly named group with linked course choices; merely inserting duplicate editable predicates can lose its intended relationship when one copy is edited. That shortcut is deferred until it can be edited without this ambiguity.

## Useful next validation

Test comprehension with students using these tasks, without explaining the operators first:

- Require A and either B or C, allowing both B and C.
- Allow either A or B but prohibit taking both.
- Prohibit taking C and D together while allowing either alone.
- Wrap an existing expression and add another alternative.
- Move a condition into a different group and predict the changed result.
- Explain why the current week fails a valid rule, then make it match.
- Restore a course after removing its last shortlisted section.

Observe whether students can predict accepted schedules, not just create attractive blocks. The changes in this iteration are reasoned design choices and implementation checks; they are not a claim of usability validation with actual students.
