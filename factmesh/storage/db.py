import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..config import settings
from ..schemas import Fact, FactRelationship, FailureRecord, DocumentInfo, Evidence, TimePeriod, Scope

class Database:
    """SQLite-based storage layer for documents, facts, relationships, and failures."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or settings.database_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    page_count INTEGER NOT NULL,
                    processed_at TEXT,
                    status TEXT NOT NULL,
                    fact_count INTEGER DEFAULT 0
                )
            """)

            # Facts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    fact_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    source_document TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    raw_value TEXT NOT NULL,
                    normalized_value REAL,
                    unit TEXT,
                    time_period TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    evidence TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    dynamic_attributes TEXT,
                    FOREIGN KEY(document_id) REFERENCES documents(document_id)
                )
            """)

            # Relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    relationship_id TEXT PRIMARY KEY,
                    fact_a_id TEXT NOT NULL,
                    fact_b_id TEXT NOT NULL,
                    relationship TEXT NOT NULL,
                    reconciling_dimension TEXT,
                    reason TEXT NOT NULL,
                    dimension_details TEXT,
                    confidence REAL NOT NULL,
                    FOREIGN KEY(fact_a_id) REFERENCES facts(fact_id),
                    FOREIGN KEY(fact_b_id) REFERENCES facts(fact_id)
                )
            """)

            # Failures table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS failures (
                    failure_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    source_document TEXT NOT NULL,
                    page_number INTEGER,
                    stage TEXT NOT NULL,
                    failure_type TEXT NOT NULL,
                    raw_snippet TEXT,
                    description TEXT NOT NULL,
                    attempted_fact TEXT,
                    confidence REAL NOT NULL,
                    mitigation_strategy TEXT NOT NULL
                )
            """)
            conn.commit()

    # --- Document operations ---
    def save_document(self, doc: DocumentInfo):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO documents 
                (document_id, filename, file_path, page_count, processed_at, status, fact_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (doc.document_id, doc.filename, doc.file_path, doc.page_count, doc.processed_at, doc.status, doc.fact_count))
            conn.commit()

    def get_documents(self) -> List[DocumentInfo]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM documents ORDER BY processed_at DESC").fetchall()
            return [
                DocumentInfo(
                    document_id=r["document_id"],
                    filename=r["filename"],
                    file_path=r["file_path"],
                    page_count=r["page_count"],
                    processed_at=r["processed_at"],
                    status=r["status"],
                    fact_count=r["fact_count"]
                ) for r in rows
            ]

    # --- Fact operations ---
    def save_facts(self, facts: List[Fact]):
        with self._get_connection() as conn:
            for f in facts:
                conn.execute("""
                    INSERT OR REPLACE INTO facts
                    (fact_id, document_id, source_document, page_number, subject, predicate,
                     raw_value, normalized_value, unit, time_period, scope, evidence,
                     confidence, dynamic_attributes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f.fact_id, f.document_id, f.source_document, f.page_number, f.subject, f.predicate,
                    f.raw_value, f.normalized_value, f.unit,
                    json.dumps(f.time_period.model_dump()),
                    json.dumps(f.scope.model_dump()),
                    json.dumps(f.evidence.model_dump()),
                    f.confidence,
                    json.dumps(f.dynamic_attributes)
                ))
            conn.commit()

    def get_facts(self, document_id: Optional[str] = None) -> List[Fact]:
        with self._get_connection() as conn:
            query = "SELECT * FROM facts"
            params = []
            if document_id:
                query += " WHERE document_id = ?"
                params.append(document_id)
            query += " ORDER BY page_number ASC"
            
            rows = conn.execute(query, params).fetchall()
            facts = []
            for r in rows:
                facts.append(Fact(
                    fact_id=r["fact_id"],
                    document_id=r["document_id"],
                    source_document=r["source_document"],
                    page_number=r["page_number"],
                    subject=r["subject"],
                    predicate=r["predicate"],
                    raw_value=r["raw_value"],
                    normalized_value=r["normalized_value"],
                    unit=r["unit"],
                    time_period=TimePeriod(**json.loads(r["time_period"])),
                    scope=Scope(**json.loads(r["scope"])),
                    evidence=Evidence(**json.loads(r["evidence"])),
                    confidence=r["confidence"],
                    dynamic_attributes=json.loads(r["dynamic_attributes"] or "{}")
                ))
            return facts

    def get_fact_by_id(self, fact_id: str) -> Optional[Fact]:
        with self._get_connection() as conn:
            r = conn.execute("SELECT * FROM facts WHERE fact_id = ?", (fact_id,)).fetchone()
            if not r:
                return None
            return Fact(
                fact_id=r["fact_id"],
                document_id=r["document_id"],
                source_document=r["source_document"],
                page_number=r["page_number"],
                subject=r["subject"],
                predicate=r["predicate"],
                raw_value=r["raw_value"],
                normalized_value=r["normalized_value"],
                unit=r["unit"],
                time_period=TimePeriod(**json.loads(r["time_period"])),
                scope=Scope(**json.loads(r["scope"])),
                evidence=Evidence(**json.loads(r["evidence"])),
                confidence=r["confidence"],
                dynamic_attributes=json.loads(r["dynamic_attributes"] or "{}")
            )

    # --- Relationship operations ---
    def save_relationships(self, relationships: List[FactRelationship]):
        with self._get_connection() as conn:
            for rel in relationships:
                conn.execute("""
                    INSERT OR REPLACE INTO relationships
                    (relationship_id, fact_a_id, fact_b_id, relationship,
                     reconciling_dimension, reason, dimension_details, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rel.relationship_id, rel.fact_a_id, rel.fact_b_id, rel.relationship.value,
                    rel.reconciling_dimension.value if rel.reconciling_dimension else None,
                    rel.reason, json.dumps(rel.dimension_details), rel.confidence
                ))
            conn.commit()

    def get_relationships(self, rel_type: Optional[str] = None) -> List[FactRelationship]:
        with self._get_connection() as conn:
            query = "SELECT * FROM relationships"
            params = []
            if rel_type:
                query += " WHERE relationship = ?"
                params.append(rel_type)
            rows = conn.execute(query, params).fetchall()

            rels = []
            for r in rows:
                fa = self.get_fact_by_id(r["fact_a_id"])
                fb = self.get_fact_by_id(r["fact_b_id"])
                rels.append(FactRelationship(
                    relationship_id=r["relationship_id"],
                    fact_a_id=r["fact_a_id"],
                    fact_b_id=r["fact_b_id"],
                    relationship=r["relationship"],
                    reconciling_dimension=r["reconciling_dimension"] or "NONE",
                    reason=r["reason"],
                    dimension_details=json.loads(r["dimension_details"] or "{}"),
                    confidence=r["confidence"],
                    fact_a=fa,
                    fact_b=fb
                ))
            return rels

    # --- Failure operations ---
    def save_failures(self, failures: List[FailureRecord]):
        with self._get_connection() as conn:
            for f in failures:
                conn.execute("""
                    INSERT OR REPLACE INTO failures
                    (failure_id, document_id, source_document, page_number,
                     stage, failure_type, raw_snippet, description, attempted_fact,
                     confidence, mitigation_strategy)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f.failure_id, f.document_id, f.source_document, f.page_number,
                    f.stage, f.failure_type, f.raw_snippet, f.description,
                    json.dumps(f.attempted_fact) if f.attempted_fact else None,
                    f.confidence, f.mitigation_strategy
                ))
            conn.commit()

    def get_failures(self) -> List[FailureRecord]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM failures ORDER BY page_number ASC").fetchall()
            return [
                FailureRecord(
                    failure_id=r["failure_id"],
                    document_id=r["document_id"],
                    source_document=r["source_document"],
                    page_number=r["page_number"],
                    stage=r["stage"],
                    failure_type=r["failure_type"],
                    raw_snippet=r["raw_snippet"],
                    description=r["description"],
                    attempted_fact=json.loads(r["attempted_fact"]) if r["attempted_fact"] else None,
                    confidence=r["confidence"],
                    mitigation_strategy=r["mitigation_strategy"]
                ) for r in rows
            ]

    def clear_all(self):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM relationships")
            conn.execute("DELETE FROM facts")
            conn.execute("DELETE FROM documents")
            conn.execute("DELETE FROM failures")
            conn.commit()

db = Database()
