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

    def test_cumulative_shipments_reconciliation(self):
        fact_a = Fact(
            fact_id="fa_cum_1", document_id="doc_pres", source_document="03-delhivery-q4-fy24-earnings-presentation.pdf",
            page_number=6, subject="Delhivery", predicate="Express Parcel Cumulative Shipments Since Inception",
            raw_value="2.8 Bn+", normalized_value=2800000000.0, unit="shipments",
            time_period=TimePeriod(raw="FY24", normalized_year=2024, period_type="cumulative"),
            scope=Scope(segment="Express Parcel Cumulative"),
            evidence=Evidence(verbatim_quote="2.8 Bn+ Express parcel shipments since inception", page_number=6, verified=True),
            confidence=0.98, dynamic_attributes={"milestone": "Cumulative", "vintage": "FY24"}
        )
        fact_b = Fact(
            fact_id="fb_cum_2", document_id="doc_prosp", source_document="01-delhivery-prospectus-2022-excerpt.pdf",
            page_number=74, subject="Delhivery", predicate="Express Parcel Cumulative Shipments Since Inception",
            raw_value="1 billion", normalized_value=1000000000.0, unit="shipments",
            time_period=TimePeriod(raw="2021", normalized_year=2021, period_type="cumulative"),
            scope=Scope(segment="Express Parcel Cumulative"),
            evidence=Evidence(verbatim_quote="1 billion express parcel shipments delivered since incorporation", page_number=74, verified=True),
            confidence=0.98, dynamic_attributes={"milestone": "Cumulative", "vintage": "2021 milestone"}
        )
        rel = self.reconciler.reconcile(fact_a, fact_b)
        self.assertEqual(rel.relationship, RelationshipType.CONTEXTUALLY_RECONCILED)
        self.assertEqual(rel.reconciling_dimension, ReconcilingDimension.TIME_PERIOD_OR_DATA_VINTAGE)
        self.assertIn("temporally consistent rather than contradictory", rel.reason)
        self.assertIn("1 billion figure is associated with 2021", rel.reason)
        self.assertIn(">2.8 billion figure is reported for FY24", rel.reason)

    def test_controlled_contradiction_fixture(self):
        fact_a = Fact(
            fact_id="fa_fix_1", document_id="doc_audit_a",
            source_document="[Demo Fixture] Internal Audit FY24", page_number=14,
            subject="Delhivery Operations", predicate="Express Parcel Shipments Volume",
            raw_value="740 million", normalized_value=740000000.0, unit="shipments",
            time_period=TimePeriod(raw="FY2024", normalized_year=2024),
            scope=Scope(segment="Express Parcel"),
            evidence=Evidence(verbatim_quote="q", page_number=14, verified=True),
            confidence=0.99
        )
        fact_b = Fact(
            fact_id="fb_fix_2", document_id="doc_audit_b",
            source_document="[Demo Fixture] Third-Party Review FY24", page_number=8,
            subject="Delhivery Operations", predicate="Express Parcel Shipments Volume",
            raw_value="810 million", normalized_value=810000000.0, unit="shipments",
            time_period=TimePeriod(raw="FY2024", normalized_year=2024),
            scope=Scope(segment="Express Parcel"),
            evidence=Evidence(verbatim_quote="q", page_number=8, verified=True),
            confidence=0.99
        )
        rel = self.reconciler.reconcile(fact_a, fact_b)
        self.assertEqual(rel.relationship, RelationshipType.CONTRADICTION)
        self.assertIn("GENUINE CONTRADICTION", rel.reason)

if __name__ == "__main__":
    unittest.main()
