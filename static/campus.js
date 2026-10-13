import { api, account, signedIn } from "./account.js";
const $ = (id) => document.getElementById(id);
const esc = (v) =>
  String(v ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const date = (v) =>
  new Date(v).toLocaleString("en-PK", {
    timeZone: "Asia/Karachi",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
const state = {
  subjects: null,
  tab: "explore",
  kind: "course",
  query: "",
  visible: 24,
  detail: null,
  thread: null,
  library: null,
};
let generation = 0;
function notice(message, error = false) {
  $("campus-notice").textContent = message;
  $("campus-notice").className =
    `notice platform-notice${error ? " error" : ""}`;
}
function empty(title, body, action = "") {
  return `<div class="hub-empty"><h3>${title}</h3><p>${body}</p>${action}</div>`;
}
function needsAccount(title) {
  $("campus-content").innerHTML = empty(
    title,
    "Sign in to keep your schedules and seat watches together across visits.",
    '<button class="primary-button" data-login>Sign in ↗</button>',
  );
}
function rating(item) {
  return item.review_count
    ? `${item.rating.toFixed(1)} / 5 · ${item.review_count} review${item.review_count === 1 ? "" : "s"}`
    : "No reviews yet — share your experience";
}
function renderExplore() {
  const items = state.subjects[state.kind].filter((s) =>
    `${s.name} ${s.code} ${s.department} ${(s.courses || []).map((key) => key.replace(":", " ")).join(" ")}`
      .toLowerCase()
      .includes(state.query.toLowerCase()),
  );
  $("campus-content").innerHTML =
    `<div class="campus-controls"><input class="campus-search" id="campus-search" type="search" placeholder="Find a course or teacher…" aria-label="Search campus subjects" value="${esc(state.query)}"><div class="subject-switch"><button data-kind="course" class="${state.kind === "course" ? "active" : ""}">Courses</button><button data-kind="instructor" class="${state.kind === "instructor" ? "active" : ""}">Teachers</button></div></div><div class="campus-grid" id="subject-grid"></div><div class="catalog-footer"><button class="text-button" data-show-more ${state.visible >= items.length ? "hidden" : ""}>Show more ↓</button><span>${Math.min(items.length, state.visible)} of ${items.length}</span></div>`;
  $("subject-grid").innerHTML =
    items
      .slice(0, state.visible)
      .map(
        (s) =>
          `<article class="subject-card"><span class="course-code">${esc(s.code)}</span><h3>${esc(s.name)}</h3><p>${state.kind === "course" ? `${s.sections} section${s.sections === 1 ? "" : "s"} in this catalog` : `Teaches ${s.courses.length} course${s.courses.length === 1 ? "" : "s"} in this catalog`}</p><span class="rating-line ${s.review_count ? "" : "empty"}">${rating(s)}</span><div class="subject-card-actions"><button class="text-button" data-subject="${esc(s.key)}" data-subject-kind="${state.kind}">${state.kind === "course" ? "Reviews & conversations" : "Teacher feedback"} ↗</button>${state.kind === "course" ? `<a class="text-button" href="/?course=${encodeURIComponent(s.code)}">Plan this course ↗</a>` : ""}</div></article>`,
      )
      .join("") ||
    empty(
      "Nothing matches yet.",
      "Try a course code, another spelling, or switch between courses and teachers.",
    );
}
async function loadTab() {
  const token = ++generation;
  state.tab = [
    "explore",
    "schedules",
    "watches",
    "alerts",
    "moderation",
  ].includes(location.hash.slice(1))
    ? location.hash.slice(1)
    : "explore";
  document
    .querySelectorAll("[data-tab]")
    .forEach((button) =>
      button.setAttribute(
        "aria-selected",
        String(button.dataset.tab === state.tab),
      ),
    );
  $("moderation-tab").hidden = account.user?.role !== "moderator";
  if (!state.subjects) return;
  if (state.tab === "explore") {
    renderExplore();
    return;
  }
  if (!account.user) {
    needsAccount(
      {
        schedules: "Make room for a few possibilities.",
        watches: "Keep an eye on the sections you want.",
        alerts: "Your seat updates, in one place.",
        moderation: "Moderation is for authorized accounts.",
      }[state.tab],
    );
    return;
  }
  $("campus-content").innerHTML = '<div class="hub-empty">Loading…</div>';
  try {
    if (state.tab === "schedules") {
      const data = await api("/library");
      if (token !== generation) return;
      $("campus-content").innerHTML =
        `<div class="campus-heading-row"><h2>My saved schedules</h2><a class="primary-button button-link" href="/">Build another week ↗</a></div><div class="campus-grid">${data.schedules.map((s) => `<article class="library-card"><span class="eyebrow">${esc(s.term)} · VERSION ${s.version}</span><h3>${esc(s.name)}</h3><p>Updated ${date(s.updated_at)} PKT</p><div class="subject-card-actions"><a class="text-button" href="/?saved=${s.id}">Open in planner ↗</a><button class="text-button" data-library="${s.id}">Manage & share</button></div></article>`).join("") || empty("Your next semester starts here.", "Build a week in the planner, then use “Save named draft” to keep different options.", '<a href="/" class="primary-button button-link">Open planner ↗</a>')}</div>`;
    } else if (state.tab === "watches") {
      const data = await api("/watches");
      if (token !== generation) return;
      $("campus-content").innerHTML =
        `<div class="campus-heading-row"><h2>Seat watches</h2><a href="/" class="text-button">Find a section ↗</a></div><p class="seat-note">These watches use observed catalog snapshots. A notification appears when a section changes from full to open. They do not reserve seats, and email/push delivery is not connected.</p><div class="campus-grid">${data.watches.map((w) => `<article class="watch-card"><span class="eyebrow">${esc(w.term)}</span><h3>${esc(w.section_id.replaceAll(":", " / "))}</h3><p>${w.section ? `${esc(w.section.name)} · ${w.section.available_seats > 0 ? `${w.section.available_seats} seats available in the current snapshot` : "Full in the current snapshot"}` : "This section is outside the active catalog; its availability is unknown."}</p><div class="subject-card-actions"><button class="text-button action-danger" data-unwatch="${w.id}">Stop watching</button></div></article>`).join("") || empty("The right section is worth watching.", "Use “Watch seats” on a section in the planner. Your watches will appear here.", '<a href="/" class="primary-button button-link">Browse sections ↗</a>')}</div>`;
    } else if (state.tab === "alerts") {
      const data = await api("/notifications");
      if (token !== generation) return;
      updateBadge(data.unread);
      $("campus-content").innerHTML =
        `<div class="campus-heading-row"><h2>Your seat updates</h2><button class="text-button" data-mark-read>Mark all read</button></div><p class="seat-note">Updates reflect observed snapshots. Confirm availability in the registration portal before acting. Watching a section that is already open does not create a backdated alert.</p><div class="campus-grid">${data.notifications.map((n) => `<article class="activity-card ${n.read_at ? "" : "unread"}"><span class="eyebrow">${n.read_at ? "SEAT UPDATE" : "NEW SEAT UPDATE"}</span><h3>${esc(n.section_id.replaceAll(":", " / "))}</h3><p>${esc(n.message)}</p><p>${date(n.created_at)} PKT · ${esc(n.term)}</p><a class="text-button" href="/?course=${encodeURIComponent(n.section_id.split(":").slice(0, 2).join(" "))}">Review section ↗</a></article>`).join("") || empty("Nothing new yet.", "When a watched section changes from full to open in an observed snapshot, its update will appear here.")}</div>`;
    } else {
      const data = await api("/moderation/reports");
      if (token !== generation) return;
      $("campus-content").innerHTML =
        `<div class="campus-heading-row"><h2>Reported content</h2></div><div class="campus-grid">${data.reports.map((r) => `<article class="moderation-card"><span class="eyebrow">${esc(r.target_type)} #${r.target_id}</span><p class="entry-body">${esc(r.target?.body || "Content unavailable")}</p><p class="muted small">Reported by ${esc(r.display_name)}: ${esc(r.reason)}</p><div class="subject-card-actions"><button class="text-button action-danger" data-moderate="${r.id}" data-action="hide">Hide content</button><button class="text-button" data-moderate="${r.id}" data-action="dismiss">Dismiss report</button></div></article>`).join("") || empty("No reports need attention.", "New reports will appear here, along with the content and report reason.")}</div>`;
    }
  } catch (error) {
    if (token === generation) {
      $("campus-content").innerHTML = empty(
        "Could not load this view.",
        esc(error.message),
      );
      notice(error.message, true);
    }
  }
}
function updateBadge(count) {
  $("alert-badge").hidden = !count;
  $("alert-badge").textContent = count;
}
async function refreshAlerts() {
  if (!account.user) {
    updateBadge(0);
    return;
  }
  try {
    const data = await api("/notifications");
    updateBadge(data.unread);
  } catch {}
}
function identityLine(entry) {
  return [
    `${esc(entry.display_name)} · @${esc(entry.username)}`,
    entry.term ? esc(entry.term) : null,
    `${date(entry.created_at)} PKT`,
  ]
    .filter(Boolean)
    .join(" · ");
}
function actions(entry, type) {
  return `<div class="entry-actions">${account.user?.id === entry.owner_id ? `<button class="text-button action-danger" data-delete-content="${entry.id}" data-type="${type}">Remove my ${type}</button>` : ""}<button class="text-button" data-report="${entry.id}" data-type="${type}">Report</button></div>`;
}
async function openSubject(kind, key) {
  state.detail = { kind, key };
  state.thread = null;
  const dialog = $("subject-dialog");
  if (!dialog.open) dialog.showModal();
  $("subject-body").innerHTML =
    '<div class="empty-state">Loading details…</div>';
  try {
    const [feedback, conversation] = await Promise.all([
      api(
        `/reviews?kind=${encodeURIComponent(kind)}&subject=${encodeURIComponent(key)}`,
      ),
      kind === "course"
        ? api(`/threads?course=${encodeURIComponent(key)}`)
        : Promise.resolve({ threads: [] }),
    ]);
    if (state.detail?.key !== key || state.thread) return;
    const item = feedback.subject,
      summary = feedback.summary;
    const mine = feedback.reviews.find(
      (r) => r.owner_id === account.user?.id && r.term === state.subjects.term,
    );
    $("subject-body").innerHTML =
      `<p class="eyebrow">${esc(item.code)} · ${esc(state.subjects.term_name)}</p><h2>${esc(item.name)}</h2><p class="muted">${kind === "course" ? "Course experiences and conversations from students." : "Teacher feedback from students who chose to share their experience."}</p><p class="profile-note">Enrollment and university identity are not verified. Ratings reflect community submissions, not official evaluations.</p><div class="subject-stats"><div><strong>${summary.count ? Number(summary.rating).toFixed(1) : "—"}</strong> <span>/ 5 overall</span></div><div><strong>${summary.count ? Number(summary.difficulty).toFixed(1) : "—"}</strong> <span>/ 5 difficulty</span></div><div><strong>${summary.count}</strong> <span>review${summary.count === 1 ? "" : "s"}</span></div></div>${kind === "instructor" ? `<p class="muted">Courses: ${item.courses.map((course) => `<button class="text-button" data-subject="${esc(course)}" data-subject-kind="course">${esc(course.replace(":", " "))}</button>`).join(" · ")}</p>` : ""}${kind === "course" ? `<p class="muted">Teachers in this catalog: ${(item.instructors || []).map((teacher) => `<button class="text-button" data-subject="${esc(teacher.key)}" data-subject-kind="instructor">${esc(teacher.name)} ↗</button>`).join(" · ") || "Teaching team or TBD; no individual teacher profile is listed."}</p>` : ""}<section class="subject-section"><h3>Student reviews</h3>${feedback.reviews.map((r) => `<article class="review-entry"><div class="entry-meta"><span>${identityLine(r)}</span><span>${r.rating}/5 overall · ${r.difficulty}/5 difficulty</span></div><p class="entry-body">${esc(r.body)}</p>${actions(r, "review")}</article>`).join("") || '<p class="muted">No reviews yet. Your experience can help the next student.</p>'}${account.user ? `<form class="platform-form" id="review-form"><h3>${mine ? "Edit your review for this term" : "Share your experience"}</h3><div class="form-columns"><label>Overall experience<select name="rating" required>${[1, 2, 3, 4, 5].map((n) => `<option value="${n}" ${(mine?.rating || 4) === n ? "selected" : ""}>${n} / 5</option>`).join("")}</select></label><label>Difficulty<select name="difficulty" required>${[1, 2, 3, 4, 5].map((n) => `<option value="${n}" ${(mine?.difficulty || 3) === n ? "selected" : ""}>${n} / 5${n === 1 ? " · lighter" : n === 5 ? " · harder" : ""}</option>`).join("")}</select></label></div><label>Your review<textarea name="body" minlength="20" maxlength="2000" placeholder="What helped you learn? What should another student know?" required>${esc(mine?.body || "")}</textarea></label><p class="profile-note">Focus on your experience. Avoid private information and personal attacks. One review per subject per term; publishing again updates yours.</p><p class="form-error" role="status"></p><button class="primary-button">${mine ? "Update review" : "Publish review"} ↗</button></form>` : '<button class="text-button" data-login>Sign in to write a review ↗</button>'}</section>${kind === "course" ? `<section class="subject-section"><h3>Conversations & study groups</h3>${conversation.threads.map((t) => `<article class="thread-entry"><span class="thread-kind">${t.kind === "study_group" ? "STUDY GROUP" : "DISCUSSION"}</span><h4>${esc(t.title)}</h4><p class="entry-meta">${identityLine(t)}</p><div class="entry-actions"><button class="text-button" data-thread="${t.id}">Open conversation ↗</button><span class="muted small">${t.comments_count} replies${t.kind === "study_group" ? ` · ${t.members_count} members` : ""}</span></div></article>`).join("") || '<p class="muted">Start a question, share a useful resource, or find people to study with.</p>'}${account.user ? `<form class="platform-form" id="thread-form"><h3>Start something useful</h3><label>Post type<select name="kind"><option value="discussion">Course discussion</option><option value="study_group">Study group</option></select></label><label>Title<input name="title" minlength="5" maxlength="120" required placeholder="What would you like to discuss?"></label><label>Details<textarea name="body" minlength="10" maxlength="4000" required placeholder="Add context. For a study group, explain the topic and how you plan to meet."></textarea></label><p class="form-error" role="status"></p><button class="primary-button">Post to this course ↗</button></form>` : '<button class="text-button" data-login>Sign in to start a conversation ↗</button>'}</section>` : ""}`;
  } catch (error) {
    $("subject-body").innerHTML = empty(
      "Details are unavailable.",
      esc(error.message),
    );
  }
}
async function openThread(identity) {
  state.thread = Number(identity);
  $("subject-body").innerHTML =
    '<div class="empty-state">Loading conversation…</div>';
  if (!$("subject-dialog").open) $("subject-dialog").showModal();
  try {
    const data = await api(`/threads/${identity}`);
    if (state.thread !== Number(identity)) return;
    const t = data.thread;
    state.threadCourse = t.course_key;
    $("subject-body").innerHTML =
      `<button class="text-button" data-subject="${esc(t.course_key)}" data-subject-kind="course">← Back to ${esc(t.course_key.replace(":", " "))}</button><p class="eyebrow">${t.kind === "study_group" ? "STUDY GROUP" : "COURSE CONVERSATION"} · ${esc(t.term)}</p><h2>${esc(t.title)}</h2><p class="entry-meta">${identityLine(t)}</p><p class="entry-body">${esc(t.body)}</p>${actions(t, "thread")}${t.kind === "study_group" ? `<section class="subject-section"><h3>${data.members.length} study group member${data.members.length === 1 ? "" : "s"}</h3><p class="profile-note">Joining makes your display name visible to this group. Do not post private contact details publicly.</p><div class="group-members">${data.members.map((m) => `<span>${esc(m.display_name)}</span>`).join("") || "<span>No one has joined yet.</span>"}</div><button class="primary-button" data-membership="${t.id}" data-joined="${data.members.some((m) => m.id === account.user?.id)}">${data.members.some((m) => m.id === account.user?.id) ? "Leave group" : "Join study group"} ↗</button></section>` : ""}<section class="subject-section"><h3>Replies</h3>${data.comments.map((c) => `<article class="comment-entry"><p class="entry-meta">${identityLine(c)}</p><p class="entry-body">${esc(c.body)}</p>${actions(c, "comment")}</article>`).join("") || '<p class="muted">No replies yet.</p>'}${account.user ? '<form class="platform-form" id="comment-form"><label>Add a reply<textarea name="body" minlength="2" maxlength="2000" required></textarea></label><p class="form-error" role="status"></p><button class="primary-button">Post reply ↗</button></form>' : '<button class="text-button" data-login>Sign in to reply ↗</button>'}</section>`;
  } catch (error) {
    $("subject-body").innerHTML = empty(
      "This conversation is unavailable.",
      esc(error.message),
    );
  }
}
async function openLibrary(identity) {
  const data = await api(`/library/${identity}`);
  state.library = data;
  const dialog = $("library-dialog");
  if (!dialog.open) dialog.showModal();
  $("library-body").innerHTML =
    `<p class="eyebrow">PRIVATE SAVED DRAFT · VERSION ${data.version}</p><h2>${esc(data.name)}</h2><p class="muted small">${esc(data.term)} · ${data.sections.length} sections · ${data.sections.reduce((sum, s) => sum + s.credits, 0)} credits</p><a class="primary-button button-link" href="/?saved=${data.id}">Open in planner ↗</a><form class="platform-form" id="rename-form"><label>Schedule name<input name="name" value="${esc(data.name)}" maxlength="80" required></label><p class="form-error" role="status"></p><button class="text-button">Rename saved schedule</button></form><section class="subject-section"><h3>Read-only share links</h3><p class="profile-note">Anyone with a link can view the selected schedule snapshot. Your shortlist, rules, and account identity stay private. Edits to the saved draft do not change existing links.</p><button class="text-button" data-create-share="${data.id}">Create a share link ↗</button>${data.shares.map((sh) => `<div class="share-entry">${sh.revoked_at ? "Revoked" : "Active"} · created ${date(sh.created_at)} PKT${sh.revoked_at ? "" : `<a href="/s/${encodeURIComponent(sh.token)}" target="_blank" rel="noopener">${location.origin}/s/${esc(sh.token)}</a><button class="text-button action-danger" data-revoke-share="${esc(sh.token)}">Revoke link</button>`}</div>`).join("")}</section><section class="subject-section"><button class="text-button action-danger" data-delete-schedule="${data.id}">Delete saved draft and its share links</button></section>`;
}
$("campus-content").addEventListener("input", (event) => {
  if (event.target.id === "campus-search") {
    state.query = event.target.value;
    state.visible = 24;
    const input = event.target;
    const position = input.selectionStart;
    renderExplore();
    $("campus-search").focus();
    $("campus-search").setSelectionRange(position, position);
  }
});
document.addEventListener("click", async (event) => {
  const tab = event.target.closest("[data-tab]");
  if (tab) {
    location.hash = tab.dataset.tab;
    return;
  }
  const kind = event.target.closest("[data-kind]");
  if (kind) {
    state.kind = kind.dataset.kind;
    state.visible = 24;
    renderExplore();
    return;
  }
  if (event.target.closest("[data-show-more]")) {
    state.visible += 24;
    renderExplore();
    return;
  }
  if (event.target.closest("[data-close-subject]")) {
    $("subject-dialog").close();
    state.detail = null;
    state.thread = null;
    if (state.tab === "explore" && state.subjects) renderExplore();
    return;
  }
  if (event.target.closest("[data-close-library]")) {
    $("library-dialog").close();
    return;
  }
  const subject = event.target.closest("[data-subject]");
  if (subject) {
    await openSubject(subject.dataset.subjectKind, subject.dataset.subject);
    return;
  }
  const thread = event.target.closest("[data-thread]");
  if (thread) {
    await openThread(thread.dataset.thread);
    return;
  }
  try {
    const library = event.target.closest("[data-library]");
    if (library) {
      await openLibrary(library.dataset.library);
      return;
    }
    const unwatch = event.target.closest("[data-unwatch]");
    if (unwatch) {
      await api(`/watches/${unwatch.dataset.unwatch}`, { method: "DELETE" });
      await loadTab();
      notice("Seat watch removed.");
      return;
    }
    if (event.target.closest("[data-mark-read]")) {
      await api("/notifications/read", { method: "POST" });
      await loadTab();
      return;
    }
    const membership = event.target.closest("[data-membership]");
    if (membership) {
      if (!(await signedIn())) return;
      await api(`/threads/${membership.dataset.membership}/membership`, {
        method: membership.dataset.joined === "true" ? "DELETE" : "POST",
      });
      await openThread(membership.dataset.membership);
      return;
    }
    const report = event.target.closest("[data-report]");
    if (report) {
      if (!(await signedIn())) return;
      const reason = prompt("Why should a moderator review this content?");
      if (!reason) return;
      await api("/reports", {
        method: "POST",
        data: {
          target_type: report.dataset.type,
          target_id: Number(report.dataset.report),
          reason,
        },
      });
      notice("Report submitted for moderation.");
      return;
    }
    const remove = event.target.closest("[data-delete-content]");
    if (remove) {
      if (!confirm("Remove your content from the community?")) return;
      await api(
        `/${{ review: "reviews", thread: "threads", comment: "comments" }[remove.dataset.type]}/${remove.dataset.deleteContent}`,
        { method: "DELETE" },
      );
      if (remove.dataset.type === "review")
        state.subjects = await api("/community/subjects");
      if (remove.dataset.type === "thread") {
        await openSubject(
          "course",
          state.threadCourse ||
            state.detail?.key ||
            state.subjects.course[0].key,
        );
      } else if (state.thread) await openThread(state.thread);
      else await openSubject(state.detail.kind, state.detail.key);
      return;
    }
    const createShare = event.target.closest("[data-create-share]");
    if (createShare) {
      await api(`/library/${createShare.dataset.createShare}/shares`, {
        method: "POST",
      });
      await openLibrary(createShare.dataset.createShare);
      return;
    }
    const revoke = event.target.closest("[data-revoke-share]");
    if (revoke) {
      await api(`/shares/${revoke.dataset.revokeShare}`, { method: "DELETE" });
      await openLibrary(state.library.id);
      return;
    }
    const deletion = event.target.closest("[data-delete-schedule]");
    if (deletion) {
      if (
        !confirm("Delete this saved draft and revoke all of its share links?")
      )
        return;
      await api(`/library/${deletion.dataset.deleteSchedule}`, {
        method: "DELETE",
      });
      $("library-dialog").close();
      await loadTab();
      return;
    }
    const moderate = event.target.closest("[data-moderate]");
    if (moderate) {
      const note = prompt(
        "Record a short reason for this moderation decision:",
      );
      if (!note) return;
      await api(`/moderation/reports/${moderate.dataset.moderate}`, {
        method: "POST",
        data: { action: moderate.dataset.action, note },
      });
      await loadTab();
      notice("Moderation decision recorded.");
      return;
    }
  } catch (error) {
    notice(error.message, true);
  }
});
document.addEventListener("submit", async (event) => {
  const form = event.target;
  if (
    !["review-form", "thread-form", "comment-form", "rename-form"].includes(
      form.id,
    )
  )
    return;
  event.preventDefault();
  const button = form.querySelector("button");
  button.disabled = true;
  const data = Object.fromEntries(new FormData(form));
  try {
    if (form.id === "review-form") {
      await api("/reviews", {
        method: "PUT",
        data: {
          ...data,
          rating: Number(data.rating),
          difficulty: Number(data.difficulty),
          kind: state.detail.kind,
          subject_key: state.detail.key,
        },
      });
      await openSubject(state.detail.kind, state.detail.key);
      notice("Your review is published. Thank you for adding context.");
      state.subjects = await api("/community/subjects");
    }
    if (form.id === "thread-form") {
      const thread = await api("/threads", {
        method: "POST",
        data: { ...data, course_key: state.detail.key },
      });
      await openThread(thread.id);
    }
    if (form.id === "comment-form") {
      await api(`/threads/${state.thread}/comments`, { method: "POST", data });
      await openThread(state.thread);
    }
    if (form.id === "rename-form") {
      await api(`/library/${state.library.id}`, {
        method: "PUT",
        data: {
          name: data.name,
          version: state.library.version,
          draft: state.library.draft,
        },
      });
      await openLibrary(state.library.id);
      await loadTab();
    }
  } catch (error) {
    form.querySelector(".form-error").textContent = error.message;
  } finally {
    button.disabled = false;
  }
});
window.addEventListener("hashchange", loadTab);
document.addEventListener("fcs-account", () => {
  if (state.subjects) loadTab();
  refreshAlerts();
  if ($("subject-dialog").open) {
    if (state.thread) openThread(state.thread);
    else if (state.detail) openSubject(state.detail.kind, state.detail.key);
  }
});
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) refreshAlerts();
});
setInterval(() => {
  if (!document.hidden) refreshAlerts();
}, 60000);
async function init() {
  try {
    state.subjects = await api("/community/subjects");
    $("campus-term").textContent = state.subjects.term_name;
    await loadTab();
    await refreshAlerts();
    const query = new URLSearchParams(location.search);
    if (query.get("subject"))
      await openSubject(query.get("kind") || "course", query.get("subject"));
    if (query.get("thread")) await openThread(query.get("thread"));
  } catch (error) {
    $("campus-content").innerHTML = empty(
      "Campus is unavailable.",
      esc(error.message),
    );
    notice(error.message, true);
  }
}
init();
