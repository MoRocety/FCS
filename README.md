# FCS

A course planner and student campus app for FCCU. Plan a week anonymously, or create an account to keep drafts, share schedules, watch seats, and participate in course conversations and a campus media feed.

## Run locally

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --port 5050
```

Open [the planner](http://127.0.0.1:5050) or [Campus](http://127.0.0.1:5050/campus). The app exposes `app:app` for WSGI and `create_app()` for isolated tests. Python 3.11 or later is supported by the CI configuration.

## Implemented journeys

- **Plan a semester:** search sections, see lectures/labs and weekend/evening meetings, shortlist alternatives, inspect conflicts, and enumerate all valid combinations through resumable search batches with nested Boolean course rules.
- **Keep possibilities:** per-term device drafts plus private named schedules in an account. Open, update, rename, copy, or delete saved drafts. Optimistic versions prevent silently overwriting another save.
- **Share a week:** deliberately create a revocable, read-only snapshot link. It contains the schedule name and selected course metadata; private shortlist, rules, credit range, and account identity are excluded. Later edits do not alter the snapshot.
- **Take it elsewhere:** versioned JSON import/export, printing, and weekly ICS calendar export using explicit semester dates and Asia/Karachi time.
- **Understand courses and teachers:** searchable profiles with overall/difficulty ratings, sample counts, and term-labelled student reviews. One review per subject per term per account; republishing edits it.
- **Talk and study together:** course discussions, comments, study-group posts, opt-in membership, author removal, and content reporting.
- **Share campus moments:** post up to four photos or one short video with a caption, category, optional course link, and accessible descriptions. Browse a chronological public feed, like, comment, remove your content, or report it.
- **Watch availability:** account seat watches and in-app alerts when a watched section changes from full to open in an observed catalog snapshot. Repeat observations do not duplicate alerts; a new reopening can notify again.
- **Moderate:** an authorized report queue with hide/dismiss decisions and an audit trail. Hiding a review prevents its author from republishing it through an edit/delete cycle.

The local instance starts without seed accounts or fabricated community content. Account registration does not verify university identity or enrollment. Seat counts remain snapshots and do not reserve seats. Email, push, institutional sign-in, and enrollment verification are not connected.

## Persistence and configuration

SQLite lives in `instance/fcs.sqlite3`, with schema version 3. Versions 1 and 2 are upgraded additively at startup without removing existing records. Local state and the session secret are ignored by Git. A persistent random session secret is created in `instance/.session-secret` unless `SECRET_KEY` is configured. Database and secret files use restricted filesystem permissions.

| Environment variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Stable session-signing secret for the deployment |
| `FCS_DATABASE` | SQLite path; defaults to the application instance directory |
| `FCS_MEDIA_ROOT` | Media storage path; defaults to `instance/media` |
| `FCS_COOKIE_NAME` | Cookie name, useful for isolated local test instances |
| `FCS_SECURE_COOKIES=1` | Secure session cookies on an HTTPS deployment |
| `WEBHOOK_SECRET` | Required authentication for course-data ingestion |
| `PORT` | Direct `python app.py` port; Flask CLI uses `--port` |

Promote an existing account for local moderation:

```sh
flask --app app promote-user existing_username
```

There is no public role-change endpoint. This command is for a trusted operator with access to the application filesystem. Back up the SQLite database, media directory, and session secret before moving hosts. Run behind a production WSGI server and HTTPS when deploying; no deployment or remote publication is performed by this iteration.

## Schedule generation

The core contract remains shortlisted sections + a credit range → every nonempty combination with at most one section per course and no overlapping lecture/lab meetings. Nested Boolean rules add another eligibility condition. A section whose own lecture and lab overlap is excluded, matching the original checker. Unannounced meeting times remain unverifiable and are disclosed.

Early pruning avoids branches that already exceed credits, cannot reach the minimum, contain clashes, or cannot satisfy the rules. A response processes at most 100,000 branches and returns at most 50 combinations, but preserves its unexplored search position in a signed continuation. **Find more schedules** resumes that search without repeating results. A pause with no matches can also continue. Only a completed search claims that all matches are present. These are exhaustive enumeration batches, not ranked top-N recommendations.

Continuation is tied to the catalog revision, shortlist order, credit range, required courses, and Boolean rules. Changing any input starts a new search; changing the catalog requires a reload. Both `/api/v1/schedules/generate` and the legacy `/submit` return `continuation` (opaque string or null), plus `limited` and schedule results. API clients send the original request again with that continuation to request the next batch. `limited: true` means more search remains, not that no additional solutions exist.

## Campus media

Open [Campus feed](http://127.0.0.1:5050/campus#feed). Browsing is public; posting, commenting, liking, reporting, and author removal use the same account and CSRF flow as course conversations. Categories are Campus, Study, Events, and Clubs. A course link associates a post with the catalog without claiming enrollment. Pagination uses IDs so loading older posts does not repeat newer ones.

Uploads accept JPEG/PNG/WebP photos (8 MB each, up to four) or one MP4/WebM clip (20 MB, up to 60 seconds). Every file requires a description. Photos are decoded, bounded to 24 million input pixels, oriented, reduced to 2048 pixels, and rebuilt as WebP without original metadata. Clips are checked and converted to H.264/AAC MP4, with a 1280-pixel bound and metadata removed. Automatic closed captions are not implemented; include spoken context in the caption. The [Pillow image decoder](https://pillow.readthedocs.io/en/stable/reference/Image.html) and [imageio-ffmpeg bundled executable](https://github.com/imageio/imageio-ffmpeg) are installed by `requirements.txt`.

Media is outside the public static directory. Filenames are random and every asset request checks its parent post's published status, including byte-range video requests. Hiding or removing a post blocks subsequent asset requests. Already downloaded copies cannot be recalled. Failed multi-file uploads clean up partial outputs. Posts are limited to eight uploads per ten minutes per account, with a 200 MB account quota; video processing has two slots per process and bounded execution time.

Author removal is a soft withdrawal. Hidden/removed files remain in server storage and count against quota; automated retention cleanup, account export/deletion, appeals, and object-storage lifecycle policies remain future work. Video conversion runs synchronously for this local implementation. A production expansion should use an isolated worker, job status, shared rate limits, storage quotas, and a defined retention policy.

## Catalog and ingestion

`ACTIVE_TERM` identifies the active term. Catalog files are found in the root first, then `scraper/`, matching deployed webhook updates and the existing scraping workflow. The checked-in Spring 2027 data is in `scraper/2027SPdata.txt`. Undergraduate course numbers below 500 are included; comprehensive exams and graduate courses are excluded.

The catalog repository validates rows and invalidates its cache on file changes. Capture time is unavailable for the bundled data; local file modification time is not presented as scrape freshness. The webhook requires `X-Webhook-Token`, validates term/content before replacement, updates the active term atomically, and observes the new revision for seat transitions. Signed-in watch/notification reads also observe changed local files. Observation timestamps say when FCS noticed a revision, not when the university captured it.

The scraping workflow is preserved. This work does not fetch new institutional data or change registration records. Source capture metadata, ingestion completeness monitoring, a durable notification worker, and multi-host PostgreSQL operation remain later steps.

## Structure

```text
app.py                      application factory, configuration, administrative CLI
fcs/catalog.py              validated course-data adapter and cache
fcs/scheduling.py            resumable search with early pruning
fcs/search_sessions.py       signed continuation tied to the original search
fcs/rules.py                 Boolean rule validation and partial evaluation
fcs/database.py              schema and transaction management
fcs/identity.py              hashed passwords, sessions, CSRF, sign-in throttling
fcs/services.py              shared catalog identities and ownership helpers
fcs/library.py               private schedules, snapshot sharing, calendar endpoint
fcs/calendar_export.py       recurring calendar serialization
fcs/community.py             reviews, discussions, groups, reporting, moderation
fcs/availability.py          observations, watches, and notifications
fcs/media.py                 feed, assets, comments, likes, and upload orchestration
fcs/media_processing.py      bounded decoding, metadata removal, video conversion
static/account.js           shared browser session client and account dialog
static/campus.js            campus journeys and dialogs
static/media-feed.js        media composer and feed interactions
static/media-draft.js       pure early upload selection validation
static/planner.js           planner state, rendering, persistence integration
static/rule-builder.js      nested expression editor
static/shared.js            read-only shared schedule view
views.py                    original-page compatibility and ingestion webhook
```

## Verification

```sh
.venv/bin/python -m unittest discover -s tests -v
node --test tests/*.test.mjs
node --check static/planner.js
node --check static/campus.js
node --check static/account.js
node --check static/shared.js
node --check static/media-feed.js
```

See [the platform plan](docs/PLATFORM_PLAN.md), [delivery roadmap](docs/ROADMAP.md), [architecture decisions](docs/ARCHITECTURE.md), [Boolean rules](docs/RULES.md), and [verification record](docs/VERIFICATION.md). GitHub Actions runs the backend and JavaScript checks; local success does not imply a remote CI run.
