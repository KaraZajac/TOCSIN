import contextlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from tocsin.pipeline import worldbank
from tocsin.pipeline.worldbank import bulk_rows

CODE = "SP.DYN.IMRT.IN"

# shaped like a real bulk download's API_<code>_DS2_en_csv_v2_<n>.csv: a BOM,
# metadata lines, then one column per year and a trailing empty column; the
# 1959 and 2026 columns sit outside the JSON query's 1960:2025 window
CSV = (
    "\ufeff"
    '"Data Source","World Development Indicators",\n'
    "\n"
    '"Last Updated Date","2026-11-11",\n'
    "\n"
    '"Country Name","Country Code","Indicator Name","Indicator Code","1959","1960","2024","2025","2026",\n'
    f'"Aruba","ABW","Mortality rate, infant","{CODE}","9","18","1.5","","7",\n'
    f'"High income","HIC","Mortality rate, infant","{CODE}","","4.2","3.9","3.8","",\n'
    f'"Zimbabwe","ZWE","Mortality rate, infant","{CODE}","","","35.25","34","",\n'
)


def bulk_zip(text: str = CSV, code: str = CODE) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(f"Metadata_Indicator_API_{code}_DS2_en_csv_v2_1.csv", '"INDICATOR_CODE",\n')
        z.writestr(f"API_{code}_DS2_en_csv_v2_1.csv", text.encode("utf-8"))
        z.writestr(f"Metadata_Country_API_{code}_DS2_en_csv_v2_1.csv", '"Country Code",\n')
    return buf.getvalue()


class TestBulkRows(unittest.TestCase):
    def test_keeps_what_the_json_path_keeps(self):
        # in-window, non-empty cells only, newest year first per country (the
        # API's order); HIC is one of the aggregates the JSON API returns
        # with an empty countryiso3code, so the JSON path never kept it
        self.assertEqual(
            bulk_rows(bulk_zip(), CODE),
            [
                {"iso3": "ABW", "year": 2024, "value": 1.5},
                {"iso3": "ABW", "year": 1960, "value": 18},
                {"iso3": "ZWE", "year": 2025, "value": 34},
                {"iso3": "ZWE", "year": 2024, "value": 35.25},
            ],
        )

    def test_integral_cells_stay_ints_like_the_api_json(self):
        # the API's JSON has 18, not 18.0, and covariates.csv writes what it
        # gets: a float here would turn "18" into "18.0" in the committed table
        rows = bulk_rows(bulk_zip(), CODE)
        self.assertEqual([type(r["value"]) for r in rows], [float, int, int, float])
        self.assertEqual(json.dumps(rows[1]["value"]), "18")

    def test_another_indicators_file_is_rejected(self):
        with self.assertRaises(ValueError):  # no API_NY.GDP.PCAP.KD_*.csv member
            bulk_rows(bulk_zip(), "NY.GDP.PCAP.KD")
        with self.assertRaises(ValueError):  # right member name, wrong rows
            bulk_rows(bulk_zip(CSV.replace(CODE, "SP.POP.GROW"), CODE), CODE)

    def test_missing_header_or_bad_cell_is_rejected(self):
        with self.assertRaises(ValueError):
            bulk_rows(bulk_zip(CSV.replace('"Country Name"', '"Economy"')), CODE)
        with self.assertRaises(ValueError):
            bulk_rows(bulk_zip(CSV.replace('"35.25"', '"n/a"')), CODE)


class TestPullFallback(unittest.TestCase):
    def pull(self, bulk):
        api_rows = [{"iso3": "ZWE", "year": 2025, "value": 34}]
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()) as out, \
                mock.patch.object(worldbank, "ROOT", Path(tmp)), \
                mock.patch.object(worldbank, "DEST", Path(tmp) / "worldbank"), \
                mock.patch.object(worldbank, "INDICATORS", {"infant_mort": (CODE, "")}), \
                mock.patch.object(worldbank, "fetch_indicator_bulk", side_effect=bulk), \
                mock.patch.object(worldbank, "fetch_indicator", return_value=api_rows) as api:
            worldbank.pull()
            written = json.loads((Path(tmp) / "worldbank" / "infant_mort.json").read_text())
        return written, out.getvalue(), api.called

    def test_bulk_used_when_it_parses(self):
        written, log, api_called = self.pull(lambda code: [{"iso3": "ABW", "year": 2024, "value": 1.5}])
        self.assertEqual(written, [{"iso3": "ABW", "year": 2024, "value": 1.5}])
        self.assertIn("(1 obs, bulk CSV)", log)
        self.assertFalse(api_called)

    def test_json_api_used_when_bulk_fails_or_is_empty(self):
        for failure in (SystemExit("download failed: …"), ValueError("no header row"),
                        zipfile.BadZipFile("not a zip"), lambda code: []):
            with self.subTest(failure=failure):
                written, log, api_called = self.pull(failure)
                self.assertTrue(api_called)
                self.assertEqual(written, [{"iso3": "ZWE", "year": 2025, "value": 34}])
                self.assertIn("falling back to the JSON API", log)
                self.assertIn("(1 obs, JSON API)", log)


if __name__ == "__main__":
    unittest.main()
