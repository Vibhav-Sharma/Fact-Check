import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel

from ..config import UPLOAD_DIR
from ..schemas import DocumentInfo, Fact, FactRelationship, FailureRecord
from ..storage import db
from ..pipeline import pipeline

router = APIRouter(prefix="/api")

class StatsResponse(BaseModel):
    total_documents: int
    total_facts: int
    corroborated_count: int
    contradiction_count: int
    reconciled_count: int
    uncertain_count: int
    failure_count: int

@router.get("/stats", response_model=StatsResponse)
def get_stats():
    docs = db.get_documents()
    facts = db.get_facts()
    rels = db.get_relationships()
    failures = db.get_failures()

    corroborated = sum(1 for r in rels if r.relationship.value == "CORROBORATED")
    contradictions = sum(1 for r in rels if r.relationship.value == "CONTRADICTION")
    reconciled = sum(1 for r in rels if r.relationship.value == "CONTEXTUALLY_RECONCILED")
    uncertain = sum(1 for r in rels if r.relationship.value == "UNCERTAIN")

    return StatsResponse(
        total_documents=len(docs),
        total_facts=len(facts),
        corroborated_count=corroborated,
        contradiction_count=contradictions,
        reconciled_count=reconciled,
        uncertain_count=uncertain,
        failure_count=len(failures)
    )

@router.get("/documents", response_model=List[DocumentInfo])
def list_documents():
    return db.get_documents()

@router.post("/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    uploaded_docs = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")

        dest_path = UPLOAD_DIR / file.filename
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        doc_info = pipeline.process_pdf(dest_path)
        uploaded_docs.append(doc_info)

    # Trigger cross-document matching after upload
    pipeline.run_cross_document_analysis()
    return {"message": f"Successfully processed {len(uploaded_docs)} documents", "documents": uploaded_docs}

@router.post("/documents/process")
def process_existing():
    pipeline.run_cross_document_analysis()
    return {"message": "Cross-document reconciliation completed"}

@router.get("/facts", response_model=List[Fact])
def list_facts(
    document_id: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    min_confidence: Optional[float] = Query(None)
):
    facts = db.get_facts(document_id=document_id)
    if subject:
        facts = [f for f in facts if subject.lower() in f.subject.lower()]
    if min_confidence is not None:
        facts = [f for f in facts if f.confidence >= min_confidence]
    return facts

@router.get("/relationships", response_model=List[FactRelationship])
def list_relationships(rel_type: Optional[str] = Query(None)):
    return db.get_relationships(rel_type=rel_type)

@router.get("/failures", response_model=List[FailureRecord])
def list_failures():
    return db.get_failures()

@router.post("/dataset-presets/{preset_name}")
def load_preset(preset_name: str):
    if preset_name not in ["delhivery", "india-macroeconomy"]:
        raise HTTPException(status_code=404, detail="Invalid preset. Choose 'delhivery' or 'india-macroeconomy'.")
    db.clear_all()
    pipeline.load_starter_dataset(preset_name)
    return {"message": f"Preset '{preset_name}' loaded successfully."}

@router.post("/reset")
def reset_database():
    db.clear_all()
    return {"message": "FactMesh database reset successfully."}
