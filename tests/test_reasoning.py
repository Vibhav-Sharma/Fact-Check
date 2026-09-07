import unittest
from factmesh.schemas import Fact, TimePeriod, Scope, Evidence, RelationshipType, ReconcilingDimension
from factmesh.reasoning.reconciler import FactReconciler

class TestReasoningEngine(unittest.TestCase):
    def setUp(self):
        self.reconciler = FactReconciler()

    def test_corroboration(self):
        fact_a = Fact(
            fact_id="fa_1", document_id="doc1", source_document="doc1.pdf", page_number=2,
            subject="Delhivery", predicate="Revenue", raw_value="₹8,142 Cr", normalized_value=81420000000.0,
            unit="INR", time_period=TimePeriod(raw="FY24", normalized_year=2024),
            scope=Scope(segment="Total"), evidence=Evidence(verbatim_quote="q", page_number=2, verified=True),
            confidence=0.98
        )
        fact_b = Fact(
            fact_id="fb_1", document_id="doc2", source_document="doc2.pdf", page_number=10,
            subject="Delhivery", predicate="Revenue", raw_value="81,420 Million", normalized_value=81420000000.0,
            unit="INR", time_period=TimePeriod(raw="Fiscal 2024", normalized_year=2024),
            scope=Scope(segment="Total"), evidence=Evidence(verbatim_quote="q", page_number=10, verified=True),
            confidence=0.97
        )
        rel = self.reconciler.reconcile(fact_a, fact_b)
        self.assertEqual(rel.relationship, RelationshipType.CORROBORATED)
        self.assertIn("corroborate", rel.reason.lower())

    def test_contextual_reconciliation_by_time(self):
        fact_a = Fact(
            fact_id="fa_2", document_id="doc1", source_document="doc1.pdf", page_number=2,
            subject="Delhivery", predicate="Revenue", raw_value="₹7,225 Cr", normalized_value=72250000000.0,
            unit="INR", time_period=TimePeriod(raw="FY23", normalized_year=2023),
            scope=Scope(segment="Total"), evidence=Evidence(verbatim_quote="q", page_number=2, verified=True),
            confidence=0.95
        )
        fact_b = Fact(
            fact_id="fb_2", document_id="doc2", source_document="doc2.pdf", page_number=10,
            subject="Delhivery", predicate="Revenue", raw_value="₹8,142 Cr", normalized_value=81420000000.0,
            unit="INR", time_period=TimePeriod(raw="FY24", normalized_year=2024),
            scope=Scope(segment="Total"), evidence=Evidence(verbatim_quote="q", page_number=10, verified=True),
            confidence=0.96
        )
        rel = self.reconciler.reconcile(fact_a, fact_b)
        self.assertEqual(rel.relationship, RelationshipType.CONTEXTUALLY_RECONCILED)
        self.assertEqual(rel.reconciling_dimension, ReconcilingDimension.TIME_PERIOD)

    def test_contradiction(self):
        fact_a = Fact(
            fact_id="fa_3", document_id="doc1", source_document="doc1.pdf", page_number=5,
            subject="Company", predicate="Headcount", raw_value="500", normalized_value=500.0,
            unit="employees", time_period=TimePeriod(raw="2024", normalized_year=2024),
            scope=Scope(segment="Total"), evidence=Evidence(verbatim_quote="q", page_number=5, verified=True),
            confidence=0.95
        )
        fact_b = Fact(
            fact_id="fb_3", document_id="doc2", source_document="doc2.pdf", page_number=12,
            subject="Company", predicate="Headcount", raw_value="750", normalized_value=750.0,
            unit="employees", time_period=TimePeriod(raw="2024", normalized_year=2024),
            scope=Scope(segment="Total"), evidence=Evidence(verbatim_quote="q", page_number=12, verified=True),
            confidence=0.95
        )
        rel = self.reconciler.reconcile(fact_a, fact_b)
        self.assertEqual(rel.relationship, RelationshipType.CONTRADICTION)

if __name__ == "__main__":
    unittest.main()
