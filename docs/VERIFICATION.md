# Planner verification — October 13, 2026

Local backend checks passed: 17 unittest cases, JavaScript syntax check, and `git diff --check`. GitHub Actions is configured but has not been run remotely.

Browser checks:

- Search for COMP 102 and add section A: Tuesday/Thursday lectures and Friday lab appear.
- Shortlist section B and generate a 4-credit schedule: two alternatives appear.
- Reload: saved section and alternatives restore.
- Add ARTS 101 A and ARTS 102 A: overlap warning and conflict status appear.
- Import a draft from another term: rejected without replacing the current schedule.
- Import a valid five-course draft: 16 credits, five courses, no time clashes; required course controls restore.
- Generate from the imported shortlist: two 16-credit options appear.
- Desktop and 390-pixel phone layout: inspected visually; phone document width equals viewport width, and the timetable has its own horizontal overflow.

The JSON export action was invoked, but the in-app browser download event timed out, so the downloaded file was not independently inspected. Export uses the standard Blob/download-link browser flow. File import and per-device restoration were verified. Print stylesheet behavior was implemented but not verified in a print preview. No production deployment or remote CI run was performed.

Screenshots: [desktop](assets/planner-desktop.jpg), [phone](assets/planner-mobile.jpg).

## Nested rules update

22 backend tests and 6 JavaScript logic tests pass. Browser verification covered migration of the existing required-course draft, course pickers, nested OR and NOT groups, validation of empty groups, generation of two matching 16-credit options, and expression restoration after reload. The 390-pixel phone layout remains within its viewport. Drag-and-drop movement is implemented, but was not separately exercised in this browser test; sibling arrows and direct nested creation are alternative controls.

Preview: [nested rule builder](assets/rule-builder.jpg). New drafts use version 2; historical version 1 drafts remain importable.

## Usability refinement

22 backend tests and 11 JavaScript logic tests pass. Browser checks verified unfinished course placeholders, Undo/Redo, moving a condition into another group through the keyboard-accessible menu, negative condition feedback, wrapping the entire expression in NOT, and undoing those changes. Existing saved expressions retained their meaning. Current-week match badges are distinct from rule validation. The 390-pixel document width remains within its viewport.

The editor preserves the original inner AND/OR scope when switching an existing multi-condition group to NOT. Live preview and subtree movement have pure regression tests. Actual student comprehension testing remains future work; see RULE_EDITOR_DESIGN.md.

## Persisted campus features — October 13, 2026

41 backend tests and 14 JavaScript logic tests pass. Coverage includes session/CSRF boundaries, account and content ownership, login/logout, schedule version conflicts, immutable share snapshots and revocation, calendar dates/recurrence/escaping, course and instructor reviews, review uniqueness, moderation audit and republishing protection, thread/comment visibility, group membership, watch ownership, repeated seat-opening cycles, alert deduplication, persistent database accounts, and keeping the last valid credit range during partial edits.

Browser tests ran against `localhost:5051` with a separate disposable SQLite database and session-cookie name. Verified account registration/sign-in, course review submission, study-group creation/joining, posting a reply, adding a seat watch, saving a named draft, reopening/updating that draft, creating a read-only snapshot, and rendering its lecture and lab meetings. The real local database remains empty of seed accounts, reviews, discussions, schedules, and watches.

ICS response content and recurrence are verified by tests. In-app browser file-download completion remains unverified, as in the earlier planner iteration. Moderator decisions and seat transitions were exercised in backend tests; no actual university seat change or external notification was simulated in the real instance. Email/push delivery, institution identity verification, remote deployment, and a remote CI run remain outside this local implementation.

Catalog observation also checks source-file modification order, preventing a stale concurrent reader from rolling back the head and fabricating a second reopening. Tests cover this case and the additive schema upgrade. This ordering watermark is not presented as university capture time.

## Campus media and exhaustive search continuation

61 backend tests and 17 JavaScript tests pass locally. New media checks cover decoded/re-encoded images, metadata removal, a real FFmpeg video transcode and byte-range playback, malformed/oversized uploads, descriptions/categories/course references, failed multi-file cleanup, quota rollback, owner boundaries, idempotent likes, comment pagination, media-post/comment reporting, and hidden asset delivery. Schema 3 adds media tables while retaining the previous records and catalog-head migration.

Browser verification ran on port 5051 with a disposable SQLite database, media directory, and separate cookie. A real file-chooser upload displayed its preview, was published with a caption/description and COMP 220 link, received a like and comment, and appeared under Study but not Events. No console warnings/errors were observed. The 390-pixel feed and composer were inspected; a squeezed course filter was corrected to wrap onto its own row. The real instance has no fabricated feed content. Preview: [desktop QA upload](assets/media-feed-qa.jpg), [mobile QA feed](assets/media-feed-mobile.jpg), [real empty feed](assets/media-feed-desktop.jpg).

The original combinator is tested directly on 40 generated integer-credit shortlists, eight sampled real-catalog shortlists, and an internally overlapping lecture/lab case. The new engine matches their complete result sets. This does not claim an exhaustive comparison over the entire catalog or identical ordering. Fractional/zero credits and Boolean constraints remain extensions.

Resumable search tests cover exact complete enumeration through small result/work batches, zero-result intermediate pauses, no duplicates, exact final batches, and signed-cursor rejection after tampering or changing any input/catalog revision. Browser QA used seven unique nonclashing courses whose total fits the range: the planner reached 50 → 100 → all 127 nonempty combinations and removed the continuation button only after reporting completion. [Complete-search evidence](assets/search-complete-qa.jpg).

Video upload/decoding/playback is exercised in backend tests; the browser uploaded and interacted with a photo, rather than separately uploading a clip. No remote CI, institutional integration, or production deployment was performed. Media conversion is synchronous; storage cleanup, isolated workers, closed captions, and production retention policy remain future work.
