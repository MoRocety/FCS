import unittest
from unittest.mock import patch
from app import create_app
from fcs.scheduling import generate
from test_scheduler import section


class SearchContinuationTests(unittest.TestCase):
    def setUp(self):
        self.sections = [
            section(
                f"CS:{100+i}:A", start=f"{9+i:02}:00", end=f"{10+i:02}:00", credits=1
            )
            for i in range(7)
        ]
        self.rule = {
            "op": "and",
            "children": [
                {
                    "op": "or",
                    "children": [
                        {"op": "course", "course_key": "CS:100", "present": True},
                        {"op": "course", "course_key": "CS:101", "present": True},
                    ],
                },
                {
                    "op": "not",
                    "children": [
                        {
                            "op": "and",
                            "children": [
                                {
                                    "op": "course",
                                    "course_key": "CS:102",
                                    "present": True,
                                },
                                {
                                    "op": "course",
                                    "course_key": "CS:103",
                                    "present": True,
                                },
                            ],
                        }
                    ],
                },
            ],
        }
        self.app = create_app(
            {"TESTING": True, "SCHEDULE_BATCH_LIMIT": 3, "SCHEDULE_NODE_BUDGET": 9}
        )
        self.client = self.app.test_client()
        self.catalog = {
            "term": "2027SP",
            "revision": "test-revision",
            "sections": self.sections,
        }
        self.payload = {
            "term": "2027SP",
            "catalog_revision": "test-revision",
            "section_ids": [s["id"] for s in self.sections],
            "min_credits": 2,
            "max_credits": 4,
            "rules": self.rule,
        }

    def api(self, payload):
        with patch.object(
            self.app.extensions["catalog"], "load", return_value=self.catalog
        ):
            return self.client.post("/api/v1/schedules/generate", json=payload)

    def test_every_combination_reachable_without_repeats_in_small_batches(self):
        reference = generate(
            self.sections, 2, 4, rules=self.rule, limit=10000, budget=1000000
        )
        results = []
        cursor = None
        for _ in range(1000):
            result = generate(
                self.sections,
                2,
                4,
                rules=self.rule,
                limit=3,
                budget=7,
                continuation=cursor,
            )
            self.assertLessEqual(result["visited"], 7)
            results.extend(result["schedules"])
            cursor = result["continuation"]
            self.assertEqual(result["limited"], bool(cursor))
            if not cursor:
                break
        else:
            self.fail("Continuation did not finish")
        self.assertEqual(reference["schedules"], results)
        self.assertEqual(len(results), len({frozenset(ids) for ids in results}))

    def test_signed_http_pages_finish_exactly_the_exhaustive_valid_set(self):
        results = []
        data = dict(self.payload)
        for _ in range(1000):
            response = self.api(data)
            self.assertEqual(response.status_code, 200, response.json)
            page = response.json
            results.extend(page["schedules"])
            if not page["continuation"]:
                break
            self.assertIsInstance(page["continuation"], str)
            data["continuation"] = page["continuation"]
        else:
            self.fail("API search did not finish")
        expected = generate(
            self.sections, 2, 4, rules=self.rule, limit=10000, budget=1000000
        )["schedules"]
        self.assertEqual(expected, results)

    def test_rejects_tampered_and_input_changed_cursors(self):
        cursor = self.api(self.payload).json["continuation"]
        for altered in ("invalid", cursor[:-5] + "abcde", [], {}, "x" * 65537):
            self.assertEqual(
                self.api({**self.payload, "continuation": altered}).status_code, 400
            )
        for change in (
            {"max_credits": 5},
            {"section_ids": self.payload["section_ids"][:-1]},
            {"rules": {"op": "and", "children": []}},
            {"required_course_keys": ["CS:100"]},
        ):
            self.assertEqual(
                self.api(
                    {**self.payload, **change, "continuation": cursor}
                ).status_code,
                400,
            )
        self.catalog["revision"] = "new-revision"
        self.assertEqual(
            self.api(
                {
                    **self.payload,
                    "catalog_revision": "new-revision",
                    "continuation": cursor,
                }
            ).status_code,
            400,
        )

    def test_work_pause_without_a_match_can_continue(self):
        cursor = None
        results = []
        empty_pauses = 0
        for _ in range(1000):
            page = generate(self.sections, 6, 6, limit=2, budget=1, continuation=cursor)
            results.extend(page["schedules"])
            cursor = page["continuation"]
            if cursor and not page["schedules"]:
                empty_pauses += 1
            if not cursor:
                break
        self.assertGreater(empty_pauses, 0)
        self.assertEqual(len(results), 7)

    def test_final_exact_batch_is_complete(self):
        result = generate([self.sections[0]], 1, 1, limit=1, required={"CS:100"})
        self.assertEqual(len(result["schedules"]), 1)
        self.assertFalse(result["limited"])
        self.assertIsNone(result["continuation"])
