from typing import List, Dict, Any

class PageChunker:
    """Chunks pages into context windows while prioritizing pages with factual density."""

    def __init__(self, window_size: int = 2, overlap: int = 0):
        self.window_size = window_size
        self.overlap = overlap

    def filter_high_signal_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter for pages that contain substantive content and quantitative/factual signals."""
        high_signal = []
        for p in pages:
            # Skip empty pages or pages with very few lines
            if p["line_count"] < 4:
                continue
            # Keep pages with substantive text or numeric data
            if p["has_numeric_data"] or len(p["clean_text"]) > 250:
                high_signal.append(p)
        return high_signal

    def create_chunks(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group pages into windows for extraction."""
        chunks = []
        if not pages:
            return chunks

        i = 0
        step = max(1, self.window_size - self.overlap)
        while i < len(pages):
            window = pages[i:i + self.window_size]
            combined_text = "\n\n--- PAGE BREAK ---\n\n".join([
                f"[PAGE {p['page_number']}]\n{p['clean_text']}" for p in window
            ])
            page_numbers = [p["page_number"] for p in window]
            chunks.append({
                "chunk_id": f"pages_{min(page_numbers)}_to_{max(page_numbers)}",
                "page_numbers": page_numbers,
                "text": combined_text,
                "raw_pages": window
            })
            i += step
        return chunks
