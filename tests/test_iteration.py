import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import app as app_module
from demo_data import DEMO_DOSSIER
from models import Claim, Source
from service import locate_claim


class EvidenceModelTests(unittest.TestCase):
    def test_claim_is_located_in_original_scene(self):
        scene = "INT. ROOM — NIGHT\nAnna sends a text message from her GSM phone."
        claim = Claim(
            id="C1",
            text="Anna sends an SMS from a GSM phone.",
            script_quote="sends a text message from her GSM phone",
            category="TECHNOLOGY",
            question="Was SMS available?",
            search_queries=["first SMS date"],
        )
        located = locate_claim(scene, claim)
        self.assertEqual(scene[located.start_offset:located.end_offset], "sends a text message from her GSM phone")

    def test_source_has_auditable_stance(self):
        source = Source(id="S1", title="Archive", url="https://example.com", excerpt="Evidence", stance="REFUTES")
        self.assertEqual(source.stance, "REFUTES")


class ProtectionTests(unittest.TestCase):
    def setUp(self):
        app_module.analysis_cache.clear()
        app_module.ip_attempts.clear()
        app_module.daily_attempts.clear()
        self.client = TestClient(app_module.app)
        self.keys = {"GEMINI_API_KEY": "test", "PARALLEL_API_KEY": "test", "RATE_LIMIT_PER_HOUR": "2"}

    def test_identical_scene_uses_cache_without_second_analysis(self):
        scene = "A screenplay scene with enough specific historical detail to pass request validation. " * 2
        with patch.dict(os.environ, self.keys, clear=True), patch("app.analyze_scene", return_value=DEMO_DOSSIER) as analyze:
            first = self.client.post("/api/analyze", json={"scene": scene})
            second = self.client.post("/api/analyze", json={"scene": scene})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.headers["X-Dramaturg-Cache"], "HIT")
        self.assertEqual(analyze.call_count, 1)

    def test_rate_limit_blocks_distinct_excess_requests(self):
        with patch.dict(os.environ, self.keys, clear=True), patch("app.analyze_scene", return_value=DEMO_DOSSIER):
            responses = [
                self.client.post("/api/analyze", json={"scene": f"Scene number {index} contains enough detailed historical material for analysis. " * 2})
                for index in range(3)
            ]
        self.assertEqual([response.status_code for response in responses], [200, 200, 429])

    def test_concurrent_live_analysis_is_rejected(self):
        app_module.analysis_lock.acquire()
        try:
            with patch.dict(os.environ, self.keys, clear=True):
                response = self.client.post("/api/analyze", json={"scene": "A distinct historical screenplay scene with enough concrete detail for verification. " * 2})
        finally:
            app_module.analysis_lock.release()
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["Retry-After"], "60")


if __name__ == "__main__":
    unittest.main()
