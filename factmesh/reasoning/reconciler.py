import uuid
from typing import List, Tuple, Optional
from ..schemas import (
    Fact, FactRelationship, RelationshipType, ReconcilingDimension
)
from .comparator import MultiDimensionalComparator

class FactReconciler:
    """
    Classifies cross-document relationships into CORROBORATED, CONTRADICTION,
    CONTEXTUALLY_RECONCILED, or UNCERTAIN with detailed explainability.
    """

    def __init__(self):
        self.comparator = MultiDimensionalComparator()

    def reconcile(self, fact_a: Fact, fact_b: Fact) -> FactRelationship:
        """
        Reconcile a pair of cross-document facts using multi-dimensional analysis.
        """
        comp = self.comparator.compare(fact_a, fact_b)
        rel_id = f"rel_{uuid.uuid4().hex[:8]}"

        # 1. Check for Corroboration: same metric, same time/scope, matching values
        if comp["numbers_match"] and (comp["time_identical"] or comp["time_missing"]) and comp["scope_identical"]:
            reason = (
                f"Both '{fact_a.source_document}' (page {fact_a.page_number}) and "
                f"'{fact_b.source_document}' (page {fact_b.page_number}) corroborate this fact. "
                f"'{fact_a.raw_value}' matches '{fact_b.raw_value}' for {fact_a.subject} ({fact_a.predicate}) "
                f"during time period {comp['time_a'] or 'specified period'}."
            )
            return FactRelationship(
                relationship_id=rel_id,
                fact_a_id=fact_a.fact_id,
                fact_b_id=fact_b.fact_id,
                relationship=RelationshipType.CORROBORATED,
                reconciling_dimension=ReconcilingDimension.NONE,
                reason=reason,
                dimension_details=comp,
                confidence=min(fact_a.confidence, fact_b.confidence),
                fact_a=fact_a,
                fact_b=fact_b
            )

        # 2. Check for Contextual Reconciliation: Numbers differ, but explained by context dimensions
        # Dimension A1: Cumulative Metrics with Different Temporal / Data Vintage Context
        if not comp["numbers_match"] and comp.get("is_cumulative") and comp.get("temporal_context_different"):
            year_a = comp.get("year_a")
            year_b = comp.get("year_b")
            val_a = comp.get("val_a")
            val_b = comp.get("val_b")

            # Clean metric name for display
            pred_lower = fact_a.predicate.lower()
            if "express parcel" in pred_lower:
                metric_name = "express parcel shipments"
            elif "shipment" in pred_lower:
                metric_name = "shipments"
            elif "cumulative" in pred_lower:
                metric_name = pred_lower.replace("cumulative", "").strip()
            else:
                metric_name = pred_lower

            # Determine temporal ordering
            if year_a is not None and year_b is not None and year_a < year_b:
                earlier_fact, later_fact = fact_a, fact_b
                earlier_time, later_time = comp["time_a"], comp["time_b"]
            elif year_a is not None and year_b is not None and year_b < year_a:
                earlier_fact, later_fact = fact_b, fact_a
                earlier_time, later_time = comp["time_b"], comp["time_a"]
            else:
                if val_a is not None and val_b is not None and val_a <= val_b:
                    earlier_fact, later_fact = fact_a, fact_b
                    earlier_time, later_time = comp["time_a"], comp["time_b"]
                else:
                    earlier_fact, later_fact = fact_b, fact_a
                    earlier_time, later_time = comp["time_b"], comp["time_a"]

            earlier_disp = earlier_fact.raw_value
            later_raw = later_fact.raw_value
            if "bn" in later_raw.lower():
                clean_num = later_raw.lower().replace("bn+", "").replace("bn", "").strip()
                later_disp = f">{clean_num} billion" if ("+" in later_raw or ">" in later_raw) else f"{clean_num} billion"
            elif later_raw.endswith("+"):
                later_disp = f">{later_raw.rstrip('+').strip()}"
            else:
                later_disp = later_raw

            reason = (
                f"The claims report cumulative {metric_name} at different points in time. "
                f"The {earlier_disp} figure is associated with {earlier_time}, "
                f"while the {later_disp} figure is reported for {later_time}. "
                f"The increase is therefore temporally consistent rather than contradictory."
            )
            return FactRelationship(
                relationship_id=rel_id,
                fact_a_id=fact_a.fact_id,
                fact_b_id=fact_b.fact_id,
                relationship=RelationshipType.CONTEXTUALLY_RECONCILED,
                reconciling_dimension=ReconcilingDimension.TIME_PERIOD_OR_DATA_VINTAGE,
                reason=reason,
                dimension_details=comp,
                confidence=0.95,
                fact_a=fact_a,
                fact_b=fact_b
            )

        # Dimension A2: Different Time Periods
        if not comp["numbers_match"] and comp["time_different"]:
            reason = (
                f"Apparent discrepancy between '{fact_a.raw_value}' and '{fact_b.raw_value}' is fully reconciled by "
                f"TIME PERIOD context: '{fact_a.source_document}' refers to {comp['time_a']}, whereas "
                f"'{fact_b.source_document}' refers to {comp['time_b']}."
            )
            return FactRelationship(
                relationship_id=rel_id,
                fact_a_id=fact_a.fact_id,
                fact_b_id=fact_b.fact_id,
                relationship=RelationshipType.CONTEXTUALLY_RECONCILED,
                reconciling_dimension=ReconcilingDimension.TIME_PERIOD,
                reason=reason,
                dimension_details=comp,
                confidence=0.92,
                fact_a=fact_a,
                fact_b=fact_b
            )

        # Dimension B: Different Operational or Reporting Scope
        if not comp["numbers_match"] and (comp["scope_different"] or comp["reporting_different"]):
            dim = ReconcilingDimension.SCOPE_OR_SEGMENT
            reason = (
                f"Claims differ in value ('{fact_a.raw_value}' vs '{fact_b.raw_value}'), but are reconciled by "
                f"OPERATIONAL / REPORTING SCOPE: {fact_a.source_document} reports on '{comp['scope_a'] or 'Total'}', "
                f"while {fact_b.source_document} reports on '{comp['scope_b'] or 'Segment'}'."
            )
            return FactRelationship(
                relationship_id=rel_id,
                fact_a_id=fact_a.fact_id,
                fact_b_id=fact_b.fact_id,
                relationship=RelationshipType.CONTEXTUALLY_RECONCILED,
                reconciling_dimension=dim,
                reason=reason,
                dimension_details=comp,
                confidence=0.88,
                fact_a=fact_a,
                fact_b=fact_b
            )

        # Dimension C: Units / Currency
        if not comp["unit_identical"] and comp["val_a"] is not None and comp["val_b"] is not None:
            reason = (
                f"Values differ due to UNIT / CURRENCY convention: '{fact_a.raw_value}' ({comp['unit_a']}) "
                f"vs '{fact_b.raw_value}' ({comp['unit_b']})."
            )
            return FactRelationship(
                relationship_id=rel_id,
                fact_a_id=fact_a.fact_id,
                fact_b_id=fact_b.fact_id,
                relationship=RelationshipType.CONTEXTUALLY_RECONCILED,
                reconciling_dimension=ReconcilingDimension.UNIT_OR_CURRENCY,
                reason=reason,
                dimension_details=comp,
                confidence=0.85,
                fact_a=fact_a,
                fact_b=fact_b
            )

        # 3. Check for Genuine Contradiction: Same entity, same metric, same time period & scope, but irreconcilable values
        if not comp["numbers_match"] and comp["time_identical"] and comp["scope_identical"]:
            reason = (
                f"GENUINE CONTRADICTION: Both documents refer to the exact same metric ({fact_a.predicate}) for "
                f"{fact_a.subject} during the same period ({comp['time_a']}), but report conflicting values: "
                f"'{fact_a.raw_value}' in '{fact_a.source_document}' (page {fact_a.page_number}) vs "
                f"'{fact_b.raw_value}' in '{fact_b.source_document}' (page {fact_b.page_number}). "
                f"No contextual reconciling dimension accounts for the discrepancy."
            )
            return FactRelationship(
                relationship_id=rel_id,
                fact_a_id=fact_a.fact_id,
                fact_b_id=fact_b.fact_id,
                relationship=RelationshipType.CONTRADICTION,
                reconciling_dimension=ReconcilingDimension.NONE,
                reason=reason,
                dimension_details=comp,
                confidence=0.94,
                fact_a=fact_a,
                fact_b=fact_b
            )

        # 4. Fallback: Uncertain
        reason = (
            f"UNCERTAIN: Discrepancy observed between '{fact_a.raw_value}' and '{fact_b.raw_value}' with "
            f"insufficient contextual metadata to decisively determine contradiction vs contextual divergence."
        )
        return FactRelationship(
            relationship_id=rel_id,
            fact_a_id=fact_a.fact_id,
            fact_b_id=fact_b.fact_id,
            relationship=RelationshipType.UNCERTAIN,
            reconciling_dimension=ReconcilingDimension.NONE,
            reason=reason,
            dimension_details=comp,
            confidence=0.55,
            fact_a=fact_a,
            fact_b=fact_b
        )
