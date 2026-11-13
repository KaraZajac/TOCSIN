import unittest

from tocsin.pipeline.validate import regime_checks

STATES = range(1, 21)  # 20 main-system states


def cy_rows(last=2025):
    return [{"gwno": str(g), "year": str(y), "main_system": "1"} for y in range(2020, last + 1) for g in STATES]


def regime_rows(last=2025, states=STATES):
    return [{"gwno": str(g), "year": str(y), "regime": "2"} for y in range(2020, last + 1) for g in states]


def failed(checks):
    return [label for ok, label in checks if not ok]


class TestRegimeChecks(unittest.TestCase):
    def test_current_shape_passes(self):
        self.assertEqual(failed(regime_checks(regime_rows(), cy_rows())), [])

    def test_empty_table_fails(self):
        # what OWID's switch to text labels did to regime.csv in 2026-11
        self.assertEqual(failed(regime_checks([], cy_rows())), ["regime table has rows"])

    def test_one_year_behind_passes_two_fail(self):
        self.assertEqual(failed(regime_checks(regime_rows(last=2024), cy_rows())), [])
        self.assertEqual(
            failed(regime_checks(regime_rows(last=2023), cy_rows())),
            ["regime data reaches 2023 (conflict data 2025)"],
        )

    def test_coverage_below_ninety_percent_fails(self):
        self.assertEqual(failed(regime_checks(regime_rows(states=range(1, 19)), cy_rows())), [])  # 90%
        self.assertEqual(
            failed(regime_checks(regime_rows(states=range(1, 18)), cy_rows())),  # 85%
            ["regime covers 2025 main-system states (85%)"],
        )

    def test_coverage_is_judged_on_the_latest_year_both_tables_have(self):
        # a partial year past the conflict data must not count as the latest
        partial = regime_rows() + [{"gwno": "1", "year": "2026", "regime": "2"}]
        self.assertEqual(failed(regime_checks(partial, cy_rows())), [])


if __name__ == "__main__":
    unittest.main()
