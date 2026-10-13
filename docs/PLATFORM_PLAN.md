# FCS university app — implementation plan

## Student journeys for this iteration

| Journey | Complete flow | Boundary |
| --- | --- | --- |
| Personal planning | Create an account → save a named planner draft → open, revise, or delete it | Planner still works anonymously; no enrollment verification |
| Schedule sharing | Save a schedule → create a read-only snapshot link → inspect or revoke the link | Sharing is deliberate; private shortlist and rule preferences are omitted |
| Calendar export | Choose semester dates → export weekly events as ICS | Dates are supplied by the student, never guessed |
| Course decisions | Find a course or teacher → read feedback → write or edit a review | Honest empty states and sample counts; no fabricated reviews |
| Course community | Start a discussion → reply → report inappropriate content | Course and term scope; no private messaging |
| Study groups | Create a study-group post → join or leave → see participants | Membership is opt-in; no private contact details exposed |
| Seat availability | Watch a section → ingest a changed catalog → receive an in-app alert when it opens | Snapshot-based, no reservation, no implied live university feed |
| Moderation | Report content → moderator examines it → dismiss or hide with an audit trail | Moderator promotion is a local administrative CLI operation |

## Architecture and data

Retain the modular monolith. Use SQLite with explicit schema initialization for the local, single-host application. Parameterized SQL, transactions, foreign keys, ownership checks, optimistic schedule versions, and tests are required. PostgreSQL and migrations become the next deployment step if multi-host operation is needed.

Modules: database schema/transactions; account identity and CSRF; persisted schedules and calendar export; community and moderation; catalog observations and seat alerts. The catalog remains the source of truth for course/section metadata. No client-supplied credits or meetings become authoritative.

Accounts use password hashing, HTTP-only sessions, same-site cookies, session CSRF tokens, and sign-in throttling. Persist a local session secret outside Git unless SECRET_KEY is configured. Community sign-in is not proof of institutional identity or enrollment.

Sharing stores immutable selected-section snapshots. A random bearer token grants read access; owners can revoke it. Course feedback has one active review per person, subject, and term. Reports and moderator decisions are separate records. Seat observations carry a sequence ID so a repeated zero-to-open cycle can alert again even when its content hash matches an older snapshot.

## Validation

Test anonymous/private access boundaries, cross-user edits, CSRF, login/logout, schedule version conflicts, snapshot revocation, valid ICS recurrence, review aggregates, report handling, membership idempotency, comment ownership, seat transitions, deduplication, and unchanged catalogs. Test UI flows in a separate disposable database. Keep the real local instance free of seed community content.

## After this iteration

Institutional identity, enrollment verification, email/push notifications, a durable worker/outbox, richer review dimensions, catalog capture metadata, campus events, degree-requirement planning, and calendar account integration. These require real policy/source integration or operational ownership; do not simulate them as working services.

## Delivered foundation and next university features

The journeys above are implemented locally. The API modules are separated by responsibility and the browser shares one session client across the planner and campus views. Device drafts preserve the last valid credit range while a field is incomplete, so a mid-edit reload cannot discard a whole week.

Next product slices, in order:

1. Named institutional terms and reliable capture-time/completeness metadata, so seat updates can show meaningful freshness.
2. Verified university identity and enrollment, with recovery, data export/deletion, and moderation appeals.
3. Prerequisite and degree-requirement planning backed by official academic requirements; never guess eligibility from course codes.
4. Campus events and club pages with organizer ownership, RSVP capacity, and moderation.
5. Personal assignment/deadline tracking and calendar account sync.
6. Textbook/resource exchange with reporting and explicit contact/privacy controls.

Implement these as independent complete flows. Direct messages, a global recommendation feed, marketplace payments, and unofficial grade predictions are deferred. The current course-linked conversations and study groups provide a useful social surface before those broader features.
