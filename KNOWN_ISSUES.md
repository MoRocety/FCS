# FCS v1: Known Issues

Notes on the live site (`MoRocety/FCS` `main`, formancoursescheduler.pythonanywhere.com).
These are recorded, not scheduled. v1 is not being patched for them.

## Back-to-back classes are treated as a clash

**Status:** confirmed on the live site, 2026-11-02. Not fixed, on purpose: no user has ever reported it.

**Cause:** `combcheck.py` `clash_check()` uses inclusive comparisons (`start1 <= start2 <= end1`, and so on),
so a class that ends at 1:00 PM "overlaps" one that starts at 1:00 PM on the same day.

**Reproduce (2027 Spring):**
1. Shortlist UNIV 100 A (Mon–Fri 10:00 AM – 1:00 PM) and ISLM 100A A (Tue 1:00 – 1:50 PM).
2. Set the credit range to 0–22, mark both as must-have, and click Generate.
3. The page alerts "No combination could be generated…". `/submit` returns `{"schedules": [], "missing_courses": []}`.

The control results from `/submit`:

| Request | Schedules |
|---|---|
| Either section alone | 1 |
| Both, no must-have | 2 (each alone, never together) |
| Both as must-have | 0 |

**Scale:** 258 valid section pairs in the 2027 Spring data are rejected this way, mostly UNIV 100
against ISLM, PSYC and HPED sections. Most touching pairs involve labs (for example 14:00–16:00 followed by a 16:00 class).

**Fix if it's ever wanted:** treat two meetings as clashing only when `start1 < end2 and start2 < end1`.

**History:**
- `New_Course_Scheduler.py` (May 2023) used a strict comparison and allowed back-to-back classes.
- v1's first commit (Jul 2023) brought back the inclusive check, and every version through V2-Alpha kept it.
- The October 2026 build fixes it (`fcs/scheduling.py`, `test_back_to_back_is_allowed`).

## Intended behaviour (not bugs)

- **A section whose lecture overlaps its own lab is never scheduled.** Examples in 2027 Spring: CHEM 100 F,
  COMP 206 C, ENVR 416 A. Picking one returns no schedules with an empty `missing_courses`.
- **Courses numbered 500 and above are excluded** from the catalog (116 graduate sections in 2027 Spring).

## Other observations (not reproduced on the live site)

- Generation combines sections rather than picking one section per course. In local runs, 5 courses with
  4 sections each produced about 104,000 candidates (1.6 s). A 6-course shortlist with larger courses didn't
  finish in 5 minutes. Big shortlists could time out on PythonAnywhere.
- The webhook falls back to `change_this_in_production` if `WEBHOOK_SECRET` is unset in the environment,
  and `term_code` is used in file paths without validation. This only matters if production lacks the env var.
- Credits go through `int(float())`, so fractional credits would be truncated. Current data has none.
