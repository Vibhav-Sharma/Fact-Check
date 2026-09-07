import unittest
from factmesh.extraction.normalizer import ValueNormalizer

class TestNormalizer(unittest.TestCase):
    def test_numeric_units(self):
        val, unit = ValueNormalizer.parse_numeric_value("$10 million")
        self.assertEqual(val, 10000000.0)
        self.assertEqual(unit, "USD")

        val2, unit2 = ValueNormalizer.parse_numeric_value("₹7,241 Cr")
        self.assertEqual(val2, 72410000000.0)
        self.assertEqual(unit2, "INR")

        val3, unit3 = ValueNormalizer.parse_numeric_value("8.2%")
        self.assertEqual(val3, 8.2)
        self.assertEqual(unit3, "%")

    def test_time_periods(self):
        tp1 = ValueNormalizer.parse_time_period("FY2024")
        self.assertEqual(tp1.normalized_year, 2024)
        self.assertEqual(tp1.period_type, "fiscal_year")

        tp2 = ValueNormalizer.parse_time_period("2024-25")
        self.assertEqual(tp2.normalized_year, 2025)

        tp3 = ValueNormalizer.parse_time_period("In 2023")
        self.assertEqual(tp3.normalized_year, 2023)

if __name__ == "__main__":
    unittest.main()
