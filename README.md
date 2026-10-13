# FCS

A course planner for FCCU. Browse undergraduate sections, build a weekly timetable, compare schedules, and keep a draft on your device.

## Run locally

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --port 5050
```

Open http://127.0.0.1:5050. Python 3.11 or later is recommended. The app also exposes `app:app` for existing WSGI deployments, plus `create_app()` for tests and configuration.

## What works

- Search by course title, code, section, or instructor; filter by department and open seats.
- Add sections to a week or shortlist alternative sections. Adding another section of the same course replaces it in your week while preserving alternatives in your shortlist.
- Display all lecture and lab meetings, including weekends and evening times. Overlapping events appear side by side and are marked as conflicts.
- Show credits, unique course count, conflicts, and unannounced meeting times.
- Build nested AND/OR/NOT course rules and generate up to 50 schedule options from at most 60 shortlisted sections. A bounded search prevents unmanageable enumeration; results disclose when a limit is reached.
- Save drafts locally per term. Export/import versioned JSON; print either the weekly or list view.

Local storage is specific to this browser and device. Export a draft for backup. An import replaces the current draft; sections no longer in the catalog are reported and skipped. The catalog is a snapshot, not registration or a seat reservation. File modification time is not presented as the time course availability was captured.

## Course data

`ACTIVE_TERM` identifies the term. The repository searches for `<term>data.txt` in the root first, then `scraper/`, matching both deployed webhook data and the scheduled scraping workflow. The checked-in Spring 2027 data lives in `scraper/2027SPdata.txt`. Undergraduate course numbers below 500 are included, matching the original scope. Comprehensive exams and graduate courses are excluded.

Changes to the active term or the data file automatically invalidate the process-local catalog cache. Parsing validates the data before it is served. If the catalog is missing, the page still opens and reports that data is unavailable.

The existing GitHub workflow scrapes on a schedule and sends data to `/webhook/update-courses`. Configure `WEBHOOK_SECRET` and `WEBHOOK_URL` in the deployment and repository secrets. No default webhook secret is accepted. Term codes and rows are validated before an atomic data-file replacement. Request bodies are limited to 2 MB.

The scraper is preserved; this work does not fetch new institutional data or change registration records. Capture-time metadata, ingestion history, and stale-data monitoring are planned next.

## Structure

```text
app.py                   application factory and WSGI entry point
fcs/catalog.py           validated text adapter and catalog repository
fcs/scheduling.py        conflict rules and bounded backtracking
fcs/api.py               /api/v1 catalog and generation endpoints
views.py                 pages, webhook, and legacy HTTP adapters
static/planner.js        browser state, rendering, draft import/export
static/planner.css       responsive planner and print styles
static/rule-builder.js   nested Boolean block editor and rule validation
fcs/rules.py             rule validation and partial evaluation
templates/planner.html   accessible page structure
tests/                   scheduling, catalog, and API regression tests
docs/                    product and architecture plans
scraper/                 existing course ingestion pipeline
```

The original interface remains at `/old`, and its filtering/generation endpoints remain available. `/submit` now uses the bounded scheduling service and includes `limited` in its response. Historical `trying.html`, `dataread.py`, and `combcheck.py` remain for reference and compatibility; the new planner does not depend on them.

## Verification

```sh
.venv/bin/python -m unittest discover -s tests -v
node --check static/planner.js
node --test tests/rules.test.mjs
```

Read [the implementation roadmap](docs/ROADMAP.md) and [the architecture decisions](docs/ARCHITECTURE.md) for the path to shared schedules, reviews, discussions, and seat alerts. Those platform features are planned, not implemented in this iteration.

See [nested schedule rules](docs/RULES.md) for examples, JSON format, and migration behavior.
