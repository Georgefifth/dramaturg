import os
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import app as app_module
from demo_data import DEMO_DOSSIER
from models import Claim, ResearchTrace, Verdict
from service import CoverageResult, analyze_scene


class PipelineProgressTests(unittest.TestCase):
    def test_pipeline_emits_real_stage_progress(self):
        claim = Claim(id="C1", text="A historical claim", script_quote="historical claim", category="HISTORY", question="Is it accurate?", search_queries=["historical claim evidence"])
        verdict = Verdict(claim=claim, status="UNVERIFIED", confidence=0, finding="Insufficient evidence", sources=[])
        trace = ResearchTrace(claim_id="C1", status="SUFFICIENT", rationale="Enough", initial_source_count=0)
        events = []
        with patch("service.extract_claims", return_value=[claim]), patch("service.search_claim", return_value=[]), patch("service.audit_coverage", return_value=[CoverageResult(claim_id="C1", status="SUFFICIENT", rationale="Enough")]), patch("service.expand_evidence", return_value=({"C1": []}, [trace])), patch("service.verify_claims", return_value=[verdict]):
            analyze_scene("A historical claim appears in this sufficiently long screenplay scene for testing.", progress=lambda *event: events.append(event))
        phases = [event[0] for event in events]
        self.assertEqual(phases[0], "extracting")
        self.assertEqual(phases[-1], "complete")
        self.assertEqual(phases.count("initial_search"), 2)
        self.assertLess(phases.index("coverage_audit"), phases.index("verification"))


class JobApiTests(unittest.TestCase):
    def setUp(self):
        app_module.analysis_cache.clear()
        app_module.ip_attempts.clear()
        app_module.daily_attempts.clear()
        app_module.job_store.clear()
        self.client = TestClient(app_module.app)
        self.keys = {"GEMINI_API_KEY": "test", "PARALLEL_API_KEY": "test"}

    def test_job_reports_progress_and_result(self):
        scene = "A detailed historical screenplay scene that is long enough for asynchronous verification. " * 2

        def complete(_scene, progress):
            progress("coverage_audit", "Auditing evidence coverage", 2, 4)
            return DEMO_DOSSIER

        with patch.dict(os.environ, self.keys, clear=True), patch("app.analyze_scene", side_effect=complete):
            created = self.client.post("/api/jobs", json={"scene": scene})
            self.assertEqual(created.status_code, 202)
            job_id = created.json()["jobId"]
            for _ in range(20):
                payload = self.client.get(f"/api/jobs/{job_id}").json()
                if payload["status"] == "complete":
                    break
                time.sleep(0.01)
        self.assertEqual(payload["status"], "complete")
        self.assertEqual(payload["dossier"]["summary"]["total"], 5)

    def test_cached_job_completes_without_background_analysis(self):
        scene = "A detailed cached screenplay scene that is long enough for asynchronous verification. " * 2
        app_module._store(scene, DEMO_DOSSIER)
        with patch.dict(os.environ, self.keys, clear=True), patch("app.analyze_scene") as analyze:
            response = self.client.post("/api/jobs", json={"scene": scene})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "complete")
        self.assertEqual(response.json()["cache"], "HIT")
        analyze.assert_not_called()


if __name__ == "__main__":
    unittest.main()
