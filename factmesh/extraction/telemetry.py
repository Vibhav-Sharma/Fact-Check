import uuid
from typing import List, Dict, Any, Optional
from ..schemas import FailureRecord

class FailureTelemetry:
    """Central registry and tracker for extraction, parsing, and reasoning failures."""

    def __init__(self):
        self._records: List[FailureRecord] = []

    def record_failure(
        self,
        document_id: str,
        source_document: str,
        stage: str,
        failure_type: str,
        description: str,
        mitigation_strategy: str,
        page_number: Optional[int] = None,
        raw_snippet: Optional[str] = None,
        attempted_fact: Optional[Dict[str, Any]] = None,
        confidence: float = 0.0
    ) -> FailureRecord:
        """Create and store a structured failure record."""
        rec = FailureRecord(
            failure_id=f"fail_{uuid.uuid4().hex[:8]}",
            document_id=document_id,
            source_document=source_document,
            page_number=page_number,
            stage=stage,
            failure_type=failure_type,
            raw_snippet=raw_snippet,
            description=description,
            attempted_fact=attempted_fact,
            confidence=confidence,
            mitigation_strategy=mitigation_strategy
        )
        self._records.append(rec)
        return rec

    def get_all(self) -> List[FailureRecord]:
        return list(self._records)

    def clear(self):
        self._records.clear()

# Global failure telemetry instance
telemetry = FailureTelemetry()
