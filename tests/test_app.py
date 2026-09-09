import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        self.assertEqual(self.client.get("/api/health").json(), {"status": "ok"})

    def test_demo_is_explicitly_sample_data(self):
        response = self.client.get("/api/demo")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["mode"], "sample")
        self.assertEqual(payload["summary"]["total"], len(payload["verdicts"]))
        self.assertTrue(all(item["sources"] for item in payload["verdicts"]))

    def test_live_analysis_requires_both_keys(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.post("/api/analyze", json={"scene": "A historically specific screenplay scene. " * 4})
        self.assertEqual(response.status_code, 503)

    def test_short_scene_is_rejected(self):
        response = self.client.post("/api/analyze", json={"scene": "Too short"})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
