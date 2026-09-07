import unittest
from fastapi.testclient import TestClient
from main import app
from factmesh.storage import db

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_stats_and_presets(self):
        # Load Delhivery preset
        res = self.client.post("/api/dataset-presets/delhivery")
        self.assertEqual(res.status_code, 200)

        # Query stats
        res_stats = self.client.get("/api/stats")
        self.assertEqual(res_stats.status_code, 200)
        data = res_stats.json()
        self.assertGreater(data["total_facts"], 0)
        self.assertGreater(data["corroborated_count"], 0)
        self.assertGreater(data["reconciled_count"], 0)

        # Query relationships
        res_rels = self.client.get("/api/relationships")
        self.assertEqual(res_rels.status_code, 200)
        rels = res_rels.json()
        self.assertGreater(len(rels), 0)

        # Query failures
        res_fails = self.client.get("/api/failures")
        self.assertEqual(res_fails.status_code, 200)
        fails = res_fails.json()
        self.assertGreater(len(fails), 0)

        # Check root UI serves HTML
        res_ui = self.client.get("/")
        self.assertEqual(res_ui.status_code, 200)
        self.assertIn("FactMesh", res_ui.text)

if __name__ == "__main__":
    unittest.main()
