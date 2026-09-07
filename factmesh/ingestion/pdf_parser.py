from pathlib import Path
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import re

class PDFParser:
    """Structure-aware PDF parser utilizing PyMuPDF for fast page extraction."""

    def __init__(self, doc_path: Path):
        self.doc_path = Path(doc_path)
        if not self.doc_path.exists():
            raise FileNotFoundError(f"PDF document not found at: {self.doc_path}")

    def get_metadata(self) -> Dict[str, Any]:
        """Extract basic PDF metadata and page count."""
        doc = fitz.open(self.doc_path)
        meta = {
            "page_count": len(doc),
            "title": doc.metadata.get("title") or self.doc_path.stem,
            "author": doc.metadata.get("author") or "",
            "file_size": self.doc_path.stat().st_size
        }
        doc.close()
        return meta

    def extract_pages(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Extract structured page text with physical page numbering (1-indexed).
        
        Returns:
            List of dicts: [
                {
                    "page_number": int,
                    "text": str,
                    "clean_text": str,
                    "line_count": int,
                    "has_numeric_data": bool
                }
            ]
        """
        pages_data = []
        doc = fitz.open(self.doc_path)
        total_pages = len(doc)
        limit = min(total_pages, max_pages) if max_pages else total_pages

        for idx in range(limit):
            page = doc[idx]
            raw_text = page.get_text("text")
            
            # Simple cleanup for analysis while keeping raw_text intact for grounding
            lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)
            
            # Check if page contains numbers / metrics
            has_numeric = bool(re.search(r'\d+(?:[.,]\d+)?\s*(?:%|cr|crore|million|billion|usd|inr|\$|rs|₹)', clean_text, re.IGNORECASE))
            
            pages_data.append({
                "page_number": idx + 1,
                "text": raw_text,
                "clean_text": clean_text,
                "line_count": len(lines),
                "has_numeric_data": has_numeric
            })

        doc.close()
        return pages_data
