const data = JSON.parse(document.getElementById("shared-data").textContent);
const esc = (v) =>
  String(v).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const names = {
  M: "Monday",
  T: "Tuesday",
  W: "Wednesday",
  R: "Thursday",
  F: "Friday",
  S: "Saturday",
  U: "Sunday",
};
const days = [
  "M",
  "T",
  "W",
  "R",
  "F",
  ...["S", "U"].filter((d) =>
    data.sections.some((s) => s.meetings.some((m) => m.days.includes(d))),
  ),
];
document.getElementById("shared-week").innerHTML = days
  .map(
    (day) =>
      `<section class="shared-day"><h3>${names[day]}</h3>${
        data.sections
          .flatMap((s) =>
            s.meetings
              .filter((m) => m.days.includes(day))
              .map((m) => ({ s, m })),
          )
          .sort((a, b) => a.m.start.localeCompare(b.m.start))
          .map(
            ({ s, m }) =>
              `<div class="shared-meeting"><strong>${esc(s.department)} ${esc(s.number)} / ${esc(s.section)}</strong><span>${esc(s.name)}</span><span>${m.start}–${m.end} · ${esc(m.room)}</span><span>${esc(s.instructor)}</span></div>`,
          )
          .join("") || '<p class="muted small">A free day.</p>'
      }</section>`,
  )
  .join("");
const unknown = data.sections.filter((s) => !s.meetings.length);
document.getElementById("shared-unknown").textContent = unknown.length
  ? `Unannounced meeting times: ${unknown.map((s) => `${s.department} ${s.number}`).join(", ")}. Confirm these before registering.`
  : "";
document.getElementById("shared-download").addEventListener("click", () => {
  const ids = data.sections.map((s) => s.id);
  const url = URL.createObjectURL(
    new Blob(
      [
        JSON.stringify(
          {
            version: 2,
            term: data.term,
            section_ids: ids,
            shortlist_ids: ids,
            rules: { op: "and", children: [] },
          },
          null,
          2,
        ),
      ],
      { type: "application/json" },
    ),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = `fcs-shared-${data.term}.json`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
document
  .getElementById("shared-print")
  .addEventListener("click", () => window.print());
