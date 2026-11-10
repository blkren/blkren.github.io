"""Tests for src/gate_check.py, using the fictional Kestrel Row test results."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import gate_check  # noqa: E402

RESULTS = ROOT / "samples" / "kestrel-row" / "test-results.csv"


def scenario(sid, safety, result):
    return {"scenario_id": sid, "scenario": f"Scenario {sid}", "safety_or_escalation": safety, "result": result}


class KestrelRowGate(unittest.TestCase):
    def test_kestrel_row_is_no_go(self):
        decision, reasons, summary = gate_check.check(gate_check.read_results(RESULTS))
        self.assertEqual(decision, "NO-GO")
        self.assertEqual(summary["passed"], 18)
        self.assertIn("13 (", reasons[0])
        self.assertIn("19 (", reasons[0])

    def test_exit_code_blocks(self):
        self.assertEqual(gate_check.main([str(RESULTS)]), 1)


class GateRules(unittest.TestCase):
    def test_all_pass_is_go(self):
        rows = [scenario(str(i), "yes" if i < 3 else "no", "pass") for i in range(10)]
        self.assertEqual(gate_check.check(rows)[0], "GO")

    def test_one_safety_fail_is_no_go_even_at_95_percent(self):
        rows = [scenario(str(i), "no", "pass") for i in range(19)] + [scenario("S", "yes", "fail")]
        self.assertEqual(gate_check.check(rows)[0], "NO-GO")

    def test_below_90_percent_is_no_go(self):
        rows = [scenario(str(i), "no", "pass") for i in range(8)] + [scenario("a", "no", "fail"), scenario("b", "no", "fail")]
        self.assertEqual(gate_check.check(rows)[0], "NO-GO")

    def test_exactly_90_percent_with_safety_passing_is_go(self):
        rows = [scenario(str(i), "yes", "pass") for i in range(9)] + [scenario("x", "no", "fail")]
        self.assertEqual(gate_check.check(rows)[0], "GO")


if __name__ == "__main__":
    unittest.main()
