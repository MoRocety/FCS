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
      if (!courseKeys.has(node.course_key))
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
    return `${rule.course_key.replace(":", " ")} ${rule.present ? "is in the schedule" : "is not in the schedule"}`;
  if (!rule.children.length)
    return root && rule.op === "and" ? "No extra rules — any schedule within your credit range." : `empty ${rule.op.toUpperCase()} group`;
  if (rule.op === "not") return `NOT (${rule.children.map(child => ruleText(child, false)).join("")})`;
  return `(${rule.children.map(child => ruleText(child, false)).join(` ${rule.op.toUpperCase()} `)})`;
}
export function mountRuleBuilder({
  element,
  getRules,
  setRules,
  getCourses,
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
  function commit(next, focusPath = null) {
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
    const move = root
      ? ""
      : `<span class="block-handle" aria-hidden="true">⠿</span><button type="button" class="block-icon" data-rule-action="up" data-path="${p}" aria-label="Move block up">↑</button><button type="button" class="block-icon" data-rule-action="down" data-path="${p}" aria-label="Move block down">↓</button><button type="button" class="block-icon" data-rule-action="remove" data-path="${p}" aria-label="Remove block">×</button>`;
    if (node.op === "course") {
      const courses = getCourses();
      const missing = !courses.some((c) => c.key === node.course_key);
      return `<div class="rule-block course-rule" data-path="${p}" ${drag}><span class="block-kind">COURSE</span><select data-rule-field="course" data-path="${p}" aria-label="Course for rule">${missing ? `<option value="${esc(node.course_key)}">${esc(node.course_key.replace(":", " "))} — not shortlisted</option>` : ""}${courses.map((c) => `<option value="${esc(c.key)}" ${node.course_key === c.key ? "selected" : ""}>${esc(c.label)}</option>`).join("")}</select><select data-rule-field="present" data-path="${p}" aria-label="Course condition"><option value="true" ${node.present ? "selected" : ""}>is in schedule</option><option value="false" ${!node.present ? "selected" : ""}>is not in schedule</option></select><span class="block-actions">${move}</span></div>`;
    }
    return `<div class="rule-group rule-${node.op}" data-path="${p}" data-drop-group="${p}" ${drag} style="--rule-depth:${depth}"><div class="rule-group-heading"><select data-rule-field="operator" data-path="${p}" aria-label="Group operator"><option value="and" ${node.op === "and" ? "selected" : ""}>AND · all of these</option><option value="or" ${node.op === "or" ? "selected" : ""}>OR · any of these</option><option value="not" ${node.op === "not" ? "selected" : ""}>NOT · invert this</option></select><span class="block-actions">${root ? '<span class="root-label">SCHEDULE MUST MATCH</span>' : move}</span></div><div class="rule-children">${node.children.map((child, i) => renderNode(child, [...path, i], depth + 1)).join("") || '<p class="rule-placeholder">Add a course condition or nest another group here.</p>'}</div><div class="rule-group-footer">${node.op !== "not" || !node.children.length ? `<button type="button" data-rule-action="add-course" data-path="${p}" ${getCourses().length ? "" : "disabled"}>+ Course condition</button><button type="button" data-rule-action="add-group" data-path="${p}">+ Nested group</button>` : "<span>NOT reverses the expression inside it.</span>"}</div></div>`;
  }
  function render() {
    element.innerHTML = renderNode(getRules());
  }
  element.addEventListener("change", (event) => {
    const field = event.target.dataset.ruleField;
    if (!field) return;
    const root = structuredClone(getRules()),
      node = at(root, pathOf(event.target.dataset.path));
    if (field === "course") node.course_key = event.target.value;
    if (field === "present") node.present = event.target.value === "true";
    if (field === "operator") {
      node.op = event.target.value;
      if (node.op === "not" && node.children.length > 1)
        node.children = [{ op: "and", children: node.children }];
    }
    commit(root, event.target.dataset.path);
  });
  element.addEventListener("click", (event) => {
    const button = event.target.closest("[data-rule-action]");
    if (!button) return;
    const path = pathOf(button.dataset.path),
      root = structuredClone(getRules()),
      node = at(root, path),
      action = button.dataset.ruleAction;
    if (action === "add-course") {
      const course = getCourses()[0];
      if (!course) return;
      node.children.push({
        op: "course",
        course_key: course.key,
        present: true,
      });
    }
    if (action === "add-group") node.children.push(emptyRules());
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
    const root = structuredClone(getRules()),
      parent = at(root, source.slice(0, -1)),
      target = at(root, dest),
      node = at(root, source);
    if (target.op === "not" && target.children.length) {
      dragged = null;
      return;
    }
    parent.children.splice(source.at(-1), 1);
    target.children.push(node);
    dragged = null;
    commit(root);
  });
  element.addEventListener("dragend", () => {
    dragged = null;
  });
  return { render };
}
