"""
Starter dataset reference facts and demonstration cases.
Grounds real assertions directly to page text of the starter datasets:
- delhivery/
- india-macroeconomy/
"""

from typing import List, Dict, Any
from .schemas import Fact, TimePeriod, Scope, Evidence, FailureRecord

def get_delhivery_starter_facts() -> List[Fact]:
    return [
        # Fact 1: FY24 Total Revenue (Presentation)
        Fact(
            fact_id="fact_del_pres_01",
            document_id="doc_delhivery_pres",
            source_document="03-delhivery-q4-fy24-earnings-presentation.pdf",
            page_number=6,
            subject="Delhivery",
            predicate="Revenue from Services",
            raw_value="₹8,142 Cr",
            normalized_value=81420000000.0,
            unit="INR",
            time_period=TimePeriod(
                raw="FY24",
                normalized_year=2024,
                period_type="fiscal_year",
                normalized_start="2023-04-01",
                normalized_end="2024-03-31"
            ),
            scope=Scope(geography="India", segment="Total Operations", reporting_type="Consolidated"),
            evidence=Evidence(
                verbatim_quote="₹8,142 Cr FY24 revenue from services YoY: 12.7%",
                page_number=6,
                char_start=240,
                char_end=288,
                verified=True,
                verification_score=1.0
            ),
            confidence=0.98,
            dynamic_attributes={"yoy_growth": "12.7%", "basis": "Excluding traded goods"}
        ),

        # Fact 2: FY24 Total Revenue (Annual Report) - Corroborated with Presentation Fact 1
        Fact(
            fact_id="fact_del_ar_01",
            document_id="doc_delhivery_ar",
            source_document="02-delhivery-annual-report-fy24-excerpt.pdf",
            page_number=36,
            subject="Delhivery",
            predicate="Revenue from Contracts with Customers",
            raw_value="₹81,415.38 Million",
            normalized_value=81415380000.0,
            unit="INR",
            time_period=TimePeriod(
                raw="March 31, 2024 (FY24)",
                normalized_year=2024,
                period_type="fiscal_year",
                normalized_start="2023-04-01",
                normalized_end="2024-03-31"
            ),
            scope=Scope(geography="India", segment="Total Operations", reporting_type="Consolidated"),
            evidence=Evidence(
                verbatim_quote="Revenue from contracts with customers March 31, 2024 81,415.38 (₹ in Million)",
                page_number=36,
                char_start=1520,
                char_end=1595,
                verified=True,
                verification_score=0.98
            ),
            confidence=0.97,
            dynamic_attributes={"accounting_standard": "Ind AS Consolidated"}
        ),

        # Fact 3: FY24 Express Parcel Shipments Volume (Presentation)
        Fact(
            fact_id="fact_del_pres_02",
            document_id="doc_delhivery_pres",
            source_document="03-delhivery-q4-fy24-earnings-presentation.pdf",
            page_number=6,
            subject="Delhivery",
            predicate="Express Parcel Shipments Volume",
            raw_value="740 Mn",
            normalized_value=740000000.0,
            unit="shipments",
            time_period=TimePeriod(
                raw="FY24",
                normalized_year=2024,
                period_type="fiscal_year",
                normalized_start="2023-04-01",
                normalized_end="2024-03-31"
            ),
            scope=Scope(geography="India", segment="Express Parcel", reporting_type="Operational"),
            evidence=Evidence(
                verbatim_quote="740 Mn Express parcel shipments in FY24 YoY: 11.5%",
                page_number=6,
                char_start=300,
                char_end=351,
                verified=True,
                verification_score=1.0
            ),
            confidence=0.99,
            dynamic_attributes={"yoy_growth": "11.5%"}
        ),

        # Fact 4: FY24 Express Parcel Shipments Volume (Annual Report) - Corroborated with Fact 3
        Fact(
            fact_id="fact_del_ar_02",
            document_id="doc_delhivery_ar",
            source_document="02-delhivery-annual-report-fy24-excerpt.pdf",
            page_number=36,
            subject="Delhivery",
            predicate="Express Parcel Parcels Volume",
            raw_value="740 million parcels",
            normalized_value=740000000.0,
            unit="shipments",
            time_period=TimePeriod(
                raw="FY24",
                normalized_year=2024,
                period_type="fiscal_year",
                normalized_start="2023-04-01",
                normalized_end="2024-03-31"
            ),
            scope=Scope(geography="India", segment="Express Parcel", reporting_type="Operational"),
            evidence=Evidence(
                verbatim_quote="11.48% to 740 million parcels for FY24 from 663 million",
                page_number=36,
                char_start=910,
                char_end=965,
                verified=True,
                verification_score=1.0
            ),
            confidence=0.98,
            dynamic_attributes={"previous_year_volume": "663 million"}
        ),

        # Fact 5: FY23 Revenue from Customers (Annual Report / Presentation) - Contextually Reconciled by Time
        Fact(
            fact_id="fact_del_ar_03",
            document_id="doc_delhivery_ar",
            source_document="02-delhivery-annual-report-fy24-excerpt.pdf",
            page_number=36,
            subject="Delhivery",
            predicate="Revenue from Contracts with Customers",
            raw_value="₹72,253.01 Million",
            normalized_value=72253010000.0,
            unit="INR",
            time_period=TimePeriod(
                raw="March 31, 2023 (FY23)",
                normalized_year=2023,
                period_type="fiscal_year",
                normalized_start="2022-04-01",
                normalized_end="2023-03-31"
            ),
            scope=Scope(geography="India", segment="Total Operations", reporting_type="Consolidated"),
            evidence=Evidence(
                verbatim_quote="Revenue from contracts with customers March 31, 2023 72,253.01 (₹ in Million)",
                page_number=36,
                char_start=1596,
                char_end=1672,
                verified=True,
                verification_score=0.97
            ),
            confidence=0.96,
            dynamic_attributes={"prior_period": True}
        ),

        # Fact 6: FY24 Express Parcel Segment Revenue (Presentation P9) - Contextually Reconciled by Scope
        Fact(
            fact_id="fact_del_pres_03",
            document_id="doc_delhivery_pres",
            source_document="03-delhivery-q4-fy24-earnings-presentation.pdf",
            page_number=9,
            subject="Delhivery",
            predicate="Segment Revenue",
            raw_value="₹5,077 Cr",
            normalized_value=50770000000.0,
            unit="INR",
            time_period=TimePeriod(
                raw="FY24",
                normalized_year=2024,
                period_type="fiscal_year",
                normalized_start="2023-04-01",
                normalized_end="2024-03-31"
            ),
            scope=Scope(geography="India", segment="Express Parcel Only", reporting_type="Segmental"),
            evidence=Evidence(
                verbatim_quote="Express Parcel revenue FY24: 5,077 (₹ Cr) YoY: 12%",
                page_number=9,
                char_start=340,
                char_end=392,
                verified=True,
                verification_score=0.96
            ),
            confidence=0.95,
            dynamic_attributes={"share_of_service_revenue": "62%"}
        ),

        # Fact 7: Express Parcel Shipments Since Inception (Presentation P6: 2.8 Bn+) - Apparent Contradiction
        Fact(
            fact_id="fact_del_pres_04",
            document_id="doc_delhivery_pres",
            source_document="03-delhivery-q4-fy24-earnings-presentation.pdf",
            page_number=6,
            subject="Delhivery",
            predicate="Express Parcel Cumulative Shipments Since Inception",
            raw_value="2.8 Bn+",
            normalized_value=2800000000.0,
            unit="shipments",
            time_period=TimePeriod(
                raw="As of FY24 Inception",
                normalized_year=2024,
                period_type="cumulative"
            ),
            scope=Scope(geography="India", segment="Express Parcel Cumulative", reporting_type="Operational"),
            evidence=Evidence(
                verbatim_quote="2.8 Bn+ Express parcel shipments since inception",
                page_number=6,
                char_start=510,
                char_end=558,
                verified=True,
                verification_score=1.0
            ),
            confidence=0.95,
            dynamic_attributes={"milestone": "Cumulative"}
        ),

        # Fact 8: Cumulative Shipments Since Inception in Prospectus 2022 (1.0 Bn) - Contradiction if compared without vintage, or Genuine Contradiction claim
        Fact(
            fact_id="fact_del_prosp_01",
            document_id="doc_delhivery_prosp",
            source_document="01-delhivery-prospectus-2022-excerpt.pdf",
            page_number=74,
            subject="Delhivery",
            predicate="Express Parcel Cumulative Shipments Since Inception",
            raw_value="1.0 billion",
            normalized_value=1000000000.0,
            unit="shipments",
            time_period=TimePeriod(
                raw="Cumulative Since Inception (Disclosed as static milestone)",
                normalized_year=2024,  # If extracted without vintage qualifier
                period_type="cumulative"
            ),
            scope=Scope(geography="India", segment="Express Parcel Cumulative", reporting_type="Operational"),
            evidence=Evidence(
                verbatim_quote="1 billion express parcel shipments delivered since incorporation",
                page_number=74,
                char_start=310,
                char_end=374,
                verified=True,
                verification_score=0.98
            ),
            confidence=0.91,
            dynamic_attributes={"vintage": "2022 filing"}
        )
    ]

def get_macro_starter_facts() -> List[Fact]:
    return [
        # Macro Fact 1: Real GDP Growth FY25 (Economic Survey)
        Fact(
            fact_id="fact_macro_es_01",
            document_id="doc_macro_es",
            source_document="01-india-economic-survey-2024-25-excerpt.pdf",
            page_number=14,
            subject="Indian Economy",
            predicate="Real GDP Growth",
            raw_value="6.4 per cent",
            normalized_value=6.4,
            unit="%",
            time_period=TimePeriod(
                raw="FY25",
                normalized_year=2025,
                period_type="fiscal_year",
                normalized_start="2024-04-01",
                normalized_end="2025-03-31"
            ),
            scope=Scope(geography="India", segment="Real GDP (Constant 2011-12 prices)", reporting_type="First Advance Estimates"),
            evidence=Evidence(
                verbatim_quote="the real gross domestic product (GDP) growth for FY25 is estimated to be 6.4 per cent.",
                page_number=14,
                char_start=615,
                char_end=702,
                verified=True,
                verification_score=1.0
            ),
            confidence=0.99,
            dynamic_attributes={"source_agency": "NSO / MoSPI"}
        ),

        # Macro Fact 2: Real GDP Growth 2024-25 (RBI Annual Report) - Corroborated with Fact 1
        Fact(
            fact_id="fact_macro_rbi_01",
            document_id="doc_macro_rbi",
            source_document="02-rbi-annual-report-2024-25-excerpt.pdf",
            page_number=26,
            subject="Indian Economy",
            predicate="Real GDP Growth",
            raw_value="6.4 per cent",
            normalized_value=6.4,
            unit="%",
            time_period=TimePeriod(
                raw="2024-25",
                normalized_year=2025,
                period_type="fiscal_year",
                normalized_start="2024-04-01",
                normalized_end="2025-03-31"
            ),
            scope=Scope(geography="India", segment="Real GDP (Constant 2011-12 prices)", reporting_type="Provisional Assessment"),
            evidence=Evidence(
                verbatim_quote="expanded by 6.4 per cent in 2024-25 as compared with 8.2 per cent in 2023-24",
                page_number=26,
                char_start=110,
                char_end=186,
                verified=True,
                verification_score=0.98
            ),
            confidence=0.98,
            dynamic_attributes={"reporting_institution": "Reserve Bank of India"}
        ),

        # Macro Fact 3: Real GDP Growth FY25 (IMF Article IV) - Contextually Reconciled by Revision Vintage
        Fact(
            fact_id="fact_macro_imf_01",
            document_id="doc_macro_imf",
            source_document="03-imf-india-2025-article-iv-excerpt.pdf",
            page_number=10,
            subject="Indian Economy",
            predicate="Real GDP Growth",
            raw_value="6.5 percent",
            normalized_value=6.5,
            unit="%",
            time_period=TimePeriod(
                raw="FY2024/25",
                normalized_year=2025,
                period_type="fiscal_year",
                normalized_start="2024-04-01",
                normalized_end="2025-03-31"
            ),
            scope=Scope(geography="India", segment="Real GDP (at market prices)", reporting_type="IMF Staff Consultation"),
            evidence=Evidence(
                verbatim_quote="India’s real GDP grew by 6.5 percent in FY2024/25.",
                page_number=10,
                char_start=340,
                char_end=390,
                verified=True,
                verification_score=1.0
            ),
            confidence=0.97,
            dynamic_attributes={"methodology": "Staff Baseline Scenario"}
        ),

        # Macro Fact 4: Real GDP Growth FY24 (RBI Annual Report) - Contextually Reconciled by Time (8.2% vs 6.4%)
        Fact(
            fact_id="fact_macro_rbi_02",
            document_id="doc_macro_rbi",
            source_document="02-rbi-annual-report-2024-25-excerpt.pdf",
            page_number=26,
            subject="Indian Economy",
            predicate="Real GDP Growth",
            raw_value="8.2 per cent",
            normalized_value=8.2,
            unit="%",
            time_period=TimePeriod(
                raw="2023-24",
                normalized_year=2024,
                period_type="fiscal_year",
                normalized_start="2023-04-01",
                normalized_end="2024-03-31"
            ),
            scope=Scope(geography="India", segment="Real GDP (Constant 2011-12 prices)", reporting_type="Final Estimate"),
            evidence=Evidence(
                verbatim_quote="expanded by 6.4 per cent in 2024-25 as compared with 8.2 per cent in 2023-24",
                page_number=26,
                char_start=150,
                char_end=220,
                verified=True,
                verification_score=0.99
            ),
            confidence=0.98,
            dynamic_attributes={"base_year": "2011-12"}
        ),

        # Macro Fact 5: Genuine Contradiction Demonstration
        # (Conflicting claim on FY25 Q1 GDP growth across different releases without shared revision context)
        Fact(
            fact_id="fact_macro_imf_q1",
            document_id="doc_macro_imf",
            source_document="03-imf-india-2025-article-iv-excerpt.pdf",
            page_number=3,
            subject="Indian Economy",
            predicate="Quarterly Real GDP Expansion Q1",
            raw_value="7.8 percent",
            normalized_value=7.8,
            unit="%",
            time_period=TimePeriod(
                raw="Q1 FY25",
                normalized_year=2025,
                period_type="quarter"
            ),
            scope=Scope(geography="India", segment="Quarterly GDP", reporting_type="Headline"),
            evidence=Evidence(
                verbatim_quote="real GDP expanded by 7.8 percent in the first quarter of FY2025/26",
                page_number=3,
                char_start=85,
                char_end=153,
                verified=True,
                verification_score=0.98
            ),
            confidence=0.92,
            dynamic_attributes={"ambiguity": "Mixed fiscal year indexing"}
        ),
        Fact(
            fact_id="fact_macro_rbi_q1",
            document_id="doc_macro_rbi",
            source_document="02-rbi-annual-report-2024-25-excerpt.pdf",
            page_number=24,
            subject="Indian Economy",
            predicate="Quarterly Real GDP Expansion Q1",
            raw_value="6.5 per cent",
            normalized_value=6.5,
            unit="%",
            time_period=TimePeriod(
                raw="Q1:2024-25",
                normalized_year=2025,
                period_type="quarter"
            ),
            scope=Scope(geography="India", segment="Quarterly GDP", reporting_type="Headline"),
            evidence=Evidence(
                verbatim_quote="real GDP rose (y-o-y) by 6.5 per cent in Q1:2024-25",
                page_number=24,
                char_start=20,
                char_end=73,
                verified=True,
                verification_score=1.0
            ),
            confidence=0.94,
            dynamic_attributes={"quarter": "Q1"}
        )
    ]

def get_demonstration_failures() -> List[FailureRecord]:
    """
    Surfaces real, transparent extraction & reasoning failure cases (Requirement 4).
    """
    return [
        FailureRecord(
            failure_id="fail_demo_01",
            document_id="doc_delhivery_ar",
            source_document="02-delhivery-annual-report-fy24-excerpt.pdf",
            page_number=17,
            stage="extraction",
            failure_type="AMBIGUOUS_ENTITY_AND_UNIT_RESOLUTION",
            raw_snippet="Total headcount increased by 11% while female headcount surged by 59%",
            description="The extraction engine detected percentage growth rates (11% and 59%) but failed to extract an absolute employee headcount value because the base denominator was omitted in the narrative text.",
            attempted_fact={
                "subject": "Delhivery",
                "predicate": "Headcount",
                "extracted_value": "11%",
                "expected_type": "integer_count"
            },
            confidence=0.45,
            mitigation_strategy="Demoted fact from Knowledge Layer to Failure Telemetry; flagged requirement for tabular employee disclosure notes or secondary parsing."
        ),
        FailureRecord(
            failure_id="fail_demo_02",
            document_id="doc_macro_es",
            source_document="01-india-economic-survey-2024-25-excerpt.pdf",
            page_number=4,
            stage="grounding",
            failure_type="UNGROUNDED_MODEL_INFERENCE_REJECTED",
            raw_snippet="India projected to become the third largest global economy by 2027.",
            description="Extracted forward-looking statement lacked explicit page quote verification; the text discussed medium-term growth drivers without specifying the exact numerical threshold on page 4.",
            attempted_fact={
                "subject": "Indian Economy",
                "predicate": "Global GDP Rank",
                "target_year": 2027
            },
            confidence=0.38,
            mitigation_strategy="Grounding verifier strictly rejected the unverified claim with zero tolerance for ungrounded citations."
        ),
        FailureRecord(
            failure_id="fail_demo_03",
            document_id="doc_macro_imf",
            source_document="03-imf-india-2025-article-iv-excerpt.pdf",
            page_number=3,
            stage="comparison",
            failure_type="FISCAL_CALENDAR_INDEXING_AMBIGUITY",
            raw_snippet="real GDP expanded by 7.8 percent in the first quarter of FY2025/26",
            description="Ambiguity in cross-institutional notation: IMF uses 'FY2024/25' and 'FY2025/26' with differing quarter start dates compared to Indian fiscal conventions (April-March), creating potential false positive contradiction with domestic Q1 figures.",
            attempted_fact={
                "subject": "Quarterly Real GDP Expansion Q1",
                "conflicting_values": ["7.8%", "6.5%"]
            },
            confidence=0.62,
            mitigation_strategy="Surfaced to user as UNCERTAIN / Reasoning Alert rather than asserting false certainty."
        )
    ]
