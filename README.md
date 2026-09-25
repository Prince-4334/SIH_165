# SIF SENTINEL
### AI-Powered SIF Precursor Intelligence Platform
**Tagline:** *"From Safety Reports to Actionable SIF Intelligence"*

---

## 1. Executive Summary & Problem Solved

Traditional safety reporting systems in the energy and oil & gas sectors ingest thousands of Unsafe Act / Unsafe Condition (UA/UC) reports, near-miss observations, and incident logs. However, **over 80% of these records describe routine minor issues** (housekeeping, minor slips/trips), causing critical high-consequence **SIF (Serious Injury & Fatality) precursors** to remain buried in the noise.

Decades of modern safety research (Campbell Institute, Dekker, Conklin) have proven that fatalities and serious injuries have fundamentally distinct root causes from minor incidents. SIF events require the presence of **hazardous energy** coupled with a **compromised or omitted primary barrier**.

**SIF Sentinel** is a purpose-built industrial HSE intelligence prototype calibrated for **Oil India Limited (OIL)** asset environments. It ingests free-text safety reports and uses transparent, deterministic NLP and safety ontology mapping to identify SIF precursors, map them to IOGP Life-Saving Rules, extract barrier breakdowns, explain why they were flagged, and recommend corrective actions before fatal loss events occur.

> **Positioning:** AI-assisted screening and decision support for HSE teams.  
> *This tool assists HSE review; it does not replace it.*

---

## 2. Core Demo Flow

```
SAFETY REPORT (UA/UC / Near-Miss / Incident)
   │
   ▼
AI/NLP SCREENING & ONTOLOGY ENGINE
   │
   ▼
SIF POTENTIAL CLASSIFICATION (HIGH / MEDIUM / LOW / NON-SIF)
   │
   ▼
IOGP LIFE-SAVING RULE MAPPING (Energy Isolation, Working at Height, Hot Work, etc.)
   │
   ▼
HAZARD + BARRIER FAILURE EXTRACTION
   │
   ▼
EXPLAINABLE RATIONALE & EXTRACTED EVIDENCE
   │
   ▼
RECOMMENDED HSE CORRECTIVE ACTION
   │
   ▼
HSE GOVERNANCE GATE & DISPOSITION (Reviewed / Escalated / Dismissed)
   │
   ▼
REAL SQLITE PERSISTENCE (`sif_sentinel.db`)
   │
   ▼
EXECUTIVE DASHBOARD & RECURRING PRECURSOR PATTERN UPDATES
```

---

## 3. Technology Stack

- **Application Framework:** Streamlit (customized with high-contrast industrial CSS tokens inspired by Intelex, Cority, Enablon, VelocityEHS)
- **Data Analytics & Transformations:** Pandas, NumPy, Scikit-learn
- **Data Visualizations:** Plotly Interactive Visuals (Donut, Pareto, Heatmap, Horizontal Bar)
- **Safety Screening & NLP Engine:** Deterministic rule engine, regex phrase extractors, and IOGP Life-Saving Rule taxonomy
- **Persistence Layer:** SQLite (`sif_sentinel.db`) with real-time KPI re-computation
- **Deployment Mode:** 100% offline, air-gapped, open-source — zero external API tokens or internet dependencies required

---

## 4. Visual Identity & Contrast System

- **Industrial Base:** Deep Graphite / Steel Navy (`#0F172A`, `#1E293B`)
- **Primary Accent:** Slate Teal / Steel Blue (`#0369A1`)
- **Safety Status Signals:**
  - High SIF Precursor Alert Red: `#DC2626`
  - Medium / Review Warning Amber: `#D97706`
  - Low / Non-SIF Safety Green: `#16A34A`
  - Neutral Slate / Info: `#475569`
- **Canvas:** Crisp neutral off-white (`#F8FAFC`, `#FFFFFF`)
- **Strict Accessibility:** Every custom CSS rule setting a background explicitly defines text `color` in the same rule, ensuring 100% contrast in default and hovered states.
- **Monochrome Icons:** Clean industrial badges with zero decorative emojis (the 🛡️ in the sidebar header is the only emoji glyph in the platform).
- **Mandatory Footer:** Plain-text disclaimer without colored banner:
  *"AI-assisted screening for HSE review — not a final safety decision."*

---

## 5. Live SQLite Dataset Benchmark

The platform is pre-seeded with **1,284 synthetic safety reports** reflecting oilfield operating facilities (Duliajan Central Gas Plant, Digboi Refinery Complex, Moran Oil Field Asset, Naharkatiya Pumping Station, Jorhat Exploration Camp, Kumchai Production Terminal):

| Metric | Target Benchmark | Live SQLite State |
| :--- | :---: | :---: |
| **Total Reports** | 1,284 | **1,284** |
| **High SIF Precursors** | 286 | **286** |
| **Precursor Rate** | 22.3% | **22.3%** |
| **HSE Review Pending** | 47 | **47** |
| **HSE Confirmed SIF** | 239 | **239** |

*Note: Analyzing and saving a new report immediately increments Total Reports by +1 in real-time, visible across all pages upon save.*

---

## 6. Section 13 Test Scenarios Suite

SIF Sentinel satisfies all 6 mandatory benchmark scenarios:

1. **Test 1 — Energy Isolation (Flange / Trapped Pressure):**
   - *Input:* Crude transfer line maintenance; section isolated but zero pressure not verified before loosening flange; trapped pressure released; nobody was injured.
   - *Result:* **HIGH SIF (Score: 90/100)** | Rule: *Energy Isolation* | Failure: *Zero-energy verification not completed*.
   - *Validation:* "Nobody was injured" correctly did **not** downgrade the high potential consequence.

2. **Test 2 — Working at Height (Missing Guardrail):**
   - *Input:* Scaffold inspection on distillation column at 6 meters; guardrail section missing; no alternative fall protection used.
   - *Result:* **HIGH SIF (Score: 92/100)** | Rule: *Working at Height* | Failure: *Fall protection barrier failure*.

3. **Test 3 — Hot Work (Welding Near Residue / No Gas Test):**
   - *Input:* Welding pipe support near process line containing hydrocarbon residue; gas testing not completed before welding started.
   - *Result:* **HIGH SIF (Score: 88/100)** | Rule: *Hot Work* | Failure: *Gas testing/area verification failure*.

4. **Test 4 — Confined Space (Vessel Entry Without Gas Test):**
   - *Input:* Technician held permit but atmospheric testing not performed; entered vessel before stopped by standby person.
   - *Result:* **HIGH SIF (Score: 94/100)** | Rule: *Confined Space* | Failure: *Atmospheric gas testing omitted before vessel entry*.

5. **Test 5 — Low Risk (Housekeeping / Loose Papers):**
   - *Input:* Loose papers found near control room entrance; removed immediately.
   - *Result:* **LOW / NON-SIF (Score: 15/100)** | Rule: *None / General Safety* | Failure: *None identified / Minor housekeeping issue*.

6. **Test 6 — Successful Barrier (LOTO & Zero Energy Verified):**
   - *Input:* Electrical supply to pump isolated and locked out; technician tested equipment and confirmed zero energy before maintenance.
   - *Result:* **LOW / NON-SIF (Score: 18/100)** | Rule: *Energy Isolation* | Failure: *None identified (Barrier successfully applied)*.
   - *Validation:* Distinguishes hazardous activities with *functioning barriers* from barrier failures.

---

## 7. How to Run Locally

### Prerequisites
- Python 3.10 to 3.13 installed.

### Setup and Launch
```bash
# 1. Clone repository
git clone <REPO_URL>
cd SIH_2026_IH

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch SIF Sentinel
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Run Test Suites
```bash
# Verify all Section 13 test scenarios
python test_scenarios.py

# Run end-to-end integration and HSE governance tests
python test_integration.py

# Run Section 23 final QA test suite
python test_qa_suite.py
```

---

## 8. Application Navigation

1. **Overview:** Live KPIs (Total Reports, SIF-Potential, SIF Rate, Pending Review), SIF Distribution donut, IOGP Rule bar chart, Precursors by Activity, SIF Potential by Asset Site, Barrier Failure Breakdown, and Recent High-Priority Reports table.
2. **Analyze Report (Hero Feature):** Narrative input with quick-load demo buttons, minimum-length validation, instant loading state, comprehensive analysis card, and HSE review disposition form writing to SQLite.
3. **SIF Reports:** Filterable audit register with 3-part structured inspection and persistent Review Status modification (`Reviewed`, `Escalated`, `Dismissed`, `Pending Review`).
4. **Precursor Patterns:** Live-calculated systemic insight cards, Pareto barrier failure analysis, and activity-rule co-occurrence matrix.
5. **Life-Saving Rules:** Standard IOGP rules compliance breakdown with conversion ratios and filtered records.
6. **About:** Theoretical background on SIF precursor screening vs Heinrich's triangle, IOGP framework, deterministic scoring rationale, and decision support boundaries.

---

## 9. Regulatory & Legal Disclaimers

- **AI-assisted screening for HSE review — not a final safety decision.**
- **Prototype scoring logic — requires validation against historical OIL data.**
- **AI-assisted recommendation — HSE validation required.**
- The platform uses synthetic demonstration data calibrated for hackathon presentation and does not connect to real proprietary OIL systems.
- The SIF Priority Score (0–100) represents triage urgency, **not** a mathematical probability of fatality or injury.
- The system surfaces precursor patterns to support human safety experts and does not predict accidents or make final safety decisions.

---

## 10. Team Information

- **Team Name:** SIF Sentinel AI Team
- **Hackathon:** Smart India Hackathon (SIH 2026 / Internal Hackathon)
- **Problem Statement:** AI-Powered SIF Precursor Intelligence Platform for OIL Assets
