import { readCreditRange } from "./draft-state.js";
import { api, signedIn } from "./account.js";
import {
  emptyRules,
  fromRequired,
  validateRules,
  logicText,
  mountRuleBuilder,
  matchesRules,
} from "./rule-builder.js";
const $ = (id) => document.getElementById(id);
const state = {
  catalog: null,
  selected: [],
  shortlist: [],
  rules: emptyRules(),
  visible: 30,
  results: [],
  searchRequest: null,
  searchCursor: null,
  library: null,
  creditRange: { min: 12, max: 18 },
};
const palette = [
  ["#e7eedb", "#8aa563", "#425632"],
  ["#e3edf2", "#80a4b5", "#375568"],
  ["#f4e8db", "#c49e6f", "#745c3d"],
  ["#eee5f3", "#aa8ab9", "#685179"],
  ["#f4e4e3", "#c68b86", "#85534e"],
  ["#e0eeea", "#70a69c", "#3c655d"],
];
const dayNames = {
  M: "Monday",
  T: "Tuesday",
  W: "Wednesday",
  R: "Thursday",
  F: "Friday",
  S: "Saturday",
  U: "Sunday",
};
const esc = (value) =>
  String(value).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const code = (s) => `${s.department} ${s.number}`;
const lookup = () => new Map(state.catalog.sections.map((s) => [s.id, s]));
const resolve = (ids) => ids.map((id) => lookup().get(id)).filter(Boolean);
const minutes = (time) =>
  Number(time.split(":")[0]) * 60 + Number(time.split(":")[1]);
const clock = (time) => {
  const [h, m] = time.split(":").map(Number);
  return `${h % 12 || 12}:${String(m).padStart(2, "0")}${h < 12 ? "am" : "pm"}`;
};
const meetingLabel = (m) =>
  `${m.days.map((d) => ({ M: "Mon", T: "Tue", W: "Wed", R: "Thu", F: "Fri", S: "Sat", U: "Sun" })[d]).join(" / ")} · ${clock(m.start)}–${clock(m.end)} · ${m.room}`;
const clashes = (a, b) =>
  a.meetings.some((x) =>
    b.meetings.some(
      (y) =>
        x.days.some((d) => y.days.includes(d)) &&
        x.start < y.end &&
        y.start < x.end,
    ),
  );
const draftKey = () => `fcs:planner:v1:${state.catalog.term}`;
function notify(message, error = false) {
  $("notice").hidden = false;
  $("notice").className = `notice${error ? " error" : ""}`;
  $("notice").textContent = message;
}
function save() {
  try {
    localStorage.setItem(draftKey(), JSON.stringify(currentDraft()));
    $("save-status").textContent = "Saved on this device";
  } catch {
    $("save-status").textContent =
      "Device storage unavailable — export your draft";
  }
}
function restore() {
  try {
    const raw = localStorage.getItem(draftKey());
    if (!raw) return;
    const data = validateDraft(JSON.parse(raw));
    state.selected = data.selected;
    state.shortlist = data.shortlist;
    state.rules = data.rules;
    state.creditRange = { ...data.credit_range };
    $("min-credits").value = data.credit_range.min;
    $("max-credits").value = data.credit_range.max;
    if (data.missing)
      notify(
        `${data.missing} saved section(s) are no longer available and were removed.`,
      );
  } catch {
    notify(
      "Your saved draft could not be restored. You can start a new one.",
      true,
    );
  }
}
function validateDraft(data) {
  if (
    !data ||
    ![1, 2].includes(data.version) ||
    data.term !== state.catalog.term ||
    !Array.isArray(data.section_ids) ||
    data.section_ids.length > 60 ||
    !Array.isArray(data.shortlist_ids) ||
    data.shortlist_ids.length > 60 ||
    (data.version === 1 &&
      (!Array.isArray(data.required_course_keys) ||
        data.required_course_keys.length > 60)) ||
    [
      ...data.section_ids,
      ...data.shortlist_ids,
      ...(data.version === 1 ? data.required_course_keys || [] : []),
    ].some((x) => typeof x !== "string")
  )
    throw new Error(
      "Use an FCS JSON export from the current term. Imports allow up to 60 sections.",
    );
  const credit_range = data.credit_range || { min: 12, max: 18 };
  if (
    !credit_range ||
    typeof credit_range.min !== "number" ||
    typeof credit_range.max !== "number" ||
    !Number.isFinite(credit_range.min) ||
    !Number.isFinite(credit_range.max) ||
    credit_range.min < 0 ||
    credit_range.max > 30 ||
    credit_range.min > credit_range.max
  )
    throw new Error("Invalid saved credit range.");
  const map = lookup();
  const selected = [...new Set(data.section_ids)].filter((id) => map.has(id));
  const shortlist = [...new Set(data.shortlist_ids)].filter((id) =>
    map.has(id),
  );
  if (shortlist.length > 60)
    throw new Error("This import exceeds the 60-section shortlist limit.");
  const keys = new Set(resolve(shortlist).map((s) => s.course_key));
  return {
    selected,
    shortlist,
    credit_range,
    rules:
      data.version === 1
        ? fromRequired(
            [...new Set(data.required_course_keys)].filter((k) => keys.has(k)),
          )
        : validateRules(
            data.rules,
            new Set(state.catalog.sections.map((s) => s.course_key)),
            true,
          ),
    missing: new Set(
      [...data.section_ids, ...data.shortlist_ids].filter((id) => !map.has(id)),
    ).size,
  };
}
let searchEpoch = 0;
let searchBusy = false;
function invalidateResults() {
  searchEpoch++;
  state.searchRequest = null;
  state.searchCursor = null;
  state.results = [];
  $("generated-results").replaceChildren();
}
function renderCatalog() {
  if (!state.catalog) return;
  const query = $("search").value.trim().toLowerCase();
  const department = $("department").value;
  const sections = state.catalog.sections.filter(
    (s) =>
      (!department || s.department === department) &&
      (!$("open-only").checked || s.available_seats > 0) &&
      (!query ||
        `${code(s)} ${s.section} ${s.name} ${s.instructor}`
          .toLowerCase()
          .includes(query)),
  );
  $("catalog-count").textContent = `${sections.length} sections`;
  $("course-list").innerHTML =
    sections
      .slice(0, state.visible)
      .map(
        (s) =>
          `<article class="course-card"><div class="course-meta"><span class="course-code">${esc(code(s))} <span class="muted">/ ${esc(s.section)}</span></span><span class="seat-badge ${s.available_seats <= 0 ? "closed" : ""}">${s.available_seats > 0 ? `${s.available_seats} seats open` : "Full"} · ${s.credits} cr</span></div><h3>${esc(s.name)}</h3><div class="course-details">${esc(s.instructor)}<br>${s.meetings.length ? s.meetings.map((m) => esc(meetingLabel(m))).join("<br>") : "Meeting time to be announced"}</div><div class="course-actions"><a class="text-button" href="/campus?kind=course&subject=${encodeURIComponent(s.course_key)}">Details ↗</a><button data-watch="${esc(s.id)}" class="text-button">Watch seats</button><button class="add-button ${state.selected.includes(s.id) ? "selected" : ""}" data-action="select" data-id="${esc(s.id)}">${state.selected.includes(s.id) ? "✓ In your week" : "+ Add to week"}</button><button class="shortlist-button ${state.shortlist.includes(s.id) ? "selected" : ""}" data-action="shortlist" data-id="${esc(s.id)}">${state.shortlist.includes(s.id) ? "✓ Shortlisted" : "+ Shortlist"}</button></div></article>`,
      )
      .join("") ||
    '<div class="empty-state">No sections match these filters.<br>Try another search or turn off “Open seats only.”</div>';
  $("load-more").hidden = state.visible >= sections.length;
  $("results-label").textContent =
    `Showing ${Math.min(state.visible, sections.length)} of ${sections.length}`;
}
function renderSchedule() {
  const sections = resolve(state.selected);
  const conflicting = new Set(
    sections
      .filter((section) =>
        section.meetings.some((a, i) =>
          section.meetings
            .slice(i + 1)
            .some(
              (b) =>
                a.days.some((day) => b.days.includes(day)) &&
                a.start < b.end &&
                b.start < a.end,
            ),
        ),
      )
      .map((section) => section.id),
  );
  let duplicates = false;
  sections.forEach((a, i) =>
    sections.slice(i + 1).forEach((b) => {
      if (clashes(a, b)) {
        conflicting.add(a.id);
        conflicting.add(b.id);
      }
      if (a.course_key === b.course_key) duplicates = true;
    }),
  );
  $("credit-count").textContent = sections.reduce((n, s) => n + s.credits, 0);
  $("course-count").textContent = new Set(
    sections.map((s) => s.course_key),
  ).size;
  const status = $("conflict-status");
  status.classList.toggle("has-conflict", conflicting.size > 0 || duplicates);
  status.textContent = duplicates
    ? "Multiple sections of one course"
    : conflicting.size
      ? `${conflicting.size} sections clash`
      : sections.some((s) => !s.meetings.length)
        ? "Check unannounced times"
        : sections.length
          ? "✓ No time clashes"
          : "Ready when you are";
  $("schedule-empty").hidden = sections.length > 0;
  const meetings = sections.flatMap((s) => s.meetings.map((m) => ({ s, m })));
  const days = [
    "M",
    "T",
    "W",
    "R",
    "F",
    ...["S", "U"].filter((d) => meetings.some(({ m }) => m.days.includes(d))),
  ];
  const start = Math.min(
    8 * 60,
    ...meetings.map(({ m }) => Math.floor(minutes(m.start) / 60) * 60),
  );
  const end = Math.max(
    18 * 60,
    ...meetings.map(({ m }) => Math.ceil(minutes(m.end) / 60) * 60),
  );
  const height = (end - start) * 0.8;
  let html = `<div class="calendar-grid" style="--day-count:${days.length}"><div class="day-header"></div>${days.map((d) => `<div class="day-header">${dayNames[d].slice(0, 3).toUpperCase()}</div>`).join("")}<div class="time-column" style="height:${height}px">`;
  for (let t = start; t < end; t += 60)
    html += `<span class="time-label" style="top:${(t - start) * 0.8}px">${(t / 60) % 12 || 12}${t < 720 ? "am" : "pm"}</span>`;
  html += "</div>";
  days.forEach((d) => {
    html += `<div class="day-column" style="height:${height}px">`;
    const entries = meetings
      .filter(({ m }) => m.days.includes(d))
      .sort((a, b) => a.m.start.localeCompare(b.m.start));
    // Partition overlapping intervals into clusters, then allocate columns within each cluster.
    const clusters = [];
    let cluster = [];
    let clusterEnd = -1;
    entries.forEach((entry) => {
      const begins = minutes(entry.m.start);
      if (begins >= clusterEnd && cluster.length) {
        clusters.push(cluster);
        cluster = [];
        clusterEnd = -1;
      }
      cluster.push(entry);
      clusterEnd = Math.max(clusterEnd, minutes(entry.m.end));
    });
    if (cluster.length) clusters.push(cluster);
    clusters.forEach((group) => {
      const columnEnds = [];
      const placed = group.map((entry) => {
        let column = columnEnds.findIndex((t) => t <= minutes(entry.m.start));
        if (column === -1) column = columnEnds.length;
        columnEnds[column] = minutes(entry.m.end);
        return { ...entry, column };
      });
      placed.forEach(({ s, m, column }) => {
        const color = palette[sections.indexOf(s) % palette.length];
        const width = 100 / columnEnds.length;
        html += `<button class="calendar-event ${conflicting.has(s.id) ? "conflicting" : ""}" data-action="remove" data-id="${esc(s.id)}" style="top:${(minutes(m.start) - start) * 0.8}px;height:${Math.max(22, (minutes(m.end) - minutes(m.start)) * 0.8 - 3)}px;left:calc(${column * width}% + 3px);width:calc(${width}% - 6px);--event-bg:${color[0]};--event-border:${color[1]};--event-ink:${color[2]}" title="${esc(`${code(s)} ${s.section} · ${s.name} · ${meetingLabel(m)}. Click to remove.`)}" aria-label="${esc(`Remove ${code(s)} section ${s.section} from your week`)}"><strong>${esc(code(s))} / ${esc(s.section)}</strong><span>${esc(s.name)}</span><span>${clock(m.start)}–${clock(m.end)}</span><span>${esc(m.room)}</span></button>`;
      });
    });
    html += "</div>";
  });
  html += "</div>";
  $("calendar").innerHTML = html;
  $("schedule-list").innerHTML =
    sections
      .map(
        (s) =>
          `<div class="schedule-row"><div><h3>${esc(code(s))} / ${esc(s.section)} · ${esc(s.name)}</h3><p>${esc(s.instructor)} · ${s.credits} credits${conflicting.has(s.id) ? " · Time clash" : ""}</p>${s.meetings.map((m) => `<p>${esc(meetingLabel(m))}</p>`).join("") || "<p>Meeting time to be announced — confirm before registering.</p>"}</div><button class="text-button" data-action="remove" data-id="${esc(s.id)}" aria-label="${esc(`Remove ${code(s)} section ${s.section}`)}">Remove</button></div>`,
      )
      .join("") ||
    '<div class="empty-state">Your schedule is empty. Add a section to get started.</div>';
}
function renderShortlist() {
  const grouped = new Map();
  resolve(state.shortlist).forEach((s) => {
    if (!grouped.has(s.course_key)) grouped.set(s.course_key, []);
    grouped.get(s.course_key).push(s);
  });
  $("shortlist-count").textContent = state.shortlist.length;
  $("shortlist").innerHTML =
    [...grouped]
      .map(
        ([key, sections]) =>
          `<div class="shortlist-chip"><span> ${esc(code(sections[0]))} <span class="muted">${sections.map((s) => esc(s.section)).join(", ")}</span></span><button data-action="unshortlist" data-key="${esc(key)}" aria-label="${esc(`Remove ${code(sections[0])} from shortlist`)}">×</button></div>`,
      )
      .join("") ||
    '<span class="muted">Use “Shortlist” on a course to keep your options open.</span>';
}
let ruleBuilder;
function ruleCourses() {
  return [
    ...new Map(
      resolve(state.shortlist).map((s) => [
        s.course_key,
        { key: s.course_key, label: `${code(s)} · ${s.name}` },
      ]),
    ).values(),
  ];
}
function renderRules() {
  ruleBuilder?.render();
  $("rule-summary").textContent = logicText(state.rules);
  try {
    validateRules(state.rules, new Set(ruleCourses().map((c) => c.key)));
    $("rule-validation").textContent = "";
    const matched = matchesRules(
      state.rules,
      new Set(resolve(state.selected).map((s) => s.course_key)),
    );
    $("rule-preview").className =
      `rule-preview ${matched ? "matches" : "differs"}`;
    $("rule-preview").textContent = matched
      ? "✓ Your current week matches these rules"
      : "Your current week does not match these rules yet";
  } catch (error) {
    $("rule-validation").textContent = error.message;
    $("rule-preview").className = "rule-preview";
    $("rule-preview").textContent =
      "Finish your rules to preview your current week";
  }
}
function renderAll() {
  renderCatalog();
  renderSchedule();
  renderShortlist();
  renderRules();
}
function handleAction(event) {
  const button = event.target.closest("[data-action]");
  if (!button) return;
  const { action, id, key } = button.dataset;
  if (action === "select") {
    if (state.selected.includes(id))
      state.selected = state.selected.filter((x) => x !== id);
    else {
      if (!state.shortlist.includes(id) && state.shortlist.length >= 60) {
        notify(
          "Your shortlist can hold 60 sections. Remove an option before adding more.",
          true,
        );
        return;
      }
      const section = lookup().get(id);
      const existing = resolve(state.selected).filter(
        (s) => s.course_key !== section.course_key,
      );
      const conflicts = existing.filter((s) => clashes(section, s));
      state.selected = [...existing.map((s) => s.id), id];
      if (!state.shortlist.includes(id)) state.shortlist.push(id);
      notify(
        conflicts.length
          ? `${code(section)} overlaps ${conflicts.map(code).join(", ")}. Both remain visible so you can compare.`
          : `${code(section)} section ${section.section} added to your week.`,
        Boolean(conflicts.length),
      );
    }
  } else if (action === "remove")
    state.selected = state.selected.filter((x) => x !== id);
  else if (action === "shortlist") {
    if (state.shortlist.includes(id)) {
      state.shortlist = state.shortlist.filter((x) => x !== id);
    } else {
      if (state.shortlist.length >= 60) {
        notify("Your shortlist can hold 60 sections.", true);
        return;
      }
      state.shortlist.push(id);
    }
  } else if (action === "unshortlist")
    state.shortlist = state.shortlist.filter(
      (id) => lookup().get(id).course_key !== key,
    );

  invalidateResults();
  renderAll();
  save();
}
function searchSnapshot() {
  return JSON.stringify([
    state.shortlist,
    state.rules,
    Number($("min-credits").value),
    Number($("max-credits").value),
  ]);
}
function renderSearchResults() {
  const count = state.results.length,
    more = Boolean(state.searchCursor);
  const unknown = resolve(state.shortlist).some((s) => !s.meetings.length);
  const summary = count
    ? `${count} possibilities found. ${more ? "There are still combinations to explore." : "Search complete — these are all matching combinations."}`
    : more
      ? "No matching schedule in this batch yet. Continue searching the remaining combinations."
      : "Search complete. No combinations fit. Add sections, adjust your credit range, or revise your rules.";
  $("generated-results").innerHTML =
    `<p class="result-note" role="status">${summary}${unknown ? " Some meeting times are unannounced. Confirm them before registering." : ""}</p>` +
    state.results
      .map((ids, i) => {
        const sections = resolve(ids);
        return `<article class="result-card"><strong>Option ${i + 1} · ${sections.reduce((n, s) => n + s.credits, 0)} credits</strong><p>${sections.map((s) => `${esc(code(s))} / ${esc(s.section)}`).join(" · ")}</p><button class="text-button" data-result="${i}">Use this schedule ↗</button></article>`;
      })
      .join("") +
    (more
      ? `<div class="result-search-actions"><button class="primary-button" data-continue-search>${count ? "Find more schedules" : "Continue search"} ↓</button><p class="muted small">Continues where this search paused. Your current options stay available.</p></div>`
      : "");
}
async function generate(more = false) {
  if (searchBusy) return;
  const button = $("generate-button"),
    continuationButton = $("generated-results").querySelector(
      "[data-continue-search]",
    );
  const min = Number($("min-credits").value),
    max = Number($("max-credits").value);
  if (
    !$("min-credits").value ||
    !$("max-credits").value ||
    min < 0 ||
    max > 30 ||
    min > max
  ) {
    notify(
      "Choose a credit range between 0 and 30, with minimum at or below maximum.",
      true,
    );
    return;
  }
  if (!state.shortlist.length) {
    notify("Shortlist some sections before finding schedules.", true);
    return;
  }
  try {
    validateRules(
      state.rules,
      new Set(resolve(state.shortlist).map((s) => s.course_key)),
    );
  } catch (error) {
    notify(error.message, true);
    return;
  }
  if (more && (!state.searchCursor || !state.searchRequest)) return;
  if (!more) {
    invalidateResults();
    state.searchRequest = JSON.parse(
      JSON.stringify({
        term: state.catalog.term,
        catalog_revision: state.catalog.revision,
        section_ids: state.shortlist,
        rules: state.rules,
        min_credits: min,
        max_credits: max,
      }),
    );
  }
  const snapshot = searchSnapshot(),
    token = searchEpoch;
  searchBusy = true;
  button.disabled = true;
  button.textContent = "Finding schedules…";
  if (continuationButton) {
    continuationButton.disabled = true;
    continuationButton.textContent = "Searching…";
  }
  try {
    const response = await fetch("/api/v1/schedules/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...state.searchRequest,
        ...(more ? { continuation: state.searchCursor } : {}),
      }),
    });
    const data = await response.json();
    if (!response.ok)
      throw new Error(data.error || "Could not generate schedules");
    if (token !== searchEpoch || snapshot !== searchSnapshot()) {
      notify(
        "Your search inputs changed. Find schedules again to use your latest choices.",
      );
      return;
    }
    state.results.push(...data.schedules);
    state.searchCursor = data.continuation;
    renderSearchResults();
  } catch (error) {
    notify(error.message, true);
  } finally {
    searchBusy = false;
    button.disabled = false;
    button.innerHTML = "Find schedules <span>↗</span>";
    if (continuationButton) {
      continuationButton.disabled = false;
      continuationButton.textContent = "Continue search ↓";
    }
  }
}
function download(name, content, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function currentDraft() {
  const range = readCreditRange($("min-credits").value, $("max-credits").value);
  if (range) state.creditRange = range;
  return {
    version: 2,
    term: state.catalog.term,
    section_ids: state.selected,
    shortlist_ids: state.shortlist,
    rules: state.rules,
    credit_range: { ...state.creditRange },
  };
}
function bind() {
  $("course-list").addEventListener("click", async (event) => {
    const button = event.target.closest("[data-watch]");
    if (!button || !(await signedIn())) return;
    button.disabled = true;
    try {
      await api("/watches", {
        method: "POST",
        data: { term: state.catalog.term, section_id: button.dataset.watch },
      });
      notify(
        "Seat watch saved. Open Campus → Seat watches to manage it. Alerts appear in the app when an observed snapshot changes from full to open.",
      );
    } catch (error) {
      notify(error.message, true);
    } finally {
      button.disabled = false;
    }
  });
  async function saveNamed(copy = false) {
    if (!(await signedIn())) return;
    let dialog = $("save-draft-dialog");
    if (!dialog) {
      dialog = document.createElement("dialog");
      dialog.id = "save-draft-dialog";
      dialog.className = "library-dialog";
      dialog.innerHTML =
        '<button class="dialog-close" data-close-save aria-label="Close save dialog">×</button><h2>Keep this possibility.</h2><p class="muted small">Your draft, shortlist, rules, and credit range stay private in your account. Share a selected schedule separately from Campus.</p><form class="platform-form"><label>Schedule name<input name="name" maxlength="80" required></label><p class="form-error" role="status"></p><button class="primary-button">Save draft ↗</button></form>';
      document.body.append(dialog);
      dialog
        .querySelector("[data-close-save]")
        .addEventListener("click", () => dialog.close());
      dialog.querySelector("form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.target,
          button = form.querySelector("button"),
          name = form.elements.name.value.trim();
        button.disabled = true;
        try {
          if (!readCreditRange($("min-credits").value, $("max-credits").value))
            throw new Error(
              "Choose a valid credit range before saving this named draft.",
            );
          const updating = state.library && dialog.dataset.copy !== "true";
          const saved = await api(
            updating ? `/library/${state.library.id}` : "/library",
            {
              method: updating ? "PUT" : "POST",
              data: {
                name,
                draft: currentDraft(),
                ...(updating ? { version: state.library.version } : {}),
              },
            },
          );
          state.library = { id: saved.id, version: saved.version, name };
          $("save-library").textContent = "Save changes";
          $("save-copy").hidden = false;
          dialog.close();
          notify(
            "Named draft saved to your account. Open Campus → My schedules to view or share it.",
          );
        } catch (error) {
          form.querySelector(".form-error").textContent = error.message;
        } finally {
          button.disabled = false;
        }
      });
    }
    dialog.dataset.copy = String(copy);
    dialog.querySelector("input").value = state.library?.name || "My semester";
    dialog.querySelector(".form-error").textContent = "";
    dialog.showModal();
  }
  $("save-library").addEventListener("click", () => saveNamed());
  $("save-copy").addEventListener("click", () => saveNamed(true));
  $("calendar-export").addEventListener("click", () => {
    let dialog = $("calendar-dialog");
    if (!dialog) {
      dialog = document.createElement("dialog");
      dialog.id = "calendar-dialog";
      dialog.innerHTML =
        '<button class="dialog-close" data-close-calendar aria-label="Close">×</button><h2>Take your week with you.</h2><p class="muted small">Choose your semester dates. Events repeat weekly in Asia/Karachi time. Confirm dates with your university.</p><form class="calendar-dates"><label>First day<input name="start" type="date" required></label><label>Last day<input name="end" type="date" required></label><p class="form-error" role="status"></p><button class="primary-button">Download calendar ↗</button></form>';
      document.body.append(dialog);
      dialog
        .querySelector("[data-close-calendar]")
        .addEventListener("click", () => dialog.close());
      dialog.querySelector("form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.target;
        try {
          const dates = Object.fromEntries(new FormData(form));
          const response = await api("/calendar-export", {
            method: "POST",
            data: { draft: currentDraft(), ...dates },
            raw: true,
          });
          download(
            `fcs-${state.catalog.term}.ics`,
            await response.text(),
            "text/calendar",
          );
          dialog.close();
          notify(
            "Calendar exported. Classes with unannounced meeting times are omitted.",
          );
        } catch (error) {
          form.querySelector(".form-error").textContent = error.message;
        }
      });
    }
    dialog.showModal();
  });
  const savedId = new URLSearchParams(location.search).get("saved");
  if (savedId)
    api(`/library/${encodeURIComponent(savedId)}`)
      .then((saved) => {
        const draft = validateDraft(saved.draft);
        state.selected = draft.selected;
        state.shortlist = draft.shortlist;
        state.rules = draft.rules;
        state.creditRange = { ...draft.credit_range };
        state.library = {
          id: saved.id,
          version: saved.version,
          name: saved.name,
        };
        $("save-library").textContent = "Save changes";
        $("save-copy").hidden = false;
        $("min-credits").value = draft.credit_range.min;
        $("max-credits").value = draft.credit_range.max;
        renderAll();
        save();
        notify(
          `Opened “${saved.name}”. Use Save changes to update this draft, or Save a copy for another option.`,
        );
      })
      .catch((error) => notify(error.message, true));

  ruleBuilder = mountRuleBuilder({
    element: $("rule-builder"),
    getRules: () => state.rules,
    setRules: (rules) => {
      state.rules = rules;
    },
    getCourses: ruleCourses,
    getPreviewKeys: () =>
      new Set(resolve(state.selected).map((s) => s.course_key)),
    onChange: () => {
      invalidateResults();
      renderRules();
      save();
    },
  });
  $("rule-builder").addEventListener("rule-error", (event) =>
    notify(event.detail, true),
  );
  $("reset-rules").addEventListener("click", () =>
    ruleBuilder.replace(emptyRules()),
  );
  ["search", "department", "open-only"].forEach((id) =>
    $(id).addEventListener(id === "search" ? "input" : "change", () => {
      state.visible = 30;
      renderCatalog();
    }),
  );
  $("load-more").addEventListener("click", () => {
    state.visible += 30;
    renderCatalog();
  });
  ["course-list", "calendar", "schedule-list", "shortlist"].forEach((id) =>
    $(id).addEventListener("click", handleAction),
  );
  $("clear-shortlist").addEventListener("click", () => {
    state.shortlist = [];

    invalidateResults();
    renderShortlist();
    renderCatalog();
    renderRules();
    save();
  });
  ["min-credits", "max-credits"].forEach((id) =>
    $(id).addEventListener("input", () => {
      invalidateResults();
      save();
    }),
  );
  $("generate-button").addEventListener("click", () => generate());
  $("generated-results").addEventListener("click", (event) => {
    if (event.target.closest("[data-continue-search]")) {
      generate(true);
      return;
    }
    const button = event.target.closest("[data-result]");
    if (!button) return;
    state.selected = [...state.results[Number(button.dataset.result)]];
    renderAll();
    save();
    notify(
      "This option is now in your week. Your shortlist is still available.",
    );
  });
  const changeView = (list) => {
    $("calendar").hidden = list;
    $("schedule-list").hidden = !list;
    $("week-view").setAttribute("aria-pressed", String(!list));
    $("list-view").setAttribute("aria-pressed", String(list));
  };
  $("week-view").addEventListener("click", () => changeView(false));
  $("list-view").addEventListener("click", () => changeView(true));
  $("export-button").addEventListener("click", () =>
    download(
      `fcs-${state.catalog.term}-schedule.json`,
      JSON.stringify(currentDraft(), null, 2),
      "application/json",
    ),
  );
  $("import-button").addEventListener("click", () => $("import-file").click());
  $("import-file").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    try {
      if (file.size > 256000)
        throw new Error("Schedule files must be smaller than 256 KB.");
      const draft = validateDraft(JSON.parse(await file.text()));
      state.selected = draft.selected;
      state.shortlist = draft.shortlist;
      state.rules = draft.rules;
      state.creditRange = { ...draft.credit_range };
      $("min-credits").value = draft.credit_range.min;
      $("max-credits").value = draft.credit_range.max;
      state.library = null;
      $("save-library").textContent = "Save named draft";
      $("save-copy").hidden = true;
      invalidateResults();
      renderAll();
      save();
      notify(
        `Schedule imported.${draft.missing ? ` ${draft.missing} unavailable section(s) were skipped.` : ""}`,
      );
    } catch (error) {
      notify(error.message, true);
    } finally {
      event.target.value = "";
    }
  });
  $("print-button").addEventListener("click", () => window.print());
}
async function init() {
  try {
    const response = await fetch("/api/v1/catalog");
    const catalog = await response.json();
    if (!response.ok) throw new Error(catalog.error || "Catalog unavailable");
    state.catalog = catalog;
    $("term-label").textContent = catalog.term_name;
    $("data-status").textContent =
      "Local catalog snapshot · capture time unavailable";
    $("data-status").title =
      `Local file modified ${new Date(catalog.file_modified_at).toLocaleString("en-PK", { timeZone: "Asia/Karachi" })} PKT. This is not the scrape timestamp.`;
    $("department").innerHTML =
      '<option value="">All departments</option>' +
      catalog.departments
        .map((d) => `<option value="${esc(d)}">${esc(d)}</option>`)
        .join("");
    restore();
    const requestedCourse = new URLSearchParams(location.search).get("course");
    if (requestedCourse) $("search").value = requestedCourse;
    bind();
    renderAll();
  } catch (error) {
    $("data-status").textContent = "Catalog unavailable";
    $("course-list").innerHTML =
      '<div class="empty-state">Unable to load the catalog. Reload the page to try again.</div>';
    notify(error.message, true);
    ["generate-button", "import-button", "export-button"].forEach(
      (id) => ($(id).disabled = true),
    );
  }
}
init();
