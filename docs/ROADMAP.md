# FCS product and delivery plan

## Current implementation status — October 13, 2026

The local app now includes accounts, private named/versioned schedules, read-only revocable shares, ICS calendar export, course and teacher reviews, course discussions, study-group membership, comments, reporting/moderation, seat watches, and in-app opening alerts. Persistence uses SQLite on one host, with separate API modules for identity, library, community, and availability. See PLATFORM_PLAN.md for the implemented journeys and boundaries.

Institutional sign-in, enrollment verification, email/push delivery, an ingestion worker/outbox, multi-host PostgreSQL, source capture-time metadata, and actual student usability testing remain future work. Historical phase descriptions below describe the larger direction; the local implementation has delivered the first slices of phases 2–5.

## Direction

Make FCS the place students use to plan a semester, understand their options, and connect around courses. The first useful outcome is a workable week. Community features should make course decisions more informed without making schedule planning harder.

Start with FCCU and one active term. Preserve the scraper and Flask deployment while separating the domain logic from page routes. Introduce persistence and accounts for features that need ownership and cross-visit state; keep the planner independent of sign-in. A useful planner should work before a student signs in.

## Current system audit

The original application uses Flask, delimited text course data, and one large HTML template containing styles and browser logic. Import-time globals hold the active catalog. Filtering and output formatting are repeated in routes. Generation first enumerates credit combinations, then filters duplicates and clashes; its cost grows rapidly as shortlists expand. It truncates fractional credits and treats adjacent classes as overlapping.

The ingestion workflow commits files under `scraper/`, while the web app originally looks only in the repository root. The webhook has a default credential, accepts arbitrary term strings in filesystem paths, and writes data before validating it. Course identities are embedded in tuple positions. There is no test suite, architectural guide, or distinction between scraper capture time and local filesystem time.

## Phase 1 — a dependable planner (implemented in this iteration)

**Student flow:** search → preview section details and availability → add to week → see clashes → keep alternatives → generate possibilities → choose a result → save/export.

Delivered:

- A responsive catalog and weekly calendar with a list view and print styles.
- Fast local search and department/open-seat filters.
- Section details including instructors, rooms, primary meetings, and alternate meetings.
- One section per course when adding directly; alternatives remain in the shortlist.
- Visible overlap detection and side-by-side calendar events.
- Per-term device drafts with JSON import/export and missing-section handling.
- Required-course controls, decimal credit ranges, bounded schedule generation, and visible search-limit feedback.
- Application factory, normalized catalog repository, pure scheduling service, versioned API, and legacy adapters.
- No implicit webhook secret; authenticated, validated ingestion with atomic file replacement.
- Backend regression suite and CI.

**Acceptance:** a student can build and restore a draft without an account, inspect every meeting, distinguish a full section from an open one, and understand when a timetable is incomplete or a search was limited. Backend tests must show parity with a small exhaustive reference and check alternate meetings, adjacent meetings, fractional credits, and invalid inputs.

**Remaining planner improvements:** named multiple drafts, undo, section lock, blocked personal time, preferred free days, gap/travel-time rules, availability refresh, persistent catalog revision history, calendar export, and accessible bulk comparison. Add ranking only after the rules are explained and tested. Scheduling results are possibilities, not recommendations about academic eligibility.

## Phase 2 — persistence and schedule sharing

SQLite implements local account persistence now. Move to PostgreSQL and formal migration tooling when multi-host deployment is needed. Add an identity provider, private schedules, named draft versions, and explicit share links. Keep anonymous device drafts and offer a one-time import after sign-in.

Core entities: User, Term, Course, Section, Meeting, Instructor, Schedule, ScheduleItem, ShareLink, and CatalogRevision. Distinguish a durable course from a term-specific section. Store snapshot references so changing catalogs can be reconciled without silently deleting a student's plan. Share links should be random, revocable, and read-only by default; private schedules remain private.

**Acceptance:** two devices show the same saved draft; concurrent edits have revision checks; revoke a share link and it stops working; a term change does not overwrite another term's plan; account deletion removes private data.

## Phase 3 — seat watches and alerts

First improve ingestion: record source URL, captured_at, revision, parse counts, and failures. Preserve the last known good catalog if fetching or parsing fails. Treat a suspicious empty catalog as a failed update rather than “all sections disappeared.” Measure completeness before replacing a catalog.

Add a seat-history table, WatchSubscription, and NotificationDelivery records. After a valid revision, compare section availability; create an event when a watched section transitions from no seats to available seats. Use a worker and durable outbox for delivery, with deduplication by subscription and catalog revision. Respect the source's permitted access cadence. The existing 30-minute workflow implies delayed alerts, not instant registration guarantees.

Start with in-app alerts. Add email only after delivery preferences and unsubscribe behavior work. Browser push comes later. Subscription status must show freshness, delivery state, and that an alert cannot reserve a seat.

**Acceptance:** a real zero-to-positive transition produces one notification; repeated scraping does not duplicate it; transient failures do not produce false alerts; subscriptions can be paused or removed; retries are idempotent; delivery failures are visible to operations.

## Phase 4 — course and instructor reviews

Add separate review subjects for courses and instructors, with a term context. Introduce verified enrollment only when there is a legitimate verification mechanism; do not imply that sign-in alone proves enrollment.

Start with structured dimensions and a short optional narrative: workload, clarity, feedback, and useful preparation. Show rating distributions and sample size. Let students edit their own review. Publish clear community rules, report controls, moderation queues, and appeals before open publishing. Never import or fabricate review content to make the platform look active.

**Acceptance:** only an authorized author can edit a review; reporting and moderation leave an audit trail; private student information is removed; aggregates require a defined minimum sample; spam controls and rate limits work; archived reviews retain correct term context.

## Phase 5 — a campus community

Start with discussions scoped to courses and terms, then study groups and opt-in schedule sharing. Defer a global feed, direct messages, and recommendation algorithms until there is demonstrated demand and moderation capacity.

Entities: Discussion, Comment, Membership, Reaction, Report, and ModerationAction. Use pagination, authorization, rate limits, soft deletion, and threading limits. Keep moderation ownership clear and provide blocking before adding private messaging.

**Acceptance:** visibility matches membership, reports reach the right queue, deleted content is handled consistently, abuse controls are exercised, and planning remains usable independently of the social area.

## Delivery order and decisions

1. Review this planner with real students and record task failures.
2. Complete capture-time metadata, ingestion tests, and catalog revisions before public seat watches.
3. Add persistent named schedules and sharing before community content.
4. Add seat watches as an independently testable slice.
5. Launch reviews behind moderation tooling, then course discussions.

Prefer a modular monolith. Each phase should ship as a complete student flow with its own tests and operational requirements. Extract a service only when measured load, team ownership, or failure isolation makes it useful.

Open decisions for the next session: institution approval/source terms, identity and enrollment verification, hosting/database budget, moderation ownership, accessibility testing with students, and the notification channel. None of these needs to block the current local planner.
