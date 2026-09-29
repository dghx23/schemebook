from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import schemebook
import schemebook_sync

class SchemeBookSyncTests(unittest.TestCase):
    def test_glossary_is_expanded(self):
        self.assertEqual(len(schemebook.JARGON), 38)
        self.assertTrue(any(row["slug"] == "cms-complaint" for row in schemebook.JARGON))

    def test_snapshot_carries_every_contract(self):
        payload = schemebook_sync.build_snapshot(schemebook.JARGON)
        self.assertEqual(payload["product"], "SchemeBook")
        self.assertEqual(len(payload["glossary"]), 38)
        self.assertEqual(len(payload["pipeline"]), 4)
        self.assertIn("schemes", payload["stats"])

    def test_sync_is_versioned_and_logged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(schemebook_sync, "DATA_DIR", root), \
                 patch.object(schemebook_sync, "SNAPSHOT_PATH", root / "snapshot.json"), \
                 patch.object(schemebook_sync, "STATE_PATH", root / "state.json"), \
                 patch.object(schemebook_sync.ingest_log, "LOG_PATH", root / "log.json"):
                state = schemebook_sync.sync(schemebook.JARGON, triggered_by="test")
                self.assertEqual(len(state["content_hash"]), 64)
                self.assertEqual(state["record_counts"]["glossary"], 38)
                self.assertTrue((root / "snapshot.json").is_file())
                events = schemebook_sync.ingest_log.recent_events(product="SchemeBook")
                self.assertEqual(len(events), 4)
                self.assertEqual(events[0]["flow_to"], "SchemeBook actual")

if __name__ == "__main__":
    unittest.main()
