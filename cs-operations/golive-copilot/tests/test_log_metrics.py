"""Tests for src/log_metrics.py, using the fictional Kestrel Row log."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import log_metrics  # noqa: E402

LOG = ROOT / "samples" / "kestrel-row" / "logs.csv"
QUALITY_OR_OUTCOMES_FLAGS = {"KR-002", "KR-006", "KR-007", "KR-008", "KR-009", "KR-012"}


class KestrelRowCounts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.schema = log_metrics.read_log(LOG)
        cls.m = log_metrics.calculate(cls.rows)

    def test_conversations(self):
        self.assertEqual(self.m["conversations"], 12)

    def test_out_of_hours(self):
        self.assertEqual(self.m["out_of_hours"], 10)

    def test_abandoned(self):
        self.assertEqual(self.m["abandoned"], 2)

    def test_escalations_over_30_minutes(self):
        self.assertEqual(self.m["late_escalations"], ["KR-010"])

    def test_staff_overrides(self):
        self.assertEqual(len(self.m["overrides"]), 2)
        self.assertEqual(self.m["overrides_by_site"], {"Riverside": 2})

    def test_outcome_reached_is_unchanged(self):
        self.assertEqual(self.m["outcome_reached"], 8)

    def test_branch_column_read_as_site(self):
        self.assertEqual(self.schema["missing"], [])
        self.assertIn("customer_ref", self.schema["optional_missing"])

    def test_threshold_is_configurable(self):
        m = log_metrics.calculate(self.rows, threshold=5)
        self.assertEqual(m["late_escalations"], ["KR-003", "KR-010"])


class KestrelRowRates(unittest.TestCase):
    def setUp(self):
        rows, _ = log_metrics.read_log(LOG)
        self.m = log_metrics.calculate(rows, flagged=QUALITY_OR_OUTCOMES_FLAGS)

    def test_resolution_rate(self):
        self.assertEqual(self.m["resolutions"], ["KR-001", "KR-011"])

    def test_correct_handling_rate(self):
        self.assertEqual(self.m["correctly_handled"], 6)
        self.assertEqual(self.m["correct_escalations"], ["KR-003", "KR-010"])
        self.assertEqual(self.m["redone_but_right"], ["KR-004", "KR-005"])

    def test_rates_need_flags(self):
        rows, _ = log_metrics.read_log(LOG)
        self.assertNotIn("resolutions", log_metrics.calculate(rows))


class Report(unittest.TestCase):
    def test_report_written_with_skill_headings(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.md"
            log_metrics.main([str(LOG), "--out", str(out)])
            text = out.read_text(encoding="utf-8")
        for heading in ["## 1. Headline", "## 2. By bucket", "## 4. Outcomes for the value ledger", "## 9. Gate check"]:
            self.assertIn(heading, text)
        self.assertIn(log_metrics.JUDGEMENT, text)
        self.assertIn("schema is an assumption", text)

    def test_default_report_name(self):
        self.assertEqual(log_metrics.report_name(LOG), "log-metrics-kestrel-row.md")

    def test_missing_column_keeps_going(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "short.csv"
            log.write_text("conversation_id,outcome,extra_col\nX-1,abandoned,1\nX-2,resolved,2\n", encoding="utf-8")
            rows, schema = log_metrics.read_log(log)
            self.assertIn("out_of_hours", schema["missing"])
            self.assertEqual(schema["extra"], ["extra_col"])
            m = log_metrics.main([str(log), "--out", str(Path(tmp) / "r.md")])
        self.assertEqual(m["conversations"], 2)
        self.assertEqual(m["abandoned"], 1)


if __name__ == "__main__":
    unittest.main()
