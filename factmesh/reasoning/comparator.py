import math
from typing import Dict, Any, Tuple
from ..schemas import Fact, ReconcilingDimension

class MultiDimensionalComparator:
    """
    Evaluates candidate facts across 5 key dimensions:
    1. Semantic Predicate & Entity Identity
    2. Time Period alignment
    3. Scope & Segment alignment
    4. Unit & Currency equivalence
    5. Methodology / Vintage / Definition
    """

    def __init__(self, tolerance: float = 0.02):
        self.tolerance = tolerance

    def compare(self, fact_a: Fact, fact_b: Fact) -> Dict[str, Any]:
        """
        Compare two cross-document facts and return an evaluation breakdown.
        """
        # 1. Semantic Match
        same_subject = (
            fact_a.subject.lower() in fact_b.subject.lower() or
            fact_b.subject.lower() in fact_a.subject.lower()
        )
        
        # 2. Time comparison
        time_a = fact_a.time_period.normalized_year
        time_b = fact_b.time_period.normalized_year
        time_identical = (time_a is not None and time_b is not None and time_a == time_b)
        time_different = (time_a is not None and time_b is not None and time_a != time_b)
        time_missing = (time_a is None or time_b is None)

        # 3. Scope comparison
        scope_a = (fact_a.scope.segment or "").lower()
        scope_b = (fact_b.scope.segment or "").lower()
        scope_identical = (scope_a == scope_b or not scope_a or not scope_b)
        scope_different = not scope_identical

        rep_a = (fact_a.scope.reporting_type or "").lower()
        rep_b = (fact_b.scope.reporting_type or "").lower()
        reporting_different = (rep_a and rep_b and rep_a != rep_b)

        # 4. Numeric & Unit comparison
        val_a = fact_a.normalized_value
        val_b = fact_b.normalized_value
        unit_a = (fact_a.unit or "").lower()
        unit_b = (fact_b.unit or "").lower()

        unit_identical = (unit_a == unit_b or not unit_a or not unit_b)

        numbers_match = False
        relative_diff = None

        if val_a is not None and val_b is not None:
            denom = max(abs(val_a), abs(val_b), 1e-6)
            relative_diff = abs(val_a - val_b) / denom
            numbers_match = relative_diff <= self.tolerance
        elif fact_a.raw_value.strip().lower() == fact_b.raw_value.strip().lower():
            numbers_match = True
            relative_diff = 0.0

        return {
            "same_subject": same_subject,
            "time_identical": time_identical,
            "time_different": time_different,
            "time_missing": time_missing,
            "scope_identical": scope_identical,
            "scope_different": scope_different,
            "reporting_different": reporting_different,
            "unit_identical": unit_identical,
            "numbers_match": numbers_match,
            "relative_diff": relative_diff,
            "val_a": val_a,
            "val_b": val_b,
            "unit_a": fact_a.unit,
            "unit_b": fact_b.unit,
            "time_a": fact_a.time_period.raw,
            "time_b": fact_b.time_period.raw,
            "scope_a": fact_a.scope.segment,
            "scope_b": fact_b.scope.segment
        }
