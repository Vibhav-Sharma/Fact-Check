import re
from typing import Tuple, Optional
from ..schemas import TimePeriod

class ValueNormalizer:
    """Normalizes numbers, units, currencies, and time periods into comparable canonical forms."""

    MULTIPLIERS = {
        'k': 1e3,
        'thousand': 1e3,
        'lakh': 1e5,
        'lakhs': 1e5,
        'm': 1e6,
        'mn': 1e6,
        'million': 1e6,
        'millions': 1e6,
        'cr': 1e7,
        'crore': 1e7,
        'crores': 1e7,
        'b': 1e9,
        'bn': 1e9,
        'billion': 1e9,
        'billions': 1e9,
        't': 1e12,
        'trillion': 1e12
    }

    @classmethod
    def parse_numeric_value(cls, raw: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Extract numeric float and standardized unit from raw string.
        Examples:
          "$10 million" -> (10000000.0, "USD")
          "₹7,241 Cr" -> (72410000000.0, "INR")
          "8.2%" -> (8.2, "%")
          "740 million shipments" -> (740000000.0, "shipments")
        """
        if not raw:
            return None, None

        clean = raw.replace(',', '').strip()

        # Check percentage
        pct_match = re.search(r'([+-]?\d+(?:\.\d+)?)\s*(?:%|percent|percentage)', clean, re.IGNORECASE)
        if pct_match:
            return float(pct_match.group(1)), "%"

        # Check currency prefix/suffix
        currency = None
        if re.search(r'(\$|usd|dollar)', clean, re.IGNORECASE):
            currency = "USD"
        elif re.search(r'(₹|rs\.?|inr|rupee)', clean, re.IGNORECASE):
            currency = "INR"

        # Search for number and multiplier
        num_pattern = r'([+-]?\d+(?:\.\d+)?)\s*([a-zA-Z]+)?'
        matches = re.findall(num_pattern, clean)
        if not matches:
            return None, currency

        for num_str, suffix in matches:
            try:
                base_num = float(num_str)
                mult = 1.0
                suffix_lower = (suffix or "").lower()
                
                # Check multiplier
                for word, factor in cls.MULTIPLIERS.items():
                    if suffix_lower == word or suffix_lower.startswith(word):
                        mult = factor
                        break

                total_val = base_num * mult
                unit = currency or (suffix if suffix and mult == 1.0 else "units")
                return total_val, unit
            except ValueError:
                continue

        return None, currency

    @classmethod
    def parse_time_period(cls, raw: str) -> TimePeriod:
        """
        Parse and canonicalize time periods such as FY2024, 2024-25, Q4 FY24, CY2023.
        """
        clean = raw.strip()
        
        # Indian Fiscal Year pattern (e.g. 2024-25, FY24, FY2024, FY 2023-24)
        fy_match = re.search(r'(?:fy|fiscal\s*year)?\s*20?(\d{2})[-–]?(\d{2})?', clean, re.IGNORECASE)
        if fy_match:
            y1 = int(fy_match.group(1))
            y2 = int(fy_match.group(2)) if fy_match.group(2) else y1
            full_year = 2000 + (y2 if y2 >= 10 else y1)
            return TimePeriod(
                raw=clean,
                normalized_year=full_year,
                period_type="fiscal_year",
                normalized_start=f"{full_year-1}-04-01",
                normalized_end=f"{full_year}-03-31"
            )

        # Standalone Year (e.g. 2024, 2025)
        year_match = re.search(r'\b(19\d\d|20\d\d)\b', clean)
        if year_match:
            yr = int(year_match.group(1))
            return TimePeriod(
                raw=clean,
                normalized_year=yr,
                period_type="calendar_year",
                normalized_start=f"{yr}-01-01",
                normalized_end=f"{yr}-12-31"
            )

        # Fallback
        return TimePeriod(raw=clean)
