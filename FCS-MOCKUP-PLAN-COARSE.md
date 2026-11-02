# FCS V3 Mockup Plan — Coarse Phases (Cost-Optimized)

Fewer phases, bigger chunks. Designed for a paid model where each API call counts.

---

## Phase A: Foundation (Catalog + Builder + Saved)

Everything a student needs to build and save a schedule. One self-contained file.

**File:** `phaseA/index.html`

**Views:**
1. Course Catalog — search, department chips, credit filter, paginated table with course/instructor/schedule/credits/seats/rating. Rows clickable to select.
2. Schedule Builder — left panel (selected courses, credit sliders, day exclusions, generate button), right panel (timetable grid with colored blocks, stats bar, ranked generated schedules list).
3. Saved Schedules — grid of saved schedule cards with load/delete.

**Interactions:** Click to select courses, switch views via tabs, credit sliders update live, prev/next combo navigation.

---

## Phase B: Intelligence Layer (Instructors + Data + Schedule Scoring)

The data-driven features that make FCS smarter than a spreadsheet. Extends Phase A.

**File:** `phaseB/index.html`

**New views added:**
1. Instructor Profile — effectiveness index (quality/difficulty/pass rate/avg grade), grade distribution bar chart, teaching style tags, office hours, course history, student reviews.
2. Instructor Comparison — side-by-side cards for two instructors, GPA-based prediction ("you'd avg B+ with Dr. Smith").
3. Course Detail — grade distribution chart, difficulty trend, workload trend, retake rate, prerequisite chain.
4. "Will It Fill?" — seat velocity, fill prediction with confidence interval, historical data.
5. Schedule Health Score — breakdown into components (time conflict, commute, workload, grade prediction, seat urgency), visual gauge.
6. Schedule Stress Test — risk flags (exam conflicts, no free day, burnout risk), energy forecast.

**Interactions:** Click instructor name → profile, click "Compare" → comparison view, click course → detail page, health score expandable breakdown.

---

## Phase C: Community + Game Day (Reviews, Voting, Waitlist, Monitoring)

The social and real-time features. Extends Phase B.

**File:** `phaseC/index.html`

**New views added:**
1. Published Schedules Feed — community schedules with upvote/downvote, fork, comments.
2. Instructor Review Form — star ratings, grade received, recommend toggle, anonymous option.
3. Semester Wrapped — personalized end-of-semester summary, shareable card.
4. Waitlist Strategy — odds, seat velocity, auto-swap toggle, safe alternative.
5. Seat Monitor Dashboard — watched sections, seat counts, trend, fill predictions.
6. Time Protector — protected time blocks grid, conflict detection.
7. Textbook Cost Calculator — per-course textbook prices, total per schedule.
8. Commute-Aware — walking time between buildings, travel visualization.

**Interactions:** Upvote/downvote, fork schedule, submit reviews, toggle auto-swap, drag to create protected blocks.

---

## Phase D: Agent + Degree Planning (AI Assistant, Course History, Career Path)

The agentic layer and long-term planning features. Extends Phase C.

**File:** `phaseD/index.html`

**New views added:**
1. Agent Chat Panel — slide-in sidebar, suggested prompts, tool call visualization, action confirmation, audit log.
2. Agent Memory — what the agent knows about the user (profile, preferences, history), editable.
3. Proactive Suggestions — contextual hints in main UI ("Registration in 3 days", "CHEM201-A opened").
4. Course History Input — search-as-you-type to add completed courses, grade selector, GPA calculator, transcript import.
5. Degree Progress — prerequisite chain visualization, completed/in-progress/remaining courses, graduation timeline.
6. Semester Path Planner — drag-and-drop courses across semesters, credit load, difficulty heatmap.
7. Course Substitution Finder — "I need a humanities elective" → ranked results.
8. Chatbot Full Page — natural language interface, rich responses (schedules + instructor cards + recommendations).
9. AI Career Path Advisor — med school vs industry paths, visual career tree.

**Interactions:** Type prompts to agent, confirm actions, drag courses in planner, connect with study buddies, import transcripts.

---

## File Structure

```
fcs-mockups/
├── phaseA/
│   └── index.html
├── phaseB/
│   └── index.html
├── phaseC/
│   └── index.html
├── phaseD/
│   └── index.html
└── shared/
    └── components.js
```

## Design System (all phases)

- **Colors:** Brand blue (#2563eb), green/amber/red for states
- **Font:** Inter, consistent scale
- **Components:** Chips, cards, tables, modals, tooltips
- **Each file:** Single HTML, Tailwind CDN, vanilla JS, hardcoded data, self-contained
- **No external dependencies** except Tailwind + Google Fonts

## Cost Estimate

4 API calls (one per phase). Each phase is a complete, self-contained HTML file. The model produces one file per phase, you preview it, give feedback, move to next.
