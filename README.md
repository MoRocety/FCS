# FCS

A course planner and student campus app for FCCU. Plan a week anonymously, or create an account to keep drafts, share schedules, watch seats, and participate in course conversations.

## Run locally

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --port 5050
```

Open [the planner](http://127.0.0.1:5050) or [Campus](http://127.0.0.1:5050/campus). The app exposes `app:app` for WSGI and `create_app()` for isolated tests. Python 3.11 or later is supported by the CI configuration.

## Implemented journeys

- **Plan a semester:** search sections, see lectures/labs and weekend/evening meetings, shortlist alternatives, inspect conflicts, and generate bounded schedule options using nested Boolean course rules.
- **Keep possibilities:** per-term device drafts plus private named schedules in an account. Open, update, rename, copy, or delete saved drafts. Optimistic versions prevent silently overwriting another save.
- **Share a week:** deliberately create a revocable, read-only snapshot link. It contains the schedule name and selected course metadata; private shortlist, rules, credit range, and account identity are excluded. Later edits do not alter the snapshot.
- **Take it elsewhere:** versioned JSON import/export, printing, and weekly ICS calendar export using explicit semester dates and Asia/Karachi time.
- **Understand courses and teachers:** searchable profiles with overall/difficulty ratings, sample counts, and term-labelled student reviews. One review per subject per term per account; republishing edits it.
- **Talk and study together:** course discussions, comments, study-group posts, opt-in membership, author removal, and content reporting.
- **Watch availability:** account seat watches and in-app alerts when a watched section changes from full to open in an observed catalog snapshot. Repeat observations do not duplicate alerts; a new reopening can notify again.
- **Moderate:** an authorized report queue with hide/dismiss decisions and an audit trail. Hiding a review prevents its author from republishing it through an edit/delete cycle.

The local instance starts without seed accounts or fabricated community content. Account registration does not verify university identity or enrollment. Seat counts remain snapshots and do not reserve seats. Email, push, institutional sign-in, and enrollment verification are not connected.

## Persistence and configuration

SQLite lives in `instance/fcs.sqlite3`, with schema version 2. Version 1 heads are upgraded additively at startup. Local state and the session secret are ignored by Git. A persistent random session secret is created in `instance/.session-secret` unless `SECRET_KEY` is configured. Database and secret files use restricted filesystem permissions.

| Environment variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Stable session-signing secret for the deployment |
| `FCS_DATABASE` | SQLite path; defaults to the application instance directory |
| `FCS_COOKIE_NAME` | Cookie name, useful for isolated local test instances |
| `FCS_SECURE_COOKIES=1` | Secure session cookies on an HTTPS deployment |
| `WEBHOOK_SECRET` | Required authentication for course-data ingestion |
| `PORT` | Direct `python app.py` port; Flask CLI uses `--port` |

Promote an existing account for local moderation:

```sh
flask --app app promote-user existing_username
```

There is no public role-change endpoint. This command is for a trusted operator with access to the application filesystem. Back up the SQLite database and session secret before moving hosts. Run behind a production WSGI server and HTTPS when deploying; no deployment or remote publication is performed by this iteration.

## Catalog and ingestion

`ACTIVE_TERM` identifies the active term. Catalog files are found in the root first, then `scraper/`, matching deployed webhook updates and the existing scraping workflow. The checked-in Spring 2027 data is in `scraper/2027SPdata.txt`. Undergraduate course numbers below 500 are included; comprehensive exams and graduate courses are excluded.

The catalog repository validates rows and invalidates its cache on file changes. Capture time is unavailable for the bundled data; local file modification time is not presented as scrape freshness. The webhook requires `X-Webhook-Token`, validates term/content before replacement, updates the active term atomically, and observes the new revision for seat transitions. Signed-in watch/notification reads also observe changed local files. Observation timestamps say when FCS noticed a revision, not when the university captured it.

The scraping workflow is preserved. This work does not fetch new institutional data or change registration records. Source capture metadata, ingestion completeness monitoring, a durable notification worker, and multi-host PostgreSQL operation remain later steps.

## Structure

```text
app.py                      application factory, configuration, administrative CLI
fcs/catalog.py              validated course-data adapter and cache
fcs/scheduling.py            bounded schedule search
fcs/rules.py                 Boolean rule validation and partial evaluation
fcs/database.py              schema and transaction management
fcs/identity.py              hashed passwords, sessions, CSRF, sign-in throttling
fcs/services.py              shared catalog identities and ownership helpers
fcs/library.py               private schedules, snapshot sharing, calendar endpoint
fcs/calendar_export.py       recurring calendar serialization
fcs/community.py             reviews, discussions, groups, reporting, moderation
fcs/availability.py          observations, watches, and notifications
static/account.js           shared browser session client and account dialog
static/campus.js            campus journeys and dialogs
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
```

See [the platform plan](docs/PLATFORM_PLAN.md), [delivery roadmap](docs/ROADMAP.md), [architecture decisions](docs/ARCHITECTURE.md), [Boolean rules](docs/RULES.md), and [verification record](docs/VERIFICATION.md). GitHub Actions runs the backend and JavaScript checks; local success does not imply a remote CI run.
