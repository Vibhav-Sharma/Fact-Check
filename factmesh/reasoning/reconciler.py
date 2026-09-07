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
        # Dimension A: Different Time Periods
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
