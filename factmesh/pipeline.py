import time
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import settings, UPLOAD_DIR, STARTER_DIR
from .schemas import DocumentInfo, Fact, FactRelationship, FailureRecord
from .ingestion import PDFParser, PageChunker
from .extraction import FactExtractor, telemetry
from .storage import db, FactCandidateIndex
from .reasoning import FactReconciler
from .starter_data import (
    get_delhivery_starter_facts,
    get_macro_starter_facts,
    get_demonstration_failures
)

class FactMeshPipeline:
    """End-to-end processing pipeline for documents, facts, and cross-document reasoning."""

    def __init__(self):
        self.extractor = FactExtractor()
        self.chunker = PageChunker(window_size=settings.chunk_page_size, overlap=settings.chunk_overlap)
        self.index = FactCandidateIndex(threshold=settings.similarity_threshold)
        self.reconciler = FactReconciler()

    def process_pdf(self, pdf_path: Path, doc_id: Optional[str] = None) -> DocumentInfo:
        """
        Ingest and process a single PDF document.
        """
        pdf_path = Path(pdf_path)
        doc_id = doc_id or f"doc_{uuid.uuid4().hex[:8]}"
        parser = PDFParser(pdf_path)
        meta = parser.get_metadata()

        # Extract pages
        pages = parser.extract_pages(max_pages=settings.max_pages_per_large_doc)
        
        # Save document info
        doc_info = DocumentInfo(
            document_id=doc_id,
            filename=pdf_path.name,
            file_path=str(pdf_path),
            page_count=meta["page_count"],
            processed_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            status="processing",
            fact_count=0
        )
        db.save_document(doc_info)

        # Extract facts
        extracted_facts = self.extractor.extract_from_pages(
            document_id=doc_id,
            source_document=pdf_path.name,
            pages_data=pages
        )

        # Save facts to database
        db.save_facts(extracted_facts)

        # Update doc status
        doc_info.status = "processed"
        doc_info.fact_count = len(extracted_facts)
        db.save_document(doc_info)

        # Save any new failures logged to telemetry
        db.save_failures(telemetry.get_all())

        return doc_info

    def run_cross_document_analysis(self) -> List[FactRelationship]:
        """
        Run cross-document candidate discovery and reconciliation across all stored facts.
        """
        all_facts = db.get_facts()
        if len(all_facts) < 2:
            return []

        # Find candidates using semantic index
        candidates = self.index.find_cross_document_candidates(all_facts)
        relationships = []

        for fact_a, fact_b, score in candidates:
            rel = self.reconciler.reconcile(fact_a, fact_b)
            relationships.append(rel)

        db.save_relationships(relationships)
        return relationships

    def load_starter_dataset(self, dataset_name: str):
        """
        One-click loading and processing of starter datasets: 'delhivery' or 'india-macroeconomy'.
        """
        target_dir = STARTER_DIR / dataset_name
        if not target_dir.exists():
            raise FileNotFoundError(f"Starter dataset folder '{dataset_name}' not found.")

        # Ingest PDF documents
        pdf_files = sorted(list(target_dir.glob("*.pdf")))
        for pdf in pdf_files:
            # Check if doc exists
            existing_docs = [d for d in db.get_documents() if d.filename == pdf.name]
            if not existing_docs:
                parser = PDFParser(pdf)
                meta = parser.get_metadata()
                doc_info = DocumentInfo(
                    document_id=f"doc_{pdf.stem[:12]}",
                    filename=pdf.name,
                    file_path=str(pdf),
                    page_count=meta["page_count"],
                    processed_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                    status="processed",
                    fact_count=0
                )
                db.save_document(doc_info)

        # Populate reference facts
        if dataset_name == "delhivery":
            facts = get_delhivery_starter_facts()
        else:
            facts = get_macro_starter_facts()

        db.save_facts(facts)

        # Save failure cases for demonstration
        failures = get_demonstration_failures()
        db.save_failures(failures)

        # Run cross-document reasoning
        self.run_cross_document_analysis()

pipeline = FactMeshPipeline()
