# FCS V3 Mockup Plan — Phased UI/UX Development

This plan is for a standalone agent that builds mockups phase by phase. It does not reference FCCU-Advisior or any competitor. All ideas come from our own vision.

---

## Phase 1: Core Scheduling Flow

**Goal:** Mockup the fundamental user journey — browse courses, select them, generate schedules, view the grid.

**Deliverable:** `phase1/index.html` — single file, Tailwind CDN, vanilla JS.

### Views to mockup:

1. **Course Catalog**
   - Navbar: logo, nav tabs (Courses / Schedule Builder / Saved), search bar, user avatar
   - Filter bar: search input, department chips (All, BIOL, CHEM, MATH, CS, ENGL, PHYS, HIST), credit filter dropdown
   - Stats bar: "Showing X courses", selected count, "Build Schedule" button
   - Course table: checkbox, course code + name, instructor, schedule (days + time), credits, seats (color-coded), rating
   - Pagination

2. **Schedule Builder**
   - Left panel: selected courses list (removable), credit range sliders (min/max), day exclusion toggles (M/T/W/R/F), max courses dropdown, crucial course chips, "Generate Schedules" button
   - Right panel: visual timetable grid (8AM-4PM, Mon-Fri), color-coded class blocks, schedule stats (credits, courses, hours/week, health score)
   - Below grid: ranked list of generated schedules with scores

3. **Saved Schedules**
   - Grid of saved schedule cards with course lists, credit totals, health scores, load/delete actions

### Interactions:
- Click table rows to select/deselect courses
- "Build Schedule" switches to builder view with selected courses
- Credit sliders update labels live
- Prev/Next combo navigation
- Tab navigation between views

---

## Phase 2: Instructor Intelligence

**Goal:** Mockup the instructor data layer — effectiveness index, multi-dimensional ratings, comparison.

**Deliverable:** `phase2/index.html` — extends Phase 1.

### Views to mockup:

1. **Instructor Profile Page**
   - Name, photo placeholder, department
   - Effectiveness Index card: quality rating (1-5), difficulty rating (1-5), first-time pass rate, avg grade, retake rate
   - Grade distribution bar chart (A/B/C/D/F breakdown)
   - Teaching style tags: "lecture-heavy", "project-based", "open-book exams", "group work required"
   - Office hours alignment: "MWF 2-3PM, Room 305"
   - Course history: which courses they've taught, when, grade distributions per term
   - Student reviews list (anonymized)

2. **Instructor Comparison View**
   - Side-by-side cards for two instructors teaching the same course
   - Quality, difficulty, pass rate, avg grade compared
   - "Based on your GPA (3.4), you'd avg B+ with Dr. Smith, B- with Dr. Jones"
   - Section availability and seat counts

3. **Instructor Search**
   - Search by name, department, course
   - Filter by quality rating, difficulty rating, teaching style
   - Results as cards with key metrics

### Interactions:
- Click instructor name from course table → instructor profile
- "Compare" button on instructor profile → comparison view
- Click teaching style tag → filter instructors by that style

---

## Phase 3: Schedule Intelligence

**Goal:** Mockup the advanced scheduling features — health score, archetypes, tournament, what-if simulator.

**Deliverable:** `phase3/index.html` — extends Phase 2.

### Views to mockup:

1. **Schedule Health Score Detail**
   - Breakdown of the 0-100 score: time conflict risk, commute feasibility, workload balance, grade prediction, seat urgency
   - Visual gauge/meter for each component
   - Suggestions: "Improve score by swapping CHEM201-A for CHEM201-B"

2. **Schedule Archetypes**
   - Selection screen: 6 archetypes as cards
     - The 4-Day Weekend (no Friday)
     - The Morning Bird (done by 1PM)
     - The Late Riser (no classes before 11AM)
     - The Balanced Life (no back-to-back)
     - The Grindset (compact 2-3 days)
     - The No-Death-Day (no 3+ consecutive)
   - Each card has a mini visual preview of what that schedule looks like
   - Click one → generates matching schedules

3. **Schedule Tournament**
   - Bracket-style UI: 8 schedules → 4 → 2 → 1 winner
   - Each matchup: side-by-side comparison of two schedules
   - User picks one per round
   - Final screen: "Your ideal schedule" with the winning schedule
   - Data collected: which tradeoffs the user prioritized

4. **What-If Simulator**
   - Current schedule displayed
   - User can click a course block to "swap" or "drop"
   - Side panel shows consequences: credits change, health score change, commute change, workload change
   - "What if" history: list of scenarios tested

5. **Schedule Stress Test**
   - Current schedule with risk flags:
     - "Week 8 has 3 midterms"
     - "No free day for 5 consecutive days"
     - "Wednesday: 2 labs + 1 lecture back-to-back"
   - Energy forecast: color-coded daily energy levels
   - Commute analysis: walking time between buildings

### Interactions:
- Click health score → expanded breakdown
- Select archetype → generates filtered schedules
- Tournament: click schedule to advance it
- What-if: click block → see live consequences

---

## Phase 4: Data Layer — Grade Distributions & Predictions

**Goal:** Mockup the data-dependent features — grade distributions, seat predictions, course difficulty trends.

**Deliverable:** `phase4/index.html` — extends Phase 3.

### Views to mockup:

1. **Course Detail Page**
   - Course code, title, credits, description
   - Grade distribution chart (bar chart, A/B/C/D/F)
   - Source indicator: "Based on 47 self-reported grades" with confidence level
   - Difficulty trend: "Difficulty increased from 3.1 to 3.8 after 2024 curriculum change"
   - Workload trend: "Workload increased from 15 to 22 hrs/week"
   - Retake rate: "28% of students retake this course"
   - Related courses: prerequisite chain visualizer

2. **"Will It Fill?" Prediction Card**
   - Current seats: 4/28
   - Velocity: "Losing ~1 seat/day"
   - Prediction: "78% chance full by Thursday"
   - Historical data: "Filled in 3 days last year"
   - Confidence interval visualization

3. **Seat History Chart**
   - Line chart showing seat count over time for a section
   - Markers for key events: "Registration opened", "Add/drop deadline"
   - Trend line projecting when it will fill

4. **Course Difficulty Heatmap**
   - 4-year calendar grid
   - Color-coded red/yellow/green per semester
   - Hover to see: avg credits, avg difficulty, avg GPA, sample size
   - Click semester to see course breakdown

### Interactions:
- Click course in catalog → course detail page
- "Will It Fill?" card appears on section views
- Click heatmap cell → expanded semester view

---

## Phase 5: Community Layer

**Goal:** Mockup the social features — published schedules, reviews, voting, sharing.

**Deliverable:** `phase5/index.html` — extends Phase 4.

### Views to mockup:

1. **Published Schedules Feed**
   - List of community-published schedules
   - Each card: name, author, courses, credits, score, upvotes/downvotes, views
   - Sort by: top rated, newest, most saved
   - Filter by: major, term, archetype

2. **Schedule Detail Page (Shared)**
   - Full timetable grid
   - Author info, publish date
   - Upvote/downvote buttons with counts
   - "Fork this schedule" button (copy to your saved)
   - Comments section
   - "23 students saved this schedule"

3. **Instructor Review Form**
   - Star ratings: quality (1-5), difficulty (1-5), workload (1-5)
   - Grade received dropdown
   - "Would you recommend?" toggle
   - Review text area
   - "Post anonymously" checkbox

4. **Instructor Reviews List**
   - Reviews sorted by recency/helpfulness
   - Each review: anonymized author, ratings, grade received, review text, helpfulness votes
   - Aggregate stats at top

5. **Anonymous Schedule Critique**
   - Post a schedule for community feedback
   - Comment thread with reactions
   - "Brave" / "Solid" / "Risky" quick reactions

6. **Semester Wrapped**
   - Personalized end-of-semester summary
   - "You spent 22 hours/week in class"
   - "Your hardest week had 4 exams"
   - "You saved 4 schedules before choosing one"
   - Shareable card format (image export)

### Interactions:
- Click "Publish" on saved schedule → confirmation → appears in feed
- Upvote/downvote on schedules
- "Fork" → copies to saved schedules
- Review form → submit → appears on instructor profile

---

## Phase 6: Agent Interface

**Goal:** Mockup the Cursor-style agent — chat sidebar, tool calls, proactive suggestions.

**Deliverable:** `phase6/index.html` — extends Phase 5.

### Views to mockup:

1. **Agent Chat Panel**
   - Fixed bottom-right button → slides open panel
   - Chat interface: user messages (right-aligned, brand color), agent messages (left-aligned, gray)
   - Agent responds with text + actions
   - Tool call visualization: "Called: generate_schedules(constraints)" shown as collapsible log
   - Typing indicator

2. **Agent Capabilities Menu**
   - Suggested prompts displayed as clickable chips:
     - "Find me the best schedule"
     - "Compare instructors for CHEM201"
     - "How many seats are left?"
     - "Can I handle 16 credits?"
     - "Import my transcript"
     - "What courses do I need to graduate?"

3. **Agent Action Confirmation**
   - When agent proposes an action (save schedule, add to watchlist):
     - Shows what it's about to do
     - "Save Schedule 1 as 'Spring 2027 Plan A'"
     - Confirm / Cancel buttons
   - Audit log: list of all actions taken

4. **Proactive Suggestions**
   - Contextual hints that appear in the main UI:
     - "Registration opens in 3 days. Want me to prep your priority list?"
     - "CHEM201-A just opened. Want me to grab it?"
     - "This schedule scores 78/100. Want me to find better?"
   - Dismissible, non-intrusive

5. **Agent Memory Panel**
   - Shows what the agent knows about the user:
     - Profile: major, year, graduation
     - Preferences: morning person, no Fridays, protect lunch
     - History: 3 schedules generated, 2 saved, 1 reviewed
   - User can edit/delete memory entries

### Interactions:
- Click suggested prompt → sends to agent
- Agent responds with text + tool calls
- Confirm action → agent executes
- Click proactive suggestion → agent acts

---

## Phase 7: Degree Planning & Course History

**Goal:** Mockup the degree audit and course history features.

**Deliverable:** `phase7/index.html` — extends Phase 6.

### Views to mockup:

1. **Course History Input**
   - Search-as-you-type to add completed courses
   - Grade selector per course (A, A-, B+, B, etc.)
   - Term taken selector
   - "Import from transcript" button (file upload)
   - Running GPA calculator
   - Visual progress bar: "72 of 120 credits complete"

2. **Degree Progress View**
   - Tree/graph visualization of prerequisite chains
   - Completed courses (green checkmarks)
   - In-progress courses (yellow dots)
   - Remaining courses (gray circles)
   - "You need 3 more science electives"
   - "BIOL310 is only offered Fall — take it now or wait a year"

3. **Semester Path Planner**
   - Remaining semesters displayed as columns
   - Drag-and-drop courses between semesters
   - Credit load per semester
   - Difficulty heatmap per semester
   - "Graduation: Spring 2029 (on track)"

4. **Course Substitution Finder**
   - "I need a humanities elective"
   - Results: list of qualifying courses with difficulty, instructor quality, seat availability
   - One-click "add to schedule builder"

5. **Transcript Import Flow**
   - Upload PDF/CSV
   - Preview extracted courses
   - Confirm/edit before saving
   - "Found 24 courses. Is this correct?"

### Interactions:
- Add courses to history → updates degree progress
- Drag courses in semester planner → rearranges path
- Click "add to schedule builder" → switches to builder with course pre-selected

---

## Phase 8: Game Day Features

**Goal:** Mockup the real-time, registration-day features — waitlist strategy, seat trading, time protector.

**Deliverable:** `phase8/index.html` — extends Phase 7.

### Views to mockup:

1. **Waitlist Strategy Card**
   - Section: CHEM201-A
   - Status: Waitlisted (#3 of 8)
   - Historical odds: "60% chance of getting in"
   - Seat velocity: "Losing ~1 seat/day"
   - Safe alternative: "CHEM201-B has 4 seats"
   - Auto-swap toggle: "If seat opens, swap automatically"

2. **Seat Monitor Dashboard**
   - List of watched sections
   - Current seat count, trend arrow, fill prediction
   - Last checked timestamp
   - "Add section" button

3. **Time Protector Settings**
   - Protected time blocks grid
   - User drags to create blocks: "Lunch 12-1PM", "Gym 4-6PM", "Jummah 1-2PM"
   - System shows which schedules violate protected blocks
   - "This schedule conflicts with your lunch block"

4. **Schedule Trading**
   - "You dropped CHEM201-A and helped 2 students get in. +50 karma"
   - Karma leaderboard
   - "Offer your seat" / "Claim a seat" actions

5. **Textbook Cost Calculator**
   - Per-course textbook list with prices
   - Total cost per schedule
   - "This schedule costs $410. This alternative costs $165"
   - Affiliate links to cheaper options

6. **Commute-Aware Scheduling**
   - User inputs location (dorm name or address)
   - Map visualization with walking routes
   - Travel time between buildings shown on schedule
   - "This 10-minute gap isn't enough — it's a 14-minute walk"

### Interactions:
- Toggle auto-swap on waitlisted sections
- Drag to create protected time blocks
- Click "offer seat" → confirms → notifies waitlisted students

---

## Phase 9: Chatbot & AI Features

**Goal:** Mockup the chatbot interface and AI-powered recommendations.

**Deliverable:** `phase9/index.html` — extends Phase 8.

### Views to mockup:

1. **Chatbot Interface**
   - Full-page chat view (not just sidebar)
   - Conversation threads
   - Agent has access to all platform data
   - Rich responses: text + schedule grids + instructor cards + course recommendations
   - "Based on your profile, here's what I recommend..."

2. **AI Course Recommendation**
   - "You've taken BIOL101, CHEM101, MATH201"
   - "Based on your Bio major, here are courses to consider"
   - Recommendations with reasoning: "CHEM201 because you need it for BIOL310"
   - Difficulty prediction: "Students with your GPA avg B+ in this course"

3. **AI Schedule Optimizer**
   - "I found a better version of your schedule"
   - Shows before/after comparison
   - "This version has higher-rated instructors and same courses"

4. **AI Study Buddy Match**
   - "3 students in your CHEM201 section are looking for study partners"
   - Anonymous profiles: "Student 1: prefers evenings, likes group study"
   - "Connect" button to initiate contact

5. **AI Career Path Advisor**
   - "If you want to go to med school, take these courses"
   - "If you want to work in industry, take these"
   - Visual career path tree
   - "Your current path aligns with med school requirements"

### Interactions:
- Type natural language prompts
- Agent responds with rich content
- Click recommendations to add to schedule builder
- Connect with study buddies

---

## Implementation Notes

### File structure:
```
fcs-mockups/
├── phase1/
│   └── index.html
├── phase2/
│   └── index.html
├── phase3/
│   └── index.html
├── phase4/
│   └── index.html
├── phase5/
│   └── index.html
├── phase6/
│   └── index.html
├── phase7/
│   └── index.html
├── phase8/
│   └── index.html
├── phase9/
│   └── index.html
└── shared/
    └── components.js    # Shared JS utilities
```

### Design system (consistent across all phases):
- **Colors:** Brand blue (#2563eb), green for positive, amber for warnings, red for danger
- **Typography:** Inter font, consistent scale (text-xs through text-2xl)
- **Spacing:** 4px grid, consistent padding/margins
- **Components:** Chips, cards, tables, modals, tooltips
- **Interactions:** Hover states, transitions, loading states
- **Responsive:** Mobile-first, breakpoints at sm/md/lg

### Each phase builds on the previous:
- Phase 1: Standalone
- Phase 2: Adds instructor views to Phase 1
- Phase 3: Adds schedule intelligence to Phase 2
- Phase 4: Adds data layer to Phase 3
- Phase 5: Adds community to Phase 4
- Phase 6: Adds agent to Phase 5
- Phase 7: Adds degree planning to Phase 6
- Phase 8: Adds game day features to Phase 7
- Phase 9: Adds chatbot/AI to Phase 8

### Mockup principles:
- Every mockup is a single HTML file with Tailwind CDN
- No external dependencies except Tailwind and Google Fonts
- Vanilla JavaScript for interactivity
- Hardcoded data (no API calls) — these are visual mockups, not functional apps
- Each phase is self-contained and can be previewed independently
- Realistic data that matches FCC's actual course catalog
