import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tocsin.pipeline import download

DATA = b"ccode\tabbrev\tyear\tcoup1\n2\tUSA\t1950\t0\n"
CAPTURE = f"https://web.archive.org/web/20270101000000id_/{download.PT_URL}"
CDX_OK = json.dumps([["urlkey", "timestamp", "original"], ["edu,uky)/x", "20270101000000", download.PT_URL]]).encode()


def fake_get(answers):
    """_get stand-in: answers maps URL -> bytes, or an exception to raise."""
    def get(url, timeout=300, context=None):
        answer = answers.get(url, SystemExit(f"download failed: {url} (HTTP 404 Not Found; attempt 1/4)"))
        if isinstance(answer, BaseException):
            raise answer
        return answer
    return get


class TestPowellThyneSources(unittest.TestCase):
    def pull(self, answers):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()) as out, \
                mock.patch.object(download, "ROOT", Path(tmp)), \
                mock.patch.object(download, "_get", fake_get(answers)), \
                mock.patch.object(download, "PT_PINNED_SHA256", hashlib.sha256(DATA).hexdigest()):
            dest = Path(tmp) / "pt-coups.tsv"
            try:
                download.pull_powell_thyne(dest)
            finally:
                written = dest.read_bytes() if dest.exists() else None
        return written, out.getvalue()

    def test_uky_used_when_it_answers(self):
        written, log = self.pull({download.PT_URL: DATA})
        self.assertEqual(written, DATA)
        self.assertIn("from uky.edu", log)

    def test_newest_capture_when_uky_refuses(self):
        written, log = self.pull({
            download.PT_URL: SystemExit("download failed: … (HTTP 403 Forbidden; attempt 1/4)"),
            download.PT_CDX: CDX_OK,
            CAPTURE: DATA,
        })
        self.assertEqual(written, DATA)
        self.assertIn("HTTP 403 Forbidden", log)
        self.assertIn("from Wayback capture 20270101000000", log)

    def test_pinned_capture_when_cdx_answers_html(self):
        # an HTML page where the CDX JSON should be once surfaced as a bare
        # JSONDecodeError traceback; now it is one more failed source
        written, log = self.pull({
            download.PT_CDX: b"<!doctype html><title>blocked</title>",
            download.PT_PINNED: DATA,
        })
        self.assertEqual(written, DATA)
        self.assertIn("lists no capture", log)
        self.assertIn("from pinned Wayback capture 20260311172726", log)

    def test_pinned_capture_must_match_its_sha256(self):
        with self.assertRaises(SystemExit) as cm:
            self.pull({download.PT_PINNED: DATA + b"tampered"})
        self.assertIn("does not match its pinned sha256", str(cm.exception))

    def test_not_the_data_file_is_skipped_and_all_failing_is_one_clear_error(self):
        with self.assertRaises(SystemExit) as cm:
            # the CDX answers an empty body when it has no capture
            self.pull({download.PT_URL: b"<html>Forbidden</html>", download.PT_CDX: b""})
        msg = str(cm.exception)
        self.assertIn("every source failed", msg)
        self.assertIn("uky.edu is not the data file", msg)
        self.assertIn("lists no capture", msg)
        self.assertIn(download.PT_PINNED, msg)


if __name__ == "__main__":
    unittest.main()
