from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class RelationshipType(str, Enum):
    CORROBORATED = "CORROBORATED"
    CONTRADICTION = "CONTRADICTION"
    CONTEXTUALLY_RECONCILED = "CONTEXTUALLY_RECONCILED"
    UNCERTAIN = "UNCERTAIN"

class ReconcilingDimension(str, Enum):
    TIME_PERIOD = "TIME_PERIOD"
    SCOPE_OR_SEGMENT = "SCOPE_OR_SEGMENT"
    UNIT_OR_CURRENCY = "UNIT_OR_CURRENCY"
    DEFINITION_OR_ACCOUNTING = "DEFINITION_OR_ACCOUNTING"
    DATA_VINTAGE_OR_REVISION = "DATA_VINTAGE_OR_REVISION"
    TIME_PERIOD_OR_DATA_VINTAGE = "TIME_PERIOD / DATA_VINTAGE"
    NONE = "NONE"

class Evidence(BaseModel):
    verbatim_quote: str = Field(..., description="Exact snippet quoted from the PDF page")
    page_number: int = Field(..., description="1-indexed physical/printed page number")
    char_start: Optional[int] = Field(None, description="Start character index in page text")
    char_end: Optional[int] = Field(None, description="End character index in page text")
    verified: bool = Field(False, description="True if verbatim quote verified in actual page text")
    verification_score: float = Field(0.0, description="Fuzzy match score (0.0 to 1.0)")

class TimePeriod(BaseModel):
    raw: str = Field(..., description="Raw time string as extracted, e.g., 'FY24', '2024-25'")
    normalized_year: Optional[int] = Field(None, description="Target normalized year, e.g. 2024")
    period_type: Optional[str] = Field(None, description="fiscal_year, calendar_year, quarter, multi_year")
    normalized_start: Optional[str] = Field(None, description="ISO-like start date e.g. 2023-04-01")
    normalized_end: Optional[str] = Field(None, description="ISO-like end date e.g. 2024-03-31")

class Scope(BaseModel):
    geography: Optional[str] = Field("National", description="Geographic boundary, e.g. India, Global")
    segment: Optional[str] = Field("Total", description="Operational segment, e.g. Express Parcel, PTL, Headline")
    reporting_type: Optional[str] = Field("Consolidated", description="Consolidated, Standalone, Advance Est, etc.")

class Fact(BaseModel):
    fact_id: str = Field(..., description="Unique fact identifier")
    document_id: str = Field(..., description="Parent document identifier")
    source_document: str = Field(..., description="Original filename")
    page_number: int = Field(..., description="1-indexed page number")
    subject: str = Field(..., description="Entity or macro subject (e.g. 'Delhivery', 'Real GDP Growth')")
    predicate: str = Field(..., description="Metric or property (e.g. 'Revenue', 'Inflation Rate')")
    raw_value: str = Field(..., description="Verbatim value text (e.g. '₹7,241 Cr', '8.2%')")
    normalized_value: Optional[float] = Field(None, description="Clean numeric value if numeric")
    unit: Optional[str] = Field(None, description="Normalized unit (e.g. 'INR Cr', '%', 'Million shipments')")
    time_period: TimePeriod
    scope: Scope
    evidence: Evidence
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence score")
    dynamic_attributes: Dict[str, Any] = Field(default_factory=dict, description="Extensible schema properties")

class FactRelationship(BaseModel):
    relationship_id: str
    fact_a_id: str
    fact_b_id: str
    relationship: RelationshipType
    reconciling_dimension: ReconcilingDimension = ReconcilingDimension.NONE
    reason: str
    dimension_details: Dict[str, Any] = Field(default_factory=dict)
    confidence: float
    fact_a: Optional[Fact] = None
    fact_b: Optional[Fact] = None

class FailureRecord(BaseModel):
    failure_id: str
    document_id: str
    source_document: str
    page_number: Optional[int] = None
    stage: str = Field(..., description="extraction, grounding, comparison, or normalization")
    failure_type: str = Field(..., description="Category of failure")
    raw_snippet: Optional[str] = None
    description: str
    attempted_fact: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    mitigation_strategy: str

class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    file_path: str
    page_count: int
    processed_at: Optional[str] = None
    status: str = "uploaded"  # uploaded, processed, error
    fact_count: int = 0
