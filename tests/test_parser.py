import unittest
from pathlib import Path
from factmesh.ingestion.pdf_parser import PDFParser

class TestPDFParser(unittest.TestCase):
    def test_delhivery_parser(self):
        sample_pdf = Path("starter-datasets/delhivery/03-delhivery-q4-fy24-earnings-presentation.pdf")
        if not sample_pdf.exists():
            self.skipTest("Starter dataset PDF not found")

        parser = PDFParser(sample_pdf)
        meta = parser.get_metadata()
        self.assertEqual(meta["page_count"], 27)

        pages = parser.extract_pages(max_pages=5)
        self.assertEqual(len(pages), 5)
        self.assertEqual(pages[0]["page_number"], 1)
        self.assertTrue(len(pages[0]["text"]) > 0)

if __name__ == "__main__":
    unittest.main()
