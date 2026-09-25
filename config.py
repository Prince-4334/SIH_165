"""
SIF SENTINEL - Configuration and Industrial Visual Design System
AI-Powered SIF Precursor Intelligence Platform
"""

APP_NAME = "SIF SENTINEL"
APP_SUBTITLE = "AI-Powered SIF Precursor Intelligence Platform"
APP_TAGLINE = "From Safety Reports to Actionable SIF Intelligence"
APP_DISCLAIMER = "AI-assisted screening for HSE review — not a final safety decision."
SCORING_DISCLAIMER = "Prototype scoring logic — requires validation against historical OIL data."
RECOMMENDATION_DISCLAIMER = "AI-assisted recommendation — HSE validation required."

# ==============================================================================
# INDUSTRIAL EHS COLOR TOKENS (Intelex / Cority / VelocityEHS inspired)
# ==============================================================================
COLORS = {
    # Industrial base & canvas
    "base_dark": "#0F172A",       # Deep graphite / steel navy
    "sidebar_bg": "#1E293B",      # Slate navy for sidebar & headers
    "card_dark": "#1E293B",       # Dark container fill
    "canvas_light": "#F8FAFC",    # Neutral off-white content canvas
    "card_bg": "#FFFFFF",         # Pure card background
    "border_light": "#E2E8F0",    # Crisp boundary lines
    "border_subtle": "#CBD5E1",   # Medium boundary
    
    # Primary & Secondary Accents
    "primary": "#0369A1",         # Muted steel blue (not neon)
    "primary_dark": "#075985",    # Darker steel blue
    "primary_light": "#E0F2FE",   # Soft steel blue tint
    "text_primary": "#0F172A",    # High contrast slate text
    "text_secondary": "#475569",  # Technical body text
    "text_muted": "#64748B",      # Subtle metadata text
    
    # Status Safety Signals (Strict Industrial Meanings)
    "status_high": "#DC2626",     # Alert red: High SIF precursor
    "status_high_bg": "#FEF2F2",  # Red tint container
    "status_high_border": "#FCA5A5",
    
    "status_med": "#D97706",      # Warning amber: Review / Medium SIF
    "status_med_bg": "#FFFBEB",   # Amber tint container
    "status_med_border": "#FCD34D",
    
    "status_low": "#16A34A",      # Muted safety green: Low / Non-SIF
    "status_low_bg": "#F0FDF4",   # Green tint container
    "status_low_border": "#86EFAC",
    
    "status_info": "#475569",     # Neutral slate: General / Housekeeping
    "status_info_bg": "#F1F5F9",  # Slate tint container
    "status_info_border": "#CBD5E1",
}

# ==============================================================================
# IOGP LIFE-SAVING RULES (Industry standard reference list)
# ==============================================================================
IOGP_RULES = [
    "Energy Isolation",
    "Working at Height",
    "Hot Work",
    "Confined Space",
    "Line of Fire",
    "Lifting Operations",
    "Driving",
    "Work Authorization",
    "Bypassing Safety Controls",
]

# Standard activities in Oil & Gas upstream/downstream operations
OPERATIONAL_ACTIVITIES = [
    "Pipeline Maintenance",
    "Mechanical Maintenance",
    "Electrical Maintenance",
    "Hot Work / Welding",
    "Lifting Operations",
    "Confined Space Entry",
    "Excavation & Trenching",
    "Vehicle Transport",
    "Wellhead Operations",
    "Housekeeping & Routine",
]

# Representative OIL Assets & Operating Areas (Synthetic Demo Data)
OIL_SITES = [
    "Duliajan Central Gas Plant",
    "Digboi Refinery Complex",
    "Moran Oil Field Asset",
    "Naharkatiya Pumping Station",
    "Jorhat Exploration Camp",
    "Kumchai Production Terminal",
]

# ==============================================================================
# DEMO TEST SCENARIOS (From Section 13 Specification)
# ==============================================================================
DEMO_SCENARIOS = {
    "Test 1 — Energy Isolation (Flange / Trapped Pressure)": {
        "text": "During maintenance of a crude oil transfer line, the team isolated the section but did not verify zero pressure before loosening the flange. Trapped pressure was released when the flange was opened. Nobody was injured.",
        "expected_sif": "HIGH",
        "expected_rule": "Energy Isolation",
        "expected_barrier_failure": "Zero-energy verification not completed",
        "site": "Duliajan Central Gas Plant",
        "report_type": "Near-Miss",
    },
    "Test 2 — Working at Height (Missing Guardrail)": {
        "text": "During scaffold inspection on the distillation column platform at 6 meters, one section of the guardrail was missing. No alternative fall protection was being used.",
        "expected_sif": "HIGH",
        "expected_rule": "Working at Height",
        "expected_barrier_failure": "Fall protection barrier failure",
        "site": "Digboi Refinery Complex",
        "report_type": "Unsafe Condition",
    },
    "Test 3 — Hot Work (Welding Near Residue / No Gas Test)": {
        "text": "Welding pipe support bracket near a process line containing hydrocarbon residue. Gas testing had not been completed before welding started.",
        "expected_sif": "HIGH",
        "expected_rule": "Hot Work",
        "expected_barrier_failure": "Gas testing/area verification failure",
        "site": "Moran Oil Field Asset",
        "report_type": "Unsafe Act",
    },
    "Test 4 — Confined Space (Vessel Entry Without Gas Test)": {
        "text": "Technician held a permit but atmospheric testing was not performed. The worker entered the vessel before the job was stopped by the standby person.",
        "expected_sif": "HIGH",
        "expected_rule": "Confined Space",
        "expected_barrier_failure": "Gas testing failure",
        "site": "Naharkatiya Pumping Station",
        "report_type": "Near-Miss",
    },
    "Test 5 — Low Risk (Housekeeping / Loose Papers)": {
        "text": "Several loose papers were found near the entrance of the control room. They were removed immediately.",
        "expected_sif": "LOW",
        "expected_rule": "None / General Safety",
        "expected_barrier_failure": "None identified / Minor housekeeping",
        "site": "Jorhat Exploration Camp",
        "report_type": "Unsafe Condition",
    },
    "Test 6 — Successful Barrier (LOTO & Zero Energy Verified)": {
        "text": "The electrical supply to the pump was isolated and locked out. The technician tested the equipment and confirmed zero energy before starting maintenance.",
        "expected_sif": "LOW / NON-SIF",
        "expected_rule": "Energy Isolation",
        "expected_barrier_failure": "None identified",
        "site": "Duliajan Central Gas Plant",
        "report_type": "Safe Observation",
    },
}
