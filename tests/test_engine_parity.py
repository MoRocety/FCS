"""Compare complete small searches directly with the original FCS combinator."""

import random
import unittest
from combcheck import credit_check, duplicate_checker, clash_check, crucial
from fcs.scheduling import generate
from fcs.catalog import CatalogRepository
from test_scheduler import section


def original_rows(sections):
    rows = []
    for s in sections:
        meetings = s["meetings"]
        main = meetings[0]
        lab = meetings[1] if len(meetings) > 1 else None
        rows.append(
            [
                s["department"],
                s["number"],
                s["section"],
                s["name"],
                s["credits"],
                repr(main["days"]),
                main["start"],
                main["end"],
                s["instructor"],
                "",
                "",
                repr(lab["days"]) if lab else "None",
                lab["start"] if lab else "None",
                lab["end"] if lab else "None",
                30,
                1,
            ]
        )
    return rows


class OriginalEngineParityTests(unittest.TestCase):
    def compare(self, sections, minimum, maximum, required):
        rows = original_rows(sections)
        reference = {
            frozenset(":".join(s[:3]) for s in combination)
            for combination in credit_check(rows, minimum, maximum)
            if not duplicate_checker(combination)
            and not clash_check(combination)
            and crucial(combination, [key.replace(":", "") for key in required])
        }
        result = generate(
            sections, minimum, maximum, required, limit=10000, budget=1000000
        )
        self.assertFalse(result["limited"])
        self.assertEqual(reference, {frozenset(s) for s in result["schedules"]})

    def test_generated_shortlists_match_original_pipeline(self):
        rng = random.Random(572)
        for trial in range(40):
            shortlist = []
            for i in range(8):
                start = rng.randrange(9, 15)
                lab = (
                    {"days": ["F"], "start": "10:00", "end": "12:00", "room": "Lab"}
                    if rng.random() < 0.3
                    else None
                )
                shortlist.append(
                    section(
                        f'CS:{100+i//2}:{"AB"[i%2]}',
                        f"{start:02}:00",
                        f"{start+1:02}:00",
                        (rng.choice(["M", "T", "F"]),),
                        rng.choice([1, 2, 3]),
                        lab,
                    )
                )
            with self.subTest(trial=trial):
                self.compare(shortlist, 3, 9, {"CS:100"} if trial % 2 else set())

    def test_real_catalog_integer_credit_shortlists(self):
        candidates = [
            s
            for s in CatalogRepository().load()["sections"]
            if s["credits"] > 0 and s["credits"].is_integer() and s["meetings"]
        ]
        rng = random.Random(814)
        for trial in range(8):
            shortlist = rng.sample(candidates, 10)
            with self.subTest(trial=trial):
                self.compare(
                    shortlist,
                    6,
                    15,
                    {shortlist[0]["course_key"]} if trial % 2 else set(),
                )

    def test_lecture_overlapping_own_lab_is_excluded(self):
        lab = {"days": ["M"], "start": "09:30", "end": "11:00", "room": "Lab"}
        self.compare(
            [section("CS:101:A", alternate=lab), section("CS:102:A", days=("T",))],
            3,
            6,
            set(),
        )
