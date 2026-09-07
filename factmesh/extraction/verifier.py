import re
import difflib
from typing import Tuple, Optional
from ..schemas import Evidence

class EvidenceGroundingVerifier:
    """
    Verifies that extracted facts are strictly grounded to source text.
    Rejects or flags facts with fabricated, hallucinated, or unlocatable quotes.
    """

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize whitespace and lowercase for robust fuzzy search."""
        return re.sub(r'\s+', ' ', text).strip().lower()

    def verify_quote(self, quote: str, page_text: str, page_number: int) -> Tuple[bool, float, Optional[int], Optional[int]]:
        """
        Check if verbatim quote exists in the page text.
        
        Returns:
            (is_verified, score, char_start, char_end)
        """
        if not quote or not page_text:
            return False, 0.0, None, None

        clean_quote = quote.strip()
        
        # 1. Direct substring check in raw text
        if clean_quote in page_text:
            start = page_text.index(clean_quote)
            end = start + len(clean_quote)
            return True, 1.0, start, end

        # 2. Normalized whitespace check
        norm_quote = self._normalize(clean_quote)
        norm_page = self._normalize(page_text)

        if norm_quote in norm_page:
            # Locate approximate character offsets in page_text
            pattern = re.escape(norm_quote).replace(r'\ ', r'\s+')
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return True, 0.98, match.start(), match.end()
            return True, 0.95, 0, len(page_text)

        # 3. Fuzzy match using SequenceMatcher across sliding window
        matcher = difflib.SequenceMatcher(None, norm_quote, norm_page)
        match = matcher.find_longest_match(0, len(norm_quote), 0, len(norm_page))
        if match.size > 0:
            coverage = match.size / max(len(norm_quote), 1)
            if coverage >= 0.80:
                return True, round(coverage, 2), None, None

        return False, 0.0, None, None

    def build_evidence(self, raw_quote: str, page_text: str, page_number: int) -> Evidence:
        """Construct a validated Evidence object with verification scores."""
        verified, score, start, end = self.verify_quote(raw_quote, page_text, page_number)
        return Evidence(
            verbatim_quote=raw_quote.strip(),
            page_number=page_number,
            char_start=start,
            char_end=end,
            verified=verified,
            verification_score=score
        )
