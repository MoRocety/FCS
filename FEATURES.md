# FCS Features: Built, Live, Mocked, Planned

Compiled 2026-11-02 from the plans, mockups and code in this archive. Each feature is grouped by how far it got.

| Status | Source |
|---|---|
| Built and tested | `2_Mac2_Personal_FCS_Oct2026/FCS` (78 automated tests in `tests/`, manual checklist in `docs/VERIFICATION.md`) |
| Live in v1 | GitHub `MoRocety/FCS` `main`, the current site |
| Mocked up | `1_Dell_Work_Jun2026/mockups/` (clickable HTML with hardcoded data, no backend) |
| Planned only | `1_Dell_Work_Jun2026/plans/FCS-V3-PLAN.md`, plus the deferred items in the October docs |

## 1. Built and tested (October 2026 build, Mac 2)

### Scheduling engine
- Clash detection that checks primary and alternate meetings (labs), allows back-to-back classes, and catches a meeting fully inside another
- Credit ranges with decimals and zero credits
- Results match an exhaustive reference search (`test_engine_parity.py`)
- Bounded generation that reports when a search was cut off
- Resumable exhaustive search: pages through every valid schedule with no repeats, using a signed cursor that detects tampering (`test_search_continuation.py`)
- Nested Boolean course rules (AND / OR / NOT / "not taking"), replacing "crucial courses". It has a visual block editor with live preview and safe import, and old v1 required-course settings migrate automatically (`rules.test.mjs`, `test_rules.py`).
- A lecture that overlaps its own lab is excluded on purpose (`test_lecture_overlapping_own_lab_is_excluded`). This is the COMP 206 C case.

### Planner UI
- Search, department filter and open-seats filter
- Section details: instructors, rooms, alternate meetings
- Weekly calendar with overlap warnings, plus a list view, print styles, and a phone layout
- Device drafts saved per term, with JSON import/export and handling for sections that disappear. A half-typed credit field can't wipe a draft (`draft-state.test.mjs`).

### Accounts and library
- Sign-in with CSRF protection and throttling
- Named, versioned saved schedules with edit-conflict detection
- Read-only share links that are snapshots and can be revoked. Deleting a draft revokes its links.
- ICS calendar export, using semester dates the student enters

### Community
- Course and instructor reviews (one per person per term), with ratings validation
- Course discussions, comments and study groups (opt-in membership)
- Reporting and moderation with an audit trail. Hidden content can't be quietly republished.
- Campus media feed: up to four photos or one clip per post, metadata stripped, size, pixel and video limits, likes, comments, category and course filters, reports (`test_media.py`, `media-draft.test.mjs`)

### Seat watches
- In-app alert when a watched section goes from full to open
- Duplicate alerts suppressed, alerts can fire again if a section reopens later, and an old catalog snapshot can't trigger a false alert

### Ingestion
- The webhook refuses to run without a secret configured and blocks path traversal
- Data is validated before saving, files are replaced atomically, and a broken catalog doesn't take down the home page

## 2. Live in v1 (the current site)
- Shortlisting sections, generating clash-free combinations, min/max credits, crucial courses
- Catalog with department, course and instructor filters and pagination; seat counts
- Scraper that updates every 30 minutes via GitHub Actions and a webhook; active-term switching; a missing-course alert

## 3. Mocked up (June 2026, `mockups/fcs-mockups-v4/`)
- Catalog, Builder (including a generated-schedule variant) and Saved
- Instructor profile: an effectiveness index, grade distribution and teaching tags
- Compare instructors, with a predicted grade
- Course detail: grade, difficulty and workload trends, prerequisites
- Will It Fill? seat-velocity prediction
- Schedule Health Score and Stress Test: burnout and exam-conflict flags, energy forecast
- Waitlist strategy with auto-swap, and a Seat monitor dashboard
- Time Protector: meal, prayer and gym blocks
- Textbook cost calculator and Commute-aware walking times
- Community feed: published schedules, voting, forking
- Review form
- Semester Wrapped
- Agent chat, with visible tool calls, confirmations and an audit log
- Agent memory and Proactive suggestions
- Course history with a GPA calculator and transcript import
- Degree progress and a prerequisite chain
- Substitution finder
- Career path advisor
- Full-page chatbot

Earlier passes of the same ideas are in `fcs-mockup/`, `fcs-mockups_phase1-9/` and `fcs-mockups-v3/`.

## 4. Planned only

### From FCS-V3-PLAN.md
- **Platform:** a FastAPI, Postgres and Next.js rebuild; Google OAuth; SSE streaming generation; Web Push and email alerts; a PDF/PNG export; a drag-and-drop Boolean constraint builder; soft scoring and ranking; deployment on Railway and Vercel, with a redirect from v1
- **Community and data:** a forum, favourites, a rules-based recommendation engine, then ML models; multi-university expansion; the "data moat" (saved schedules, votes, reviews and searches feeding the recommendations)
- **Creative ideas:**
  - Schedule difficulty heatmap
  - Schedule compatibility match and Study Buddy Matcher
  - Course load simulator
  - Schedule history and patterns
  - Schedule archetypes
  - Schedule Tournament
  - "What If" simulator
  - Aesthetic score
  - Room quality intel
  - Professor consistency tracker
  - Reverse schedule builder
  - Anonymous critique
  - Professor Hunter
  - Seat trading
  - Workload DNA
  - Drop-risk prediction
  - Office-hours alignment
  - Grade trajectory
  - Social proof
  - Exam conflict detector
  - Instructor schedule history
  - Schedule comparison engine
- **Agentic vision ("Cursor for University Management"):** an agent loop with tools, memory, trust and safety rules, and proactive behaviour

### Deferred in the October docs
- University sign-in and enrollment verification
- Email/push delivery and a background worker
- Postgres for multiple hosts
- Degree-requirement planning based on official requirements
- Events and clubs
- Deadline tracking
- Textbook exchange
- Direct messages
- Recommendation algorithms
- Grade predictions
