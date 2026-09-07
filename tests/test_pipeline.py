import unittest
from pathlib import Path
from factmesh.pipeline import pipeline
from factmesh.storage import db

class TestPipeline(unittest.TestCase):
    def setUp(self):
        db.clear_all()

    def test_starter_delhivery_load(self):
        pipeline.load_starter_dataset("delhivery")
        facts = db.get_facts()
        self.assertGreater(len(facts), 5)

        rels = db.get_relationships()
        self.assertGreater(len(rels), 0)

        # Check for corroboration
        corrob = [r for r in rels if r.relationship.value == "CORROBORATED"]
        self.assertGreater(len(corrob), 0)

        # Check for reconciliation
        recon = [r for r in rels if r.relationship.value == "CONTEXTUALLY_RECONCILED"]
        self.assertGreater(len(recon), 0)

        # Check for failures
        fails = db.get_failures()
        self.assertGreater(len(fails), 0)

    def test_starter_macro_load(self):
        pipeline.load_starter_dataset("india-macroeconomy")
        facts = db.get_facts()
        self.assertGreater(len(facts), 4)

        rels = db.get_relationships()
        self.assertGreater(len(rels), 0)

if __name__ == "__main__":
    unittest.main()
