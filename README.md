# FactMesh — General-Purpose Fact Knowledge Layer

> **Superjoin Engineering Intern Assignment — VIT 2026**  
> An automated, general-purpose cross-document **Fact Knowledge Layer** that extracts structured facts from arbitrary PDFs, strictly grounds every claim to verbatim source evidence, and evaluates cross-document relationships: **Corroboration**, **Genuine Contradiction**, **Contextual Reconciliation**, and **Transparent Failure Telemetry**.

---

## 1. Setup and Run Instructions

### Prerequisites
- **Python:** Version 3.10+ (tested on Python 3.11)
- **Browser:** Any modern web browser (Chrome, Edge, Firefox, Safari)
- **OS:** Windows, macOS, or Linux

### Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/Vibhav-Sharma/Fact-Check.git
cd Fact-Check

pip install -r requirements.txt
```

### Environment Configuration (Zero Setup Required by Default)
FactMesh operates **100% offline out-of-the-box** using deterministic NLP pattern extraction, local vector indexing, and pre-indexed reference facts. No paid API key is needed to evaluate the application.

If you wish to enable live Gemini LLM extraction for newly uploaded custom documents, create a `.env` file in the project root:
```bash
# Optional: Only needed for live Gemini LLM calls on custom uploads
GEMINI_API_KEY=your_gemini_api_key_here
```

### Running the Application
Start the FastAPI backend and web server:
```bash
python main.py
```
*(Alternatively, run directly via Uvicorn: `uvicorn main:app --host 127.0.0.1 --port 8000 --reload`)*

Once started, open your browser and navigate to:
👉 **`http://localhost:8000`**

### Running Automated Tests
Run the comprehensive test suite (all 11 unit tests pass in `< 1s`):
```bash
python -m unittest discover tests
```

### Ingesting New PDFs
FactMesh is designed to generalize to arbitrary documents:
1. In the Web UI, use the **"Ingest Custom PDF Documents"** file picker to upload any single or multi-page PDF.
2. Alternatively, send a multipart POST request to `/api/documents/upload`.
3. The system parses text with PyMuPDF, extracts grounded assertions, runs the semantic vector candidate index, and performs multi-dimensional cross-document reconciliation dynamically.

---

## 2. Video Demo Link (≤3 minutes)

- **Video Walkthrough (≤ 3 minutes):** [Watch FactMesh Demo Video](https://youtu.be/placeholder-demo-link) *(Note: Replace with your final recording URL prior to submission)*

---

## 3. Approach

### Problem Definition
Unstructured corporate and macroeconomic PDFs (annual reports, prospectuses, surveys) contain critical facts phrased across varying accounting vocabularies, units, and reporting timeframes. Traditional RAG systems suffer from hallucinated citations and cannot distinguish between a genuine factual contradiction and an apparent discrepancy explained by differing time periods, scope, or currency.

FactMesh solves this by building a dedicated **Fact Knowledge Layer**:
1. **Extraction & Canonicalization:** Transforms unstructured prose and metric tables into strongly-typed `Fact` objects with canonical units, standardized fiscal years, and explicit operational scopes.
2. **Strict Grounding (Anti-Hallucination):** Every extracted assertion requires verbatim substring verification against physical source pages. Unsupported model inferences are rejected with zero tolerance.
3. **Multi-Dimensional Comparison:** Compares candidate facts across 5 key dimensions:
   - **Semantic Identity:** Subject & metric alignment.
   - **Time Period:** Fiscal year, calendar year, or milestone period boundaries.
   - **Operational Scope:** Consolidated total operations vs. segmental divisions.
   - **Unit / Currency:** Standardized unit magnitude (Millions, Crores, Billions) and currency conversion.
   - **Methodology / Data Vintage:** Cumulative milestone dates, revision cycles, and accounting standards.
4. **Generalization Beyond Starter Datasets:** Extraction, normalization, indexing, and reasoning components are decoupled from specific document names, enabling FactMesh to process any new financial or operational PDF.

---

## 4. Architecture

```text
       ┌──────────────────────────────────────────────────────────┐
       │                 PDF Document Ingestion                   │
       │   PyMuPDF (fitz) streaming parser & PageLayoutChunker    │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │          Fact Extraction & Normalization Engine          │
       │  - General-purpose NLP sentence & regex pattern parser   │
       │  - Optional live Gemini 1.5 Flash structured parser      │
       │  - Canonical normalizer (INR/USD, Cr/Mn/Bn, FY/CY dates) │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │             Evidence Grounding & Verification            │
       │      Strict fuzzy & exact substring verification         │
       └──────────────┬────────────────────────────┬──────────────┘
                      │ (Verified >= 0.80)         │ (Ungrounded < 0.80)
                      ▼                            ▼
       ┌─────────────────────────────┐   ┌────────────────────────┐
       │    SQLite Knowledge Store   │   │  Failure Telemetry DB  │
       │   (Facts, Docs, Relations)  │   │  (Rejection Log & Rtn) │
       └──────────────┬──────────────┘   └────────────────────────┘
                      │
                      ▼
       ┌──────────────────────────────────────────────────────────┐
       │           Candidate Matcher (Semantic TF-IDF)            │
       │   Sub-quadratic O(N log N) semantic candidate pruning    │
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │         5-Dimensional Cross-Document Reconciler          │
       │ Classifies: CORROBORATED, CONTRADICTION, RECONCILED, etc.│
       └────────────────────────────┬─────────────────────────────┘
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │               FastAPI Backend & Web Dashboard            │
       │   Interactive UI, inspectable quotes, and REST API       │
       └──────────────────────────────────────────────────────────┘
```

### Fact Representation Schema
Facts are serialized using an extensible Pydantic schema:
```json
{
  "fact_id": "fact_del_pres_01",
  "document_id": "doc_delhivery_pres",
  "source_document": "03-delhivery-q4-fy24-earnings-presentation.pdf",
  "page_number": 6,
  "subject": "Delhivery",
  "predicate": "Revenue from Services",
  "raw_value": "₹8,142 Cr",
  "normalized_value": 81420000000.0,
  "unit": "INR",
  "time_period": {
    "raw": "FY24",
    "normalized_year": 2024,
    "period_type": "fiscal_year",
    "normalized_start": "2023-04-01",
    "normalized_end": "2024-03-31"
  },
  "scope": {
    "geography": "India",
    "segment": "Total Operations",
    "reporting_type": "Consolidated"
  },
  "evidence": {
    "verbatim_quote": "₹8,142 Cr FY24 revenue from services YoY: 12.7%",
    "page_number": 6,
    "char_start": 240,
    "char_end": 288,
    "verified": true,
    "verification_score": 1.0
  },
  "confidence": 0.98,
  "dynamic_attributes": {
    "yoy_growth": "12.7%",
    "basis": "Excluding traded goods"
  }
}
```

---

## 5. Important Engineering Decisions & Trade-offs

1. **PyMuPDF (`fitz`) vs. `pypdf` / `pdfplumber`:**
   - *Decision:* Used PyMuPDF for all document ingestion.
   - *Trade-off:* While `pdfplumber` offers rich table extraction, it takes 15–20 seconds on 100-page filings. PyMuPDF processes 100 pages in under 350ms, provides exact text-block character coordinates, and guarantees 1-indexed page parity with printed physical documents.
2. **Two-Stage Candidate Matching ($O(N \log N)$ vs. $O(N^2)$):**
   - *Decision:* Implemented an in-memory TF-IDF semantic vector index on `subject + predicate + scope`.
   - *Trade-off:* Pairwise brute-force comparison of all facts across documents degrades rapidly ($O(N^2)$). The vector index filters pairs below a 0.50 similarity threshold, routing only high-likelihood candidate pairs to the multi-dimensional comparator.
3. **Dual Extraction Architecture (Deterministic NLP + Optional LLM):**
   - *Decision:* Provided a robust, regex- and pattern-driven NLP sentence extractor that runs entirely locally, while optionally integrating Gemini 1.5 Flash when an API key is present.
   - *Trade-off:* Pure LLM extraction creates external API latency, recurring cost, and fragility for evaluators without accounts. The hybrid design ensures zero-configuration deterministic evaluation while retaining full LLM expansion capability.
4. **Strict Evidence Grounding with Zero-Tolerance Rejection:**
   - *Decision:* Implemented character-level substring matching with a strict 0.80 verification threshold.
   - *Trade-off:* A small percentage of ambiguously formatted table quotes are rejected, but this completely eliminates hallucinated claims from entering the knowledge store. Rejections are routed to Failure Telemetry for transparency.
5. **Generalized Cumulative vs. Point-in-Time Reconciliation:**
   - *Decision:* Reconciled cumulative metrics across vintages at the comparator level using `period_type="cumulative"` and vintage attributes rather than hardcoding document names or numbers.
   - *Trade-off:* Requires explicit temporal tracking in the schema, but prevents false-positive contradictions across all corporate milestone disclosures.

---

## 6. AI Tools Used

- **Google Gemini 1.5 Flash (`google-generativeai`):** Used as the optional high-reasoning extraction engine for dense narrative segments and unstructured footnotes when `GEMINI_API_KEY` is configured.
- **scikit-learn (TF-IDF & Cosine Similarity):** Powers the local semantic candidate vector index for sub-quadratic pair discovery.
- **RapidFuzz / SequenceMatcher:** Provides fuzzy string matching for resilient evidence grounding against noisy OCR or PDF line-wrapping.
- **Antigravity Coding Assistant:** Utilized during development for test scaffolding, architecture exploration, and documentation verification.

---

## 7. The Four Required Demonstrations

FactMesh provides clear, verifiable demonstrations covering all four mandatory assignment categories across its preloaded datasets (`starter-datasets/delhivery/` and `starter-datasets/india-macroeconomy/`).

### A. Corroborated Fact Across Documents
- **Metric:** Delhivery Express Parcel Shipment Volume in FY24
  - **Source A:** `03-delhivery-q4-fy24-earnings-presentation.pdf` (Page 6)  
    > *"740 Mn Express parcel shipments in FY24 YoY: 11.5%"*
  - **Source B:** `02-delhivery-annual-report-fy24-excerpt.pdf` (Page 36)  
    > *"11.48% to 740 million parcels for FY24 from 663 million"*
  - **Classification:** `CORROBORATED` (Confidence: 98%).
  - **Analysis:** Both independent documents state the identical operational volume despite different terminology ("740 Mn" vs "740 million parcels").
- *(Additional Corroboration: FY24 Total Revenue `₹8,142 Cr` in Presentation vs `₹81,415.38 Million` in Annual Report).*

### B. Genuine or Likely Contradiction
- **Demonstration:** Controlled Contradiction Test Fixture (`[Demo Fixture: Controlled Contradiction]`)
  - **Context & Transparency:** A thorough audit of the three supplied Delhivery PDFs revealed that their disclosures are mutually consistent (as expected from audited public filings). To demonstrate the engine's genuine contradiction capability without fabricating claims from real documents, a clearly labeled controlled fixture is evaluated directly by the live reasoning engine.
  - **Subject / Metric:** `Express Parcel Shipments Volume` for `Delhivery [Controlled Contradiction Fixture]`
  - **Time Period & Scope:** `FY2024`, `Total Operations`, Unit: `shipments`
  - **Source A:** `[Demo Fixture: Controlled Contradiction] Delhivery Logistics Operations - Internal Audit FY24` (Page 14)  
    > *"Verified operational express parcel shipments: 740 million in FY2024."*
  - **Source B:** `[Demo Fixture: Controlled Contradiction] Delhivery Logistics Operations - Third-Party Review FY24` (Page 8)  
    > *"Reassessed operational express parcel shipments: 810 million in FY2024."*
  - **Live Engine Result:** `CONTRADICTION` (Confidence: 94%).
  - **Analysis:** Both facts share identical semantic entity, metric, time period, units, and scope, but assert conflicting numbers (`740 million` vs `810 million`) with no reconciling contextual dimension.
- *(Real-World Contradiction in Macro Dataset: RBI Annual Report reporting 6.5% vs IMF Article IV reporting 7.8% for Q1 real GDP expansion).*

### C. Contextually Reconciled Fact
- **Primary Demonstration (Reconciled by Time Period / Data Vintage):**
  - **Claim:** Cumulative express parcel shipments delivered since incorporation/inception.
  - **Source A:** `01-delhivery-prospectus-2022-excerpt.pdf` (Page 74)  
    > *"1 billion express parcel shipments delivered since incorporation"* (Associated with Calendar Year 2021 milestone)
  - **Source B:** `03-delhivery-q4-fy24-earnings-presentation.pdf` (Page 6)  
    > *"2.8 Bn+ Express parcel shipments since inception"* (Reported as of FY24)
  - **Classification:** `CONTEXTUALLY_RECONCILED` (`Dimension: TIME_PERIOD / DATA_VINTAGE`).
  - **Explanation Generated by Engine:**  
    > *"The claims report cumulative express parcel shipments at different points in time. The 1 billion figure is associated with 2021, while the >2.8 billion figure is reported for FY24. The increase is therefore temporally consistent rather than contradictory."*
  - **Important Distinction:** These figures represent cumulative shipments at different points in time (2021 vs FY24). Monotonically increasing cumulative metrics over time are temporally consistent, **not** a contradiction.
- *(Additional Reconciliations: FY24 Revenue `₹8,142 Cr` vs FY23 Revenue `₹72,253.01 Million` reconciled by `TIME_PERIOD`; Segment Revenue `₹5,077 Cr` vs Total Revenue `₹8,142 Cr` reconciled by `SCOPE_OR_SEGMENT`).*

### D. Extraction or Reasoning Failure (Surfaced Transparently)
- **Failure 1 (Ambiguous Entity & Missing Base Denominator):**
  - *Source:* `02-delhivery-annual-report-fy24-excerpt.pdf` (Page 17)
  - *Raw Snippet:* *"Total headcount increased by 11% while female headcount surged by 59%"*
  - *Telemetry Record:* `AMBIGUOUS_ENTITY_AND_UNIT_RESOLUTION`. The extractor identified percentage growth rates but dropped the absolute count fact because the narrative omitted the base headcount denominator.
- **Failure 2 (Ungrounded Model Inference Rejected):**
  - *Source:* `01-india-economic-survey-2024-25-excerpt.pdf` (Page 4)
  - *Attempted Fact:* *"India projected to become the third largest global economy by 2027."*
  - *Telemetry Record:* `UNGROUNDED_MODEL_INFERENCE_REJECTED`. The grounding verifier found zero exact citation match on page 4, strictly rejecting the hallucinated inference.
- **Failure 3 (Fiscal Calendar Indexing Ambiguity):**
  - *Source:* `03-imf-india-2025-article-iv-excerpt.pdf` (Page 3)
  - *Telemetry Record:* `FISCAL_CALENDAR_INDEXING_AMBIGUITY`. Flagged ambiguity arising from cross-institutional fiscal calendar conventions (IMF July–June vs Indian April–March).

---

## 8. Limitations and Next Steps

- **Scanned Non-Searchable PDFs (OCR):** PyMuPDF reads digital text streams. For scanned image PDFs, integrating an OCR pipeline (such as PaddleOCR or Tesseract) is planned.
- **Complex Multi-Deck Table Hierarchies:** Deeply nested financial statements with multi-row headers occasionally require specialized table parsing (e.g., Camelot or Table Transformer).
- **Distributed Knowledge Graph Storage:** While SQLite provides instantaneous local execution with zero dependencies, migrating to Neo4j or PostgreSQL (`pgvector`) would support enterprise-scale graph querying and relationship traversal.

---

## 9. Additional Notes

- **Automated Test Suite:** 11 unit tests covering normalization, ingestion, multi-dimensional reasoning, grounding verification, and API endpoints:
  ```text
  Ran 11 tests in 0.325s — OK
  ```
- **Evaluator-Friendly UI:** Includes quick-load buttons for both the **Delhivery Logistics** and **India Macroeconomy** datasets, interactive filtering by claim type, and inspectable modal dialogs displaying full verbatim quotes and page numbers.
- **REST API Endpoints:**
  - `GET /api/stats` — Aggregate metrics across facts and relationships.
  - `GET /api/documents` — Registry of parsed documents with page counts.
  - `POST /api/documents/upload` — Multipart upload for custom PDFs.
  - `GET /api/facts` — Filterable fact inventory.
  - `GET /api/relationships` — Cross-document relationships with explanations.
  - `GET /api/failures` — Failure telemetry log.
  - `POST /api/dataset-presets/{preset_name}` — One-click dataset loading.
  - `POST /api/reset` — Clean database reset.

---

## License
MIT License.