// Shared, data-only rule representation. No executable strings or expressions.
export const emptyRules = () => ({ op: "and", children: [] });
export const fromRequired = (keys) => ({
  op: "and",
  children: keys.map((course_key) => ({
    op: "course",
    course_key,
    present: true,
  })),
});
export function validateRules(rule, courseKeys, allowIncomplete = false) {
  let count = 0;
  function visit(node, depth, root = false) {
    if (++count > 80 || depth > 8)
      throw new Error("Rules allow at most 8 levels and 80 blocks.");
    if (!node || typeof node !== "object" || Array.isArray(node))
      throw new Error("Invalid rule block.");
    if (node.op === "course") {
      if (
        Object.keys(node).sort().join(",") !== "course_key,op,present" ||
        typeof node.course_key !== "string" ||
        typeof node.present !== "boolean"
      )
        throw new Error("Invalid course predicate.");
      if (!node.course_key && !allowIncomplete)
        throw new Error(
          "Choose a course for each condition before generating.",
        );
      if (node.course_key && !courseKeys.has(node.course_key))
        throw new Error(
          "Every rule course needs a section in your shortlist. Restore the course or edit its rule.",
        );
      return { ...node };
    }
    if (
      !["and", "or", "not"].includes(node.op) ||
      Object.keys(node).sort().join(",") !== "children,op" ||
      !Array.isArray(node.children)
    )
      throw new Error("Invalid rule group.");
    if (
      node.op === "not" &&
      (node.children.length > 1 ||
        (!allowIncomplete && node.children.length !== 1))
    )
      throw new Error("NOT needs exactly one expression.");
    if (
      !allowIncomplete &&
      !node.children.length &&
      !(root && node.op === "and")
    )
      throw new Error("Add a rule to each group, or remove the empty group.");
    return {
      op: node.op,
      children: node.children.map((child) => visit(child, depth + 1)),
    };
  }
  return visit(rule, 1, true);
}
export function ruleText(rule, root = true) {
  if (rule.op === "course")
    return `${rule.course_key ? rule.course_key.replace(":", " ") : "[choose a course]"} ${rule.present ? "is in the schedule" : "is not in the schedule"}`;
  if (!rule.children.length)
    return root && rule.op === "and"
      ? "No extra rules — any schedule within your credit range."
      : `empty ${rule.op.toUpperCase()} group`;
  if (rule.op === "not")
    return `NOT (${rule.children.map((child) => ruleText(child, false)).join("")})`;
  return `(${rule.children.map((child) => ruleText(child, false)).join(` ${rule.op.toUpperCase()} `)})`;
}
export function logicText(rule, root = true) {
  if (rule.op === "course") {
    const code = rule.course_key.replace(":", " ") || "[choose a course]";
    return rule.present ? code : `NOT ${code}`;
  }
  if (!rule.children.length)
    return root && rule.op === "and"
      ? "No extra course restrictions"
      : `[empty ${rule.op.toUpperCase()}]`;
  if (rule.op === "not") return `NOT (${logicText(rule.children[0], false)})`;
  return `(${rule.children.map((child) => logicText(child, false)).join(` ${rule.op.toUpperCase()} `)})`;
}
export function matchesRules(rule, courseKeys) {
  if (rule.op === "course")
    return rule.present === courseKeys.has(rule.course_key);
  if (rule.op === "not") return !matchesRules(rule.children[0], courseKeys);
  return rule.op === "and"
    ? rule.children.every((child) => matchesRules(child, courseKeys))
    : rule.children.some((child) => matchesRules(child, courseKeys));
}
export function changeOperator(node, nextOperator) {
  const previousOperator = node.op;
  return {
    op: nextOperator,
    children:
      nextOperator === "not" && node.children.length > 1
        ? [{ op: previousOperator, children: structuredClone(node.children) }]
        : structuredClone(node.children),
  };
}
export function moveRule(root, source, destination) {
  const next = structuredClone(root);
  const at = (path) => path.reduce((node, index) => node.children[index], next);
  if (
    !source.length ||
    (destination.length >= source.length &&
      source.every((value, i) => destination[i] === value))
  )
    throw new Error("A group cannot be moved inside itself.");
  const parent = at(source.slice(0, -1)),
    target = at(destination),
    node = at(source);
  if (!target.children || (target.op === "not" && target.children.length))
    throw new Error(
      "This group cannot accept another expression. Add an AND or OR group first.",
    );
  parent.children.splice(source.at(-1), 1);
  target.children.push(node);
  return next;
}
export function mountRuleBuilder({
  element,
  getRules,
  setRules,
  getCourses,
  getPreviewKeys = () => new Set(),
  onChange,
}) {
  const esc = (v) =>
    String(v).replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  const pathString = (path) => path.join(".");
  const at = (root, path) =>
    path.reduce((node, index) => node.children[index], root);
  const pathOf = (value) => (value === "" ? [] : value.split(".").map(Number));
  let dragged = null;
  let lastSignature = null;
  const past = [],
    future = [];
  function groups(node = getRules(), path = [], items = []) {
    if (node.children) {
      items.push({
        path,
        name: path.length
          ? `Group ${items.length} · ${{ and: "all", or: "at least one", not: "excluded pattern" }[node.op]}`
          : "All rules",
        node,
      });
      node.children.forEach((child, index) =>
        groups(child, [...path, index], items),
      );
    }
    return items;
  }
  function commit(next, focusPath = null, remember = true) {
    // Structural limit also applies to incomplete blocks while editing.
    let count = 0;
    function within(node, depth) {
      return (
        ++count <= 80 &&
        depth <= 8 &&
        (node.children || []).every((child) => within(child, depth + 1))
      );
    }
    if (!within(next, 1)) {
      element.dispatchEvent(
        new CustomEvent("rule-error", {
          detail: "Rules allow at most 8 levels and 80 blocks.",
        }),
      );
      return;
    }
    if (remember) {
      past.push(structuredClone(getRules()));
      if (past.length > 20) past.shift();
      future.length = 0;
    }
    lastSignature = JSON.stringify(next);
    setRules(next);
    render();
    onChange();
    if (focusPath !== null)
      element
        .querySelector(
          `[data-path="${focusPath}"] select, [data-path="${focusPath}"] button`,
        )
        ?.focus();
  }
  function renderNode(node, path = [], depth = 0) {
    const p = pathString(path),
      root = path.length === 0;
    const drag = root ? "" : `draggable="true"`;
    let matchBadge = "";
    try {
      if (!root && node.children && !node.children.length)
        throw new Error("Incomplete");
      validateRules(node, new Set(getCourses().map((course) => course.key)));
      const matches = matchesRules(node, getPreviewKeys());
      matchBadge = `<span class="block-match ${matches ? "yes" : "no"}" title="${matches ? "Matches" : "Does not match"} your current week" aria-label="${matches ? "Matches" : "Does not match"} your current week">${matches ? "✓ matches" : "○ doesn't match"}</span>`;
    } catch {
      matchBadge = '<span class="block-match pending">unfinished</span>';
    }

    const destinations = groups().filter(
      (group) =>
        !(
          group.path.length >= path.length &&
          path.every((value, i) => group.path[i] === value)
        ) && !(group.node.op === "not" && group.node.children.length),
    );
    const move = root
      ? ""
      : `<span class="block-handle" aria-hidden="true" title="Drag this block to another group">⠿</span><details class="block-menu"><summary aria-label="Block actions">•••</summary><div class="block-menu-body"><button type="button" data-rule-action="up" data-path="${p}">Move up</button><button type="button" data-rule-action="down" data-path="${p}">Move down</button><label>Move into<select data-rule-field="move" data-path="${p}" aria-label="Move block into a group"><option value="">Choose a group…</option>${destinations.map((group) => `<option value="@${pathString(group.path)}">${esc(group.name || "All rules")}</option>`).join("")}</select></label><button type="button" data-rule-action="remove" data-path="${p}" class="remove-block">Remove block</button></div></details>`;
    if (node.op === "course") {
      const courses = getCourses();
      const missing =
        node.course_key && !courses.some((c) => c.key === node.course_key);
      return `<div class="rule-block course-rule" data-path="${p}" ${drag}><span class="block-kind">COURSE</span><select data-rule-field="course" data-path="${p}" aria-label="Course for rule"><option value="" ${!node.course_key ? "selected" : ""}>Choose a course…</option>${missing ? `<option value="${esc(node.course_key)}">${esc(node.course_key.replace(":", " "))} — not shortlisted</option>` : ""}${courses.map((c) => `<option value="${esc(c.key)}" ${node.course_key === c.key ? "selected" : ""}>${esc(c.label)}</option>`).join("")}</select><select data-rule-field="present" data-path="${p}" aria-label="Course condition"><option value="true" ${node.present ? "selected" : ""}>is included</option><option value="false" ${!node.present ? "selected" : ""}>is left out</option></select><span class="block-actions">${matchBadge}${move}</span></div>`;
    }
    const groupLabel =
      groups()
        .find((group) => pathString(group.path) === p)
        ?.name.split(" ·")[0] || "";
    return `<div class="rule-group rule-${node.op}" data-path="${p}" data-drop-group="${p}" ${drag} style="--rule-depth:${depth}"><div class="rule-group-heading"><select data-rule-field="operator" data-path="${p}" aria-label="Group operator"><option value="and" ${node.op === "and" ? "selected" : ""}>All of these (AND)</option><option value="or" ${node.op === "or" ? "selected" : ""}>At least one (OR)</option><option value="not" ${node.op === "not" ? "selected" : ""}>Exclude this pattern (NOT)</option></select><span class="block-actions">${matchBadge}${root ? '<span class="root-label">YOUR RULES</span>' : `<span class="group-id">${esc(groupLabel)}</span>${move}`}</span></div><p class="group-explanation">${{ and: "Every condition below must match.", or: "One or more conditions must match. Both are allowed.", not: "Reject a schedule when the pattern inside matches." }[node.op]}</p><div class="rule-children">${node.children.map((child, i) => renderNode(child, [...path, i], depth + 1)).join("") || '<p class="rule-placeholder">Add a course condition or nest another group here.</p>'}</div><div class="rule-group-footer">${node.op !== "not" || !node.children.length ? `<button type="button" data-rule-action="add-course" data-path="${p}" ${getCourses().length ? "" : "disabled"}>+ Course condition</button><details class="add-group-picker"><summary>+ Connect conditions</summary><div class="add-group-options"><button type="button" data-rule-action="add-group" data-group-op="and" data-path="${p}">All of these · AND</button><button type="button" data-rule-action="add-group" data-group-op="or" data-path="${p}">At least one · OR</button><button type="button" data-rule-action="add-group" data-group-op="not" data-path="${p}">Exclude a combination · NOT</button></div></details>` : "<span>Tip: excluding A AND B still allows A alone or B alone.</span>"}</div></div>`;
  }
  function render() {
    const signature = JSON.stringify(getRules());
    if (lastSignature !== null && signature !== lastSignature) {
      past.length = 0;
      future.length = 0;
    }
    lastSignature = signature;
    element.innerHTML = `<div class="rule-tools"><div><button type="button" data-rule-action="undo" ${past.length ? "" : "disabled"}>↶ Undo</button><button type="button" data-rule-action="redo" ${future.length ? "" : "disabled"}>↷ Redo</button></div><details class="wrap-picker"><summary>Group the whole expression</summary><div class="add-group-options"><button type="button" data-rule-action="wrap-and">Combine with AND</button><button type="button" data-rule-action="wrap-or">Combine with OR</button><button type="button" data-rule-action="wrap-not">Negate everything</button></div></details></div>${renderNode(getRules())}`;
  }
  element.addEventListener("change", (event) => {
    const field = event.target.dataset.ruleField;
    if (!field) return;
    if (field === "move") {
      if (!event.target.value) return;
      try {
        commit(
          moveRule(
            getRules(),
            pathOf(event.target.dataset.path),
            pathOf(event.target.value.slice(1)),
          ),
        );
      } catch (error) {
        element.dispatchEvent(
          new CustomEvent("rule-error", { detail: error.message }),
        );
      }
      return;
    }
    const root = structuredClone(getRules()),
      node = at(root, pathOf(event.target.dataset.path));
    if (field === "course") node.course_key = event.target.value;
    if (field === "present") node.present = event.target.value === "true";
    if (field === "operator") {
      const changed = changeOperator(node, event.target.value);
      node.op = changed.op;
      node.children = changed.children;
    }
    commit(root, event.target.dataset.path);
  });
  element.addEventListener("click", (event) => {
    const button = event.target.closest("[data-rule-action]");
    if (!button) return;
    const actionName = button.dataset.ruleAction;
    if (actionName === "undo" || actionName === "redo") {
      const from = actionName === "undo" ? past : future,
        to = actionName === "undo" ? future : past;
      if (!from.length) return;
      to.push(structuredClone(getRules()));
      commit(from.pop(), null, false);
      return;
    }
    if (actionName.startsWith("wrap-")) {
      commit({
        op: actionName.slice(5),
        children: [structuredClone(getRules())],
      });
      return;
    }
    const path = pathOf(button.dataset.path),
      root = structuredClone(getRules()),
      node = at(root, path),
      action = button.dataset.ruleAction;
    if (action === "add-course") {
      const course = getCourses()[0];
      if (!course) return;
      node.children.push({
        op: "course",
        course_key: "",
        present: true,
      });
    }
    if (action === "add-group") {
      const op = button.dataset.groupOp || "or";
      node.children.push(
        op === "not"
          ? { op: "not", children: [emptyRules()] }
          : { op, children: [] },
      );
    }
    if (["remove", "up", "down"].includes(action) && path.length) {
      const parent = at(root, path.slice(0, -1)),
        index = path.at(-1);
      if (action === "remove") parent.children.splice(index, 1);
      else {
        const target = index + (action === "up" ? -1 : 1);
        if (target < 0 || target >= parent.children.length) return;
        [parent.children[index], parent.children[target]] = [
          parent.children[target],
          parent.children[index],
        ];
      }
    }
    commit(
      root,
      action === "remove" ? pathString(path.slice(0, -1)) : button.dataset.path,
    );
  });
  element.addEventListener("dragstart", (event) => {
    // Ignore native drags originating in selects or inputs.
    if (event.target.closest("select,button")) {
      event.preventDefault();
      return;
    }
    const block = event.target.closest("[draggable=true]");
    if (!block) return;
    dragged = block.dataset.path;
    event.dataTransfer.setData("text/plain", dragged);
    event.dataTransfer.effectAllowed = "move";
    event.stopPropagation();
  });
  element.addEventListener("dragover", (event) => {
    if (dragged === null) return;
    const group = event.target.closest("[data-drop-group]");
    if (group) {
      element
        .querySelectorAll(".drop-ready")
        .forEach((node) => node.classList.remove("drop-ready"));
      group.classList.add("drop-ready");
      event.preventDefault();
      event.dataTransfer.dropEffect = "move";
    }
  });
  element.addEventListener("drop", (event) => {
    if (dragged === null) return;
    event.preventDefault();
    event.stopPropagation();
    const group = event.target.closest("[data-drop-group]");
    if (!group) return;
    const source = pathOf(dragged),
      dest = pathOf(group.dataset.dropGroup);
    if (dest.length >= source.length && source.every((v, i) => dest[i] === v)) {
      dragged = null;
      return;
    }
    try {
      commit(moveRule(getRules(), source, dest));
    } catch (error) {
      element.dispatchEvent(
        new CustomEvent("rule-error", { detail: error.message }),
      );
    }
    dragged = null;
    element
      .querySelectorAll(".drop-ready")
      .forEach((group) => group.classList.remove("drop-ready"));
  });
  element.addEventListener("dragend", () => {
    element
      .querySelectorAll(".drop-ready")
      .forEach((node) => node.classList.remove("drop-ready"));
    dragged = null;
  });
  return { render, replace: (next) => commit(next) };
}
