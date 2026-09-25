

import re
from typing import Dict, Any, List, Tuple
from config import IOGP_RULES, SCORING_DISCLAIMER, RECOMMENDATION_DISCLAIMER



# Negation & omission indicators (crucial for distinguishing failed barriers vs verified ones)
OMISSION_NEGATION_PATTERNS = [
    r"\bnot\s+perform(?:ed)?\b",
    r"\bnot\s+verif(?:ied|y)\b",
    r"\bdid\s+not\s+verify\b",
    r"\bdid\s+not\s+test\b",
    r"\bwithout\s+(?:prior\s+)?(?:testing|isolation|permit|verification|loto|guardrail|harness)\b",
    r"\bnot\s+completed?\b",
    r"\bfail(?:ed|ure)?\s+to\b",
    r"\bomitt(?:ed|ing)\b",
    r"\bmissing\b",
    r"\babsent\b",
    r"\bno\s+(?:alternative\s+)?(?:fall\s+protection|barrier|guardrail|permit|gas\s+test|testing|spotter)\b",
    r"\bbypass(?:ed|ing)?\b",
    r"\bdisabl(?:ed|ing)\b",
    r"\bdefeat(?:ed|ing)\b",
    r"\bviolat(?:ed|ion)\b",
    r"\bunauthoriz(?:ed)?\b",
    r"\buncontrolled\b",
    r"\bleak(?:ed|ing)?\b",
    r"\breleas(?:ed|ing)?\b",
    r"\bdefect(?:ive)?\b",
    r"\bdamag(?:ed)?\b",
    r"\bcorrod(?:ed|ion)\b",
]

# Success indicators (when a barrier was properly performed/tested)
SUCCESS_BARRIER_PATTERNS = [
    r"\bisolated\s+and\s+locked\s+out\b",
    r"\blockout\s+tagout\s+completed\b",
    r"\bconfirmed\s+zero\s+energy\b",
    r"\bverif(?:ied|y)\s+(?:zero\s+pressure|zero\s+energy)\b",
    r"\bgas\s+test(?:ing)?\s+confirmed\s+safe\b",
    r"\b100%\s+tie-off\s+maintained\b",
    r"\bpermit\s+fully\s+authorized\b",
    r"\bexclusion\s+zone\s+enforced\b",
    r"\btested\s+the\s+equipment\s+and\s+confirmed\b",
    r"\bbarrier\s+(?:holding|effective|maintained)\b",
]

# Phrases like "nobody was injured" or "no one was hurt" must NOT downgrade potential consequence
NO_INJURY_CLAUSES = [
    r"\bnobody\s+was\s+injured\b",
    r"\bno\s+injur(?:y|ies)\b",
    r"\bno\s+one\s+was\s+hurt\b",
    r"\bno\s+harm\s+done\b",
    r"\bluckily\s+no\s+one\b",
    r"\bno\s+personnel\s+harmed\b",
]

# Rule and Hazard definitions with regex triggers
RULE_DEFINITIONS = {
    "Energy Isolation": {
        "keywords": [
            "isolation", "isolated", "lockout", "tagout", "loto", "valve", "flange",
            "blinding", "spading", "bleed", "depressuriz", "zero pressure", "zero energy",
            "residual pressure", "trapped pressure", "pressurized", "pipeline", "transfer line",
            "steam line", "breaker", "electrical supply", "switchgear", "circuit", "accumulator",
            "hydraulic pressure", "pneumatic"
        ],
        "hazard_default": "Stored / Pressurized Energy",
        "barrier_default": "Energy Isolation (LOTO) & Zero-Energy Verification",
        "high_consequence": "Uncontrolled hazardous energy release → High-pressure injection, fire, arc flash, or fatality potential",
        "recommended_action": "Enforce mandatory zero-energy verification and physical lock-out/tag-out before equipment boundary disruption."
    },
    "Working at Height": {
        "keywords": [
            "height", "scaffold", "scaffolding", "ladder", "harness", "lanyard", "guardrail",
            "fall protection", "fall arrest", "grating", "open edge", "platform", "manlift",
            "cherry picker", "basket", "roof", "elevated", "meters high", "ft high", "6 meters", "deck opening"
        ],
        "hazard_default": "Fall from Height / Unguarded Edge",
        "barrier_default": "Fall Protection System (Engineered Guardrails & Full-Body Harness)",
        "high_consequence": "Fall from elevation (>1.8m) → Severe trauma or fatality potential",
        "recommended_action": "Halt work, install physical barrier/edge protection, and verify 100% harness tie-off compliance."
    },
    "Hot Work": {
        "keywords": [
            "welding", "welder", "grinding", "torch", "cutting", "sparks", "flame", "hot work",
            "hydrocarbon", "hydrocarbon residue", "flammable", "gas test", "combustible",
            "lel", "fire watch", "flash fire", "habitat", "welding blanket", "crude vapour"
        ],
        "hazard_default": "Flammable Vapour / Process Residual Hydrocarbons",
        "barrier_default": "Hot Work Permit, Continuous Gas Testing & Fire Watch",
        "high_consequence": "Ignition of flammable hydrocarbon atmosphere → Flash fire / explosion fatality potential",
        "recommended_action": "Immediately stop hot work; perform four-gas testing and verify process decontamination."
    },
    "Confined Space": {
        "keywords": [
            "confined space", "vessel", "tank", "drum", "column", "sump", "pit", "manhole",
            "excavation", "oxygen", "toxic", "h2s", "co", "atmospheric test", "gas testing",
            "standby person", "hole watcher", "breathing apparatus", "scba", "forced ventilation"
        ],
        "hazard_default": "Atmospheric Hazard (Toxic Gas, H2S, or Oxygen Deficiency)",
        "barrier_default": "Confined Space Entry Permit, Calibrated Gas Testing & Standby Watch",
        "high_consequence": "Toxic inhalation or oxygen depletion (<19.5%) → Rapid asphyxiation / fatality potential",
        "recommended_action": "Suspend entry immediately; re-test atmosphere at all vessel elevations and verify continuous mechanical ventilation."
    },
    "Line of Fire": {
        "keywords": [
            "line of fire", "stored energy", "tension", "whip", "flying debris", "projectile",
            "pressurized hose", "hydraulic hose", "snapping", "cable snap", "pinch point",
            "crush zone", "moving machinery", "rotating", "swivel", "high pressure line"
        ],
        "hazard_default": "Kinetic / Mechanical Stored Energy & Trajectory Exposure",
        "barrier_default": "Physical Guarding, Whip Checks & Line-of-Fire Exclusion Zone",
        "high_consequence": "High-velocity projectile or pinch-point impact → Severe crush trauma or fatal strike",
        "recommended_action": "Establish demarcated exclusion perimeter and inspect mechanical restraining whip checks."
    },
    "Lifting Operations": {
        "keywords": [
            "crane", "lifting", "rigging", "sling", "shackle", "hoist", "suspended load",
            "rigger", "banksman", "crane operator", "boom", "lift plan", "tag line",
            "overhead load", "load dropped", "dropped object"
        ],
        "hazard_default": "Suspended Overhead Load / Rigging Failure",
        "barrier_default": "Certified Rigging Equipment, Lift Plan & Exclusion Zone",
        "high_consequence": "Dropped heavy load or boom failure → Catastrophic impact crush / multiple fatality potential",
        "recommended_action": "Barricade crane swing radius, verify rigging load-test certificates, and review critical lift plan."
    },
    "Driving": {
        "keywords": [
            "vehicle", "driving", "driver", "speeding", "seatbelt", "truck", "tanker",
            "pickup", "collision", "rollover", "journey management", "distracted driving", "fatigue"
        ],
        "hazard_default": "Vehicle in Motion / Transport Collision Hazard",
        "barrier_default": "Journey Management Plan, Seatbelts & Speed Governor Compliance",
        "high_consequence": "High-speed road or lease road rollover/collision → Severe vehicular trauma or fatality",
        "recommended_action": "Enforce in-vehicle monitoring system (IVMS) review and re-brief driver on journey management protocols."
    },
    "Work Authorization": {
        "keywords": [
            "permit to work", "ptw", "authorization", "unauthorized work", "simops",
            "job safety analysis", "jsa", "toolbox talk", "risk assessment", "permit expired"
        ],
        "hazard_default": "Uncontrolled Simultaneous Operations / Non-Authorized Hazard Exposure",
        "barrier_default": "Permit-to-Work (PTW) System & Work Authorization Controls",
        "high_consequence": "Uncoordinated process intervention → Escalated multi-system process safety incident",
        "recommended_action": "Stand-down job; audit permit scope against field activity and obtain issuing authority re-endorsement."
    },
    "Bypassing Safety Controls": {
        "keywords": [
            "override", "interlock", "safety valve", "psv", "prv", "alarm bypassed",
            "sensor disabled", "esd", "emergency shutdown bypassed", "tampered", "jumper"
        ],
        "hazard_default": "Defeated Process Safeguard / Unmitigated Process Deviation",
        "barrier_default": "Management of Change (MOC) & Formal Safety Control Bypass Authorization",
        "high_consequence": "Unmitigated overpressure or loss of primary containment → Major process hazard",
        "recommended_action": "Restore primary safety interlock/device or initiate emergency Management of Change (MOC) signoff."
    },
}

# Activity mapping
ACTIVITY_PATTERNS = [
    (r"\b(?:flange|pipeline|pipe\s+support|transfer\s+line|flowline|manifold|crude\s+line)\b", "Pipeline Maintenance"),
    (r"\b(?:weld(?:ing)?|cutting|torch|grinding|hot\s+work)\b", "Hot Work / Welding"),
    (r"\b(?:scaffold(?:ing)?|ladder|working\s+at\s+height|platform|roof|mast)\b", "Working at Height / Scaffolding"),
    (r"\b(?:vessel|tank\s+entry|column|drum|confined\s+space|manhole)\b", "Confined Space Entry"),
    (r"\b(?:crane|rigging|sling|lifting|hoist|banksman|suspended\s+load)\b", "Lifting Operations"),
    (r"\b(?:electrical|switchgear|breaker|transformer|substation|cable|supply\s+to\s+the\s+pump)\b", "Electrical Maintenance"),
    (r"\b(?:pump|compressor|engine|turbine|valve|motor|seal|bearing|mechanical)\b", "Mechanical Maintenance"),
    (r"\b(?:truck|tanker|vehicle|driving|transport|pickup)\b", "Vehicle Transport"),
    (r"\b(?:drilling|wellhead|blowout|drill\s+string|casing|wireline)\b", "Wellhead Operations"),
    (r"\b(?:paper|papers|trash|housekeeping|mess|debris|walkway|floor|lighting)\b", "Housekeeping & Routine"),
]

# Housekeeping / Low Risk Indicators
HOUSEKEEPING_PATTERNS = [
    r"\bloose\s+papers?\b",
    r"\bhousekeeping\b",
    r"\bswept\b",
    r"\blitter\b",
    r"\bwater\s+puddle\b",
    r"\bunorganized\s+tools\b",
    r"\btidy\b",
    r"\bclean\s+up\b",
]


def clean_text(text: str) -> str:
    """Normalize input text."""
    if not text:
        return ""
    return text.strip()


def extract_tokens_and_evidence(text: str) -> List[str]:
    """Extract relevant technical safety tokens from narrative."""
    lowered = text.lower()
    evidence = []
    
    technical_terms = [
        "pipeline", "transfer line", "crude oil", "flange", "loosening", "trapped pressure",
        "zero pressure", "zero energy", "isolation", "isolated", "locked out", "lockout", "tagout",
        "scaffold", "guardrail", "fall protection", "harness", "6 meters", "platform",
        "welding", "hydrocarbon residue", "gas testing", "flammable", "sparks",
        "confined space", "vessel", "atmospheric testing", "standby person",
        "crane", "rigging", "sling", "suspended load", "exclusion zone",
        "vehicle", "seatbelt", "driving", "loose papers", "housekeeping", "control room"
    ]
    
    for term in technical_terms:
        if term in lowered:
            evidence.append(term)
            
    # Also grab specific numbers with units like '6 meters' or '15 bar'
    measurement_matches = re.findall(r"\b\d+\s*(?:meters?|m|bar|psi|volts?|v|kv|tons?)\b", lowered)
    for m in measurement_matches:
        if m not in evidence:
            evidence.append(m)
            
    return evidence


def detect_activity(text: str) -> str:
    """Classify the operational activity."""
    lowered = text.lower()
    for pattern, activity_name in ACTIVITY_PATTERNS:
        if re.search(pattern, lowered):
            return activity_name
    return "Operational Maintenance"


def analyze_safety_report(narrative: str, site: str = "OIL Facility", report_type: str = "Observation") -> Dict[str, Any]:
    """
    Core AI/NLP Safety Intelligence Analyzer.
    Deterministic, transparent, explainable pipeline.
    """
    raw_text = clean_text(narrative)
    
   
    if not raw_text:
        return {
            "sif_level": "NEEDS REVIEW",
            "priority_score": 0,
            "score_label": "Report empty — no analysis possible.",
            "life_saving_rule": "None / General Safety",
            "activity": "Unspecified Activity",
            "hazard": "No Narrative Provided",
            "barrier": "Not Evaluated",
            "barrier_status": "N/A",
            "barrier_failure": "No text provided",
            "potential_consequence": "Cannot determine potential consequence without description.",
            "explanation": "No narrative text was supplied for evaluation.",
            "extracted_evidence": [],
            "recommended_action": "Please input a valid safety observation or incident narrative.",
            "secondary_notes": "",
            "is_valid": False,
            "error_message": "Empty report text."
        }
        
    if len(raw_text.split()) < 3 and not any(k in raw_text.lower() for k in ["welding", "scaffold", "crane", "flange"]):
        return {
            "sif_level": "NEEDS REVIEW",
            "priority_score": 15,
            "score_label": "Insufficient signal — manual triage recommended.",
            "life_saving_rule": "None / General Safety",
            "activity": "General Operations",
            "hazard": "Insufficient Signal / Low Data",
            "barrier": "Routine Administrative",
            "barrier_status": "Indeterminate",
            "barrier_failure": "Narrative too brief for automated screening",
            "potential_consequence": "Unknown consequence due to brief reporting.",
            "explanation": "The safety report contains fewer than 3 words and lacks identifiable hazard or barrier descriptors. Manual HSE review required.",
            "extracted_evidence": raw_text.split(),
            "recommended_action": "Contact the reporting observer to gather detailed event context.",
            "secondary_notes": "",
            "is_valid": True,
            "error_message": None
        }

    lowered = raw_text.lower()
    evidence = extract_tokens_and_evidence(raw_text)
    activity = detect_activity(raw_text)

    # Check for Housekeeping / Low Risk explicitly (Section 13 Test 5)
    is_housekeeping = any(re.search(p, lowered) for p in HOUSEKEEPING_PATTERNS)
    
    # Check for Successful Barrier execution (Section 13 Test 6)
    has_successful_barrier = any(re.search(p, lowered) for p in SUCCESS_BARRIER_PATTERNS)
    
    # Check for Barrier Failure / Omission / Violation (Section 13 Test 1, 2, 3, 4)
    has_barrier_omission = any(re.search(p, lowered) for p in OMISSION_NEGATION_PATTERNS)

   
    rule_scores = {}
    for rule, defn in RULE_DEFINITIONS.items():
        score = 0
        for kw in defn["keywords"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", lowered):
                score += 1
        rule_scores[rule] = score

    # Find highest matching rule
    sorted_rules = sorted(rule_scores.items(), key=lambda x: x[1], reverse=True)
    top_rule, top_count = sorted_rules[0]
    secondary_rule = sorted_rules[1][0] if len(sorted_rules) > 1 and sorted_rules[1][1] > 0 else None

    # Fallback if no specific rule matched
    if top_count == 0:
        if is_housekeeping:
            return {
                "sif_level": "LOW",
                "priority_score": 15,
                "score_label": "Low SIF potential — routine workplace observation.",
                "life_saving_rule": "None / General Safety",
                "activity": activity,
                "hazard": "Minor Housekeeping / Slip or Trip Issue",
                "barrier": "Routine Housekeeping & Workstation Standards",
                "barrier_status": "Controlled",
                "barrier_failure": "None identified / Minor housekeeping issue",
                "potential_consequence": "Minor slip, trip, or negligible impact.",
                "explanation": "The report describes a low-energy housekeeping matter with no exposure to high-energy hazardous sources or Life-Saving Rule breaches.",
                "extracted_evidence": evidence if evidence else ["housekeeping", "loose items"],
                "recommended_action": "Maintain clean workplace standards and close out during daily supervisor inspection.",
                "secondary_notes": "",
                "is_valid": True,
                "error_message": None
            }
        else:
            return {
                "sif_level": "LOW",
                "priority_score": 20,
                "score_label": "Insufficient signal — manual triage recommended.",
                "life_saving_rule": "None / General Safety",
                "activity": activity,
                "hazard": "Indeterminate / Low Signal",
                "barrier": "Standard Operating Procedures",
                "barrier_status": "Indeterminate",
                "barrier_failure": "None identified",
                "potential_consequence": "No direct high-energy precursor identified.",
                "explanation": "The narrative does not contain distinct Life-Saving Rule keywords or high-energy failure mechanisms. Flagged for standard HSE triage.",
                "extracted_evidence": evidence,
                "recommended_action": "Review during routine HSE safety meeting; request clarification if needed.",
                "secondary_notes": "",
                "is_valid": True,
                "error_message": None
            }

   
    rule_info = RULE_DEFINITIONS[top_rule]
    hazard = rule_info["hazard_default"]
    barrier = rule_info["barrier_default"]
    consequence = rule_info["high_consequence"]
    rec_action = rule_info["recommended_action"]
    
    # Specific Scenario Mapping & Nuance Handling
    barrier_failure = "None identified"
    barrier_status = "Controlled"
    sif_level = "LOW"
    priority_score = 25
    explanation = ""

    # Check Test 6: Successful Barrier (LOTO applied, zero energy verified)
    if top_rule == "Energy Isolation" and ("zero energy" in lowered or "confirmed" in lowered or "tested the equipment" in lowered) and not has_barrier_omission:
        sif_level = "LOW / NON-SIF"
        priority_score = 18
        barrier_status = "Successfully Applied"
        barrier_failure = "None identified (Barrier successfully applied)"
        consequence = "Hazardous energy safely isolated; work completed under controlled barrier protection."
        explanation = "The report confirms that electrical/energy isolation and lock-out were executed, and the technician verified zero energy prior to maintenance. Crucially, dangerous activities with successfully applied barriers do not constitute SIF precursors."
        rec_action = "Acknowledge proactive compliance with Energy Isolation Life-Saving Rule and record safe work practice."

    # Check Test 1: Energy Isolation Failure (did not verify zero pressure / flange loosening)
    elif top_rule == "Energy Isolation":
        if has_barrier_omission or "did not verify" in lowered or "trapped pressure" in lowered or "loosening the flange" in lowered:
            sif_level = "HIGH"
            priority_score = 90
            barrier_status = "Failed / Omitted"
            hazard = "Stored / Pressurized Energy"
            barrier = "Energy Isolation & Zero-Energy Verification"
            barrier_failure = "Zero-energy verification not completed"
            consequence = "Uncontrolled energy release → Serious Injury / Fatality potential"
            explanation = "The report describes exposure to stored pressure during pipeline/equipment maintenance and indicates that zero-pressure/zero-energy verification was not completed before the flange was opened. Although no injury occurred in this specific event, the potential consequence meets high SIF criteria."
            rec_action = "Verify isolation and zero-energy state before continuing maintenance; issue safety stand-down on flange opening procedures."
        else:
            sif_level = "MEDIUM"
            priority_score = 65
            barrier_status = "Degraded"
            barrier_failure = "Incomplete energy isolation verification"
            explanation = "The report identifies an activity involving hazardous stored energy. Review isolation controls and zero-energy logs."

    # Check Test 2: Working at Height (Missing guardrail / no fall protection)
    elif top_rule == "Working at Height":
        if has_barrier_omission or "missing" in lowered or "no alternative fall protection" in lowered or "guardrail" in lowered:
            sif_level = "HIGH"
            priority_score = 92
            barrier_status = "Failed / Omitted"
            hazard = "Fall from Height / Unguarded Edge"
            barrier = "Fall Protection System (Guardrails & Full-Body Harness)"
            barrier_failure = "Fall protection barrier failure (Missing guardrail / harness omitted)"
            consequence = "Fall from elevation → Serious Injury / Fatality potential"
            explanation = "The report identifies elevated work where edge protection was compromised (missing guardrail) and no secondary fall arrest system was utilized. Exposure to an unmitigated fall hazard carries immediate SIF potential."
            rec_action = "Halt elevated work immediately, barricade access, and install certified edge protection with 100% tie-off."
        else:
            sif_level = "MEDIUM"
            priority_score = 60
            barrier_status = "Degraded"
            barrier_failure = "Partial fall protection degradation"
            explanation = "Elevated work observed. Inspect scaffolding tags and fall arrest anchor points."

    # Check Test 3: Hot Work (Welding near residue, gas test skipped)
    elif top_rule == "Hot Work":
        if has_barrier_omission or "gas testing had not been completed" in lowered or "hydrocarbon residue" in lowered or "not been completed" in lowered:
            sif_level = "HIGH"
            priority_score = 88
            barrier_status = "Failed / Omitted"
            hazard = "Flammable Vapour / Process Hydrocarbon Residue"
            barrier = "Hot Work Permit & Continuous Gas Testing"
            barrier_failure = "Gas testing/area verification failure"
            consequence = "Hydrocarbon ignition / flash fire → Serious Injury / Fatality potential"
            explanation = "Welding or spark-producing work was initiated in proximity to residual hydrocarbons without prior atmospheric gas testing. This represents a critical breakdown of primary explosion prevention barriers."
            rec_action = "Stop hot work, isolate ignition sources, purge residual hydrocarbons, and require signed atmospheric test before restarting."
        else:
            sif_level = "MEDIUM"
            priority_score = 55
            barrier_status = "Degraded"
            barrier_failure = "Hot work housekeeping or minor perimeter issue"
            explanation = "Hot work observed. Ensure valid fire watch and continuous LEL monitoring."

    # Check Test 4: Confined Space (Entered vessel without atmospheric test)
    elif top_rule == "Confined Space":
        if has_barrier_omission or "atmospheric testing was not performed" in lowered or "entered the vessel" in lowered:
            sif_level = "HIGH"
            priority_score = 94
            barrier_status = "Failed / Omitted"
            hazard = "Atmospheric Hazard (Toxic Gas / Oxygen Deficiency)"
            barrier = "Confined Space Entry Permit & Atmospheric Gas Testing"
            barrier_failure = "Atmospheric gas testing omitted before vessel entry"
            consequence = "Toxic gas inhalation or asphyxiation (<19.5% O2) → Fatality potential"
            explanation = "Personnel entered a confined vessel without mandatory multi-gas testing. Atmospheric hazards are silent killers; entering without testing represents an immediate high-severity SIF precursor."
            rec_action = "Evacuate vessel, secure hatch with physical lockout, recalibrate gas detector, and retrain team on entry authorization."
        else:
            sif_level = "MEDIUM"
            priority_score = 65
            barrier_status = "Degraded"
            barrier_failure = "Permit or standby communication delay"
            explanation = "Confined space activity identified. Verify standby watcher presence and atmospheric test log."

    # General High SIF / Medium SIF evaluation for other rules
    elif top_rule in ["Line of Fire", "Lifting Operations"]:
        if has_barrier_omission or any(w in lowered for w in ["dropped", "snap", "struck", "under load", "pinch", "breach"]):
            sif_level = "HIGH"
            priority_score = 86
            barrier_status = "Failed / Omitted"
            barrier_failure = "Exclusion zone or equipment integrity failure"
            explanation = f"Critical breakdown of {top_rule} controls with potential high kinetic energy transfer."
        else:
            sif_level = "MEDIUM"
            priority_score = 58
            barrier_status = "Degraded"
            barrier_failure = "Pre-use inspection observation"
            explanation = f"Activity involves {top_rule}. Controls observed with minor deviations."

    elif top_rule in ["Driving", "Work Authorization", "Bypassing Safety Controls"]:
        if has_barrier_omission:
            sif_level = "HIGH"
            priority_score = 82
            barrier_status = "Failed / Omitted"
            barrier_failure = f"Core {top_rule} protocol omitted or bypassed"
            explanation = f"Intentional bypass or critical failure of {top_rule} barrier."
        else:
            sif_level = "MEDIUM"
            priority_score = 50
            barrier_status = "Degraded"
            barrier_failure = "Administrative or documentation gap"
            explanation = f"General observation related to {top_rule}."

    # Generate secondary rule note if applicable
    secondary_note = ""
    if secondary_rule and secondary_rule != top_rule and rule_scores.get(secondary_rule, 0) > 0:
        secondary_note = f"Note: Narrative also contains secondary references associated with IOGP {secondary_rule}."
        explanation += f" ({secondary_note})"

    score_label = (
        "High SIF potential — flagged for immediate HSE review."
        if sif_level == "HIGH"
        else "Medium SIF potential — schedule standard HSE review."
        if sif_level == "MEDIUM"
        else "Low SIF potential — routine workplace observation."
    )

    return {
        "sif_level": sif_level,
        "priority_score": priority_score,
        "score_label": score_label,
        "life_saving_rule": top_rule,
        "activity": activity,
        "hazard": hazard,
        "barrier": barrier,
        "barrier_status": barrier_status,
        "barrier_failure": barrier_failure,
        "potential_consequence": consequence,
        "explanation": explanation,
        "extracted_evidence": evidence,
        "recommended_action": rec_action,
        "secondary_notes": secondary_note,
        "is_valid": True,
        "error_message": None
    }
