"""
SIF SENTINEL - Synthetic HSE Dataset Generator
Generates realistic oilfield safety reports tailored to OIL operational assets.
Target calibrated:
- 1,284 Total Synthetic Reports (data_source = 'DEMO')
- 286 High-SIF Precursors (22.3%)
- 47 PENDING HSE REVIEW
- 239 CONFIRMED BY HSE
Clearly marked everywhere: DEMO / SYNTHETIC DATA
"""

import random
import json
import sqlite3
from datetime import datetime, timedelta
from config import OIL_SITES, DEMO_SCENARIOS
from nlp_engine import analyze_safety_report
from db import (
    STATUS_PENDING, STATUS_CONFIRMED,
    STATUS_REJECTED, STATUS_NEEDS_REVIEW
)

REVIEWER_NAMES = [
    "R. Sharma (OIL Lead Process Safety)",
    "P. Das (Senior HSE Asset Inspector)",
    "K. Gogoi (Field Safety Specialist)",
    "M. Borah (Mechanical Integrity Eng.)",
    "B. Saikia (Asset Protection Lead)",
    "T. Phukan (HSE Operations Officer)",
]

# Rich narrative templates for varied generation
HIGH_SIF_TEMPLATES = [
    {
        "narrative": "During maintenance on crude export transfer line #{unit}, crew isolated upstream valve but neglected to bleed downstream vent or verify zero pressure prior to unbolting the spool flange. Sudden residual pressure puff observed.",
        "rule": "Energy Isolation",
        "activity": "Pipeline Maintenance",
        "hazard": "Stored / Pressurized Energy",
        "barrier": "Energy Isolation & Zero-Energy Verification",
        "barrier_failure": "Zero-energy verification not completed",
        "consequence": "Uncontrolled pressurized hydrocarbon release → High-velocity spray / eye trauma / fire potential",
        "action": "Enforce double block and bleed procedure; mandate digital pressure gauge verification before flange bolt removal.",
        "score_range": (85, 95),
        "comment": "Confirmed SIF precursor: Trapped crude line pressure breached barrier boundary without verification.",
    },
    {
        "narrative": "Scaffolders dismantled intermediate working deck at {height}m elevation on crude distillation tower without erecting edge barrier or providing temporary static safety lines for adjacent pipefitters.",
        "rule": "Working at Height",
        "activity": "Working at Height / Scaffolding",
        "hazard": "Fall from Height / Unguarded Edge",
        "barrier": "Fall Protection System (Guardrails & Full-Body Harness)",
        "barrier_failure": "Fall protection barrier failure (Missing guardrail / harness omitted)",
        "consequence": "Unprotected fall from elevated platform → Catastrophic blunt trauma or fatality",
        "action": "Issue immediate red scaffold tag; install dual guardrail and intermediate toe-board before re-entry.",
        "score_range": (88, 96),
        "comment": "Confirmed high SIF: Working at >4m with missing physical guardrails and zero 100% tie-off compliance.",
    },
    {
        "narrative": "Fabrication team started oxy-acetylene torch cutting on pipe support bracket 2 meters from open hydrocarbon sump. Continuous multi-gas detector was left inside crew vehicle and area gas testing was not conducted.",
        "rule": "Hot Work",
        "activity": "Hot Work / Welding",
        "hazard": "Flammable Vapour / Process Hydrocarbon Residue",
        "barrier": "Hot Work Permit & Continuous Gas Testing",
        "barrier_failure": "Gas testing/area verification failure",
        "consequence": "Hot spark ignition of fugitive volatile vapours → Flash fire or localized explosion",
        "action": "Immediate stop work; require calibrated 4-gas monitoring and fire blanket coverage within 15m radius.",
        "score_range": (86, 94),
        "comment": "Confirmed high SIF: Spark generation near hydrocarbon sump with complete omission of mandatory gas testing.",
    },
    {
        "narrative": "Cleaning contractor entered high-pressure separator vessel #{unit} via manway before atmospheric testing certificate was signed by authorized gas tester. Standby watchman was absent from manway perimeter.",
        "rule": "Confined Space",
        "activity": "Confined Space Entry",
        "hazard": "Atmospheric Hazard (Toxic Gas / Oxygen Deficiency)",
        "barrier": "Confined Space Entry Permit & Atmospheric Gas Testing",
        "barrier_failure": "Atmospheric gas testing omitted before vessel entry",
        "consequence": "Inhalation of toxic H2S or oxygen depleted atmosphere (<19%) → Rapid loss of consciousness / asphyxiation",
        "action": "Halt vessel entry, lock access hatch, station trained hole-watch, and verify three consecutive safe gas tests.",
        "score_range": (90, 98),
        "comment": "Confirmed high SIF: Vessel entry without toxic gas test is a primary life-threatening precursor.",
    },
    {
        "narrative": "Mobile crane was slewing a 4.2-ton manifold spool over the live gas compressor skid while maintenance workers were still beneath the load trajectory. Crane signalman failed to establish an exclusion barricade.",
        "rule": "Lifting Operations",
        "activity": "Lifting Operations",
        "hazard": "Suspended Overhead Load / Rigging Failure",
        "barrier": "Certified Rigging Equipment, Lift Plan & Exclusion Zone",
        "barrier_failure": "Exclusion zone not barricaded; load slewed above personnel",
        "consequence": "Rigging failure or load drop → Catastrophic crushing trauma / severe impact fatality",
        "action": "Barricade complete crane swing radius with physical hard fencing; enforce clear drop-zone protocol.",
        "score_range": (84, 92),
        "comment": "Confirmed high SIF: Overhead suspended heavy load slewed directly over working personnel.",
    },
    {
        "narrative": "Technician unbolted hydraulic actuator on emergency shutdown valve while accumulator circuit was holding 120 bar pressure. Hydraulic fluid jet vented into the personnel walkway.",
        "rule": "Energy Isolation",
        "activity": "Mechanical Maintenance",
        "hazard": "Stored / Pressurized Energy",
        "barrier": "Energy Isolation & Hydraulic Bleed-off",
        "barrier_failure": "Hydraulic accumulator depressurization omitted",
        "consequence": "High-pressure fluid injection into tissue → Severe arterial damage / amputation potential",
        "action": "Isolate hydraulic power unit and physically vent accumulator pressure gauge to zero.",
        "score_range": (88, 95),
        "comment": "Confirmed high SIF: High-pressure fluid injection risk due to un-depressurized accumulator.",
    },
    {
        "narrative": "Contractor truck driver speeding at 65 km/h on wet unpaved oilfield lease road without wearing seatbelt. Vehicle skidded near pipeline right-of-way culvert.",
        "rule": "Driving",
        "activity": "Vehicle Transport",
        "hazard": "Vehicle in Motion / Transport Collision Hazard",
        "barrier": "Journey Management Plan, Seatbelts & Speed Governor Compliance",
        "barrier_failure": "Excessive speed on hazardous road & seatbelt non-compliance",
        "consequence": "Vehicle rollover or culvert collision → Severe vehicular impact trauma",
        "action": "Review driver IVMS telemetry; enforce 40 km/h lease road speed limit and conduct defensive driving re-brief.",
        "score_range": (80, 89),
        "comment": "Confirmed high SIF: Hazardous transport violation on wet lease road near hydrocarbon infrastructure.",
    },
]

MEDIUM_SIF_TEMPLATES = [
    {
        "narrative": "Hot work permit issued for structural grinding at pump bay, but spark containment tarp was only partially fastened and dry chemical fire extinguisher inspection tag had lapsed by two weeks.",
        "rule": "Hot Work",
        "activity": "Hot Work / Welding",
        "hazard": "Flammable Vapour / Stray Hot Sparks",
        "barrier": "Hot Work Spark Containment & Fire Fighting Equipment",
        "barrier_failure": "Incomplete spark containment enclosure",
        "consequence": "Potential spark propagation to adjacent equipment",
        "action": "Re-secure fire-retardant containment and replace expired fire extinguisher.",
        "score_range": (50, 65),
    },
    {
        "narrative": "Electrical technician working inside low-voltage motor control center cabinet with calibrated test leads. Lockout padlock was applied, but warning danger tag was faded and partially illegible.",
        "rule": "Energy Isolation",
        "activity": "Electrical Maintenance",
        "hazard": "Low-Voltage Electrical Energy",
        "barrier": "Lockout Tagout System (LOTO)",
        "barrier_failure": "Illegible / degraded equipment identification tag",
        "consequence": "Risk of inadvertent switch energization by third party",
        "action": "Replace equipment isolation tag with weather-resistant serialized identification.",
        "score_range": (45, 60),
    },
    {
        "narrative": "Pipefitter wearing full fall arrest harness while inspecting elevated gas manifold at 2.4 meters, but lanyard snap hook was anchored to a 1-inch conduit pipe instead of an engineered anchorage point.",
        "rule": "Working at Height",
        "activity": "Working at Height / Scaffolding",
        "hazard": "Fall from Height",
        "barrier": "Engineered Anchorage Point & Full-Body Harness",
        "barrier_failure": "Non-certified tie-off anchorage point selected",
        "consequence": "Anchorage failure in the event of an arrested fall",
        "action": "Provide portable certified beam clamp or identify designated structural tie-off beam.",
        "score_range": (58, 70),
    },
    {
        "narrative": "Rigging slings used for lifting 800 kg valve body showed minor surface fraying on synthetic outer sleeve. Load was successfully set on trailer.",
        "rule": "Lifting Operations",
        "activity": "Lifting Operations",
        "hazard": "Suspended Overhead Load",
        "barrier": "Rigging Inspection & Color Code Verification",
        "barrier_failure": "Rigging sling minor surface wear / degradation",
        "consequence": "Reduced safety factor under dynamic lift load",
        "action": "Quarantine frayed synthetic sling and recertify rigging locker gear.",
        "score_range": (48, 62),
    },
    {
        "narrative": "Gas tester calibrated multi-gas monitor with bump gas, but calibration due date was scheduled for tomorrow afternoon. Testing results were within normal limits.",
        "rule": "Confined Space",
        "activity": "Confined Space Entry",
        "hazard": "Atmospheric Gas Monitoring",
        "barrier": "Calibrated Gas Detection Instrument",
        "barrier_failure": "Calibration certificate nearing expiry",
        "consequence": "Potential sensor drift over extended operational period",
        "action": "Send device to instrument lab for certified multi-point span recalibration.",
        "score_range": (42, 55),
    },
]

LOW_SIF_TEMPLATES = [
    {
        "narrative": "The electrical supply to pump #{unit} was isolated and locked out. The technician tested the equipment at local push button and confirmed zero energy before starting mechanical seal overhaul.",
        "rule": "Energy Isolation",
        "activity": "Electrical Maintenance",
        "hazard": "Stored / Electrical Energy (Controlled)",
        "barrier": "Energy Isolation (LOTO) & Zero-Energy Verification",
        "barrier_failure": "None identified (Barrier successfully applied)",
        "consequence": "Hazard safely controlled; zero-energy barrier fully validated.",
        "action": "Safe work observation logged; commend adherence to positive isolation protocol.",
        "score_range": (10, 20),
    },
    {
        "narrative": "Routine housekeeping check in control room lobby found several loose cardboard boxes and printer paper packages stacked in walkway. Material relocated to storage closet.",
        "rule": "None / General Safety",
        "activity": "Housekeeping & Routine",
        "hazard": "Minor Housekeeping / Trip Obstacle",
        "barrier": "Routine Housekeeping Standards",
        "barrier_failure": "None identified / Minor housekeeping issue",
        "consequence": "Minor trip hazard without high-energy potential.",
        "action": "Maintain clean workplace standards and close out during daily supervisor inspection.",
        "score_range": (10, 18),
    },
    {
        "narrative": "Small puddle of rainwater accumulated on concrete apron outside workshop bay after heavy monsoon shower. Area swept and caution cone placed.",
        "rule": "None / General Safety",
        "activity": "Housekeeping & Routine",
        "hazard": "Minor Slip Hazard (Wet Surface)",
        "barrier": "Workplace Drainage & Warning Signage",
        "barrier_failure": "None identified / Minor housekeeping issue",
        "consequence": "Low-speed slip with negligible injury potential.",
        "action": "Clear drainage ditch to avoid standing water buildup.",
        "score_range": (8, 16),
    },
    {
        "narrative": "Technician conducted pre-shift visual inspection of hand tools in mechanical workshop. Replaced one worn screwdriver with rounded head from tool inventory.",
        "rule": "None / General Safety",
        "activity": "Mechanical Maintenance",
        "hazard": "Minor Hand Tool Wear",
        "barrier": "Pre-Use Hand Tool Inspection",
        "barrier_failure": "None identified",
        "consequence": "Minor pinch or slippage during fastening.",
        "action": "Dispose of rounded tool and restock tool cabinet.",
        "score_range": (10, 20),
    },
    {
        "narrative": "Scaffold tag checked on painting platform. Green scaffold inspection tag was verified current and signed by scaffold inspector within the 7-day validity window.",
        "rule": "Working at Height",
        "activity": "Working at Height / Scaffolding",
        "hazard": "Work at Height (Controlled)",
        "barrier": "Scaffold Inspection & Tagging System",
        "barrier_failure": "None identified (Barrier successfully applied)",
        "consequence": "Engineered guardrails and toe-boards verified intact.",
        "action": "Record positive safe observation in daily contractor HSE log.",
        "score_range": (12, 22),
    },
    {
        "narrative": "Pre-entry gas test of freshwater pump suction sump completed with calibrated 4-gas detector. O2 measured 20.9%, H2S 0.0 ppm, LEL 0%, CO 0 ppm. Continuous ventilation started.",
        "rule": "Confined Space",
        "activity": "Confined Space Entry",
        "hazard": "Atmospheric Gas Monitoring (Controlled)",
        "barrier": "Atmospheric Gas Testing & Mechanical Ventilation",
        "barrier_failure": "None identified (Barrier successfully applied)",
        "consequence": "Atmosphere verified non-hazardous before personnel entry.",
        "action": "Continue mandatory continuous monitoring during sump maintenance.",
        "score_range": (10, 20),
    },
]


def seed_database(target_total: int = 1284, target_high_sif: int = 286, target_pending: int = 47):
    """
    Seed the database with calibrated synthetic demo data.
    Ensures:
    - 1,284 Total Demo records (data_source = 'DEMO')
    - 286 High SIF reports
    - 47 PENDING HSE REVIEW
    - 239 CONFIRMED BY HSE
    """
    from db import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clean previous records
    cursor.execute("DELETE FROM reports")
    conn.commit()
    
    print(f"Seeding synthetic HSE dataset: Total={target_total}, High-SIF={target_high_sif}, Pending={target_pending}...")
    
    high_count = target_high_sif  # 286
    medium_count = 340
    low_count = target_total - high_count - medium_count  # 658
    
    records = []
    base_date = datetime(2026, 9, 25, 18, 30)
    
    # 1. Insert the 6 Section 13 Demo Scenarios explicitly first
    demo_keys = list(DEMO_SCENARIOS.keys())
    for i, name in enumerate(demo_keys):
        demo = DEMO_SCENARIOS[name]
        analysis = analyze_safety_report(demo["text"])
        report_id = f"OIL-DEMO-2026-0000{i+1}"
        date_str = (base_date - timedelta(days=random.randint(1, 15), hours=random.randint(1, 23))).strftime("%Y-%m-%d %H:%M")
        
        # Test 1 and Test 2 start as PENDING HSE REVIEW
        if i in [0, 1]:
            status = STATUS_PENDING
            reviewer = ""
            comment = ""
            rev_date = ""
        elif i in [2, 3]:
            status = STATUS_CONFIRMED
            reviewer = REVIEWER_NAMES[i]
            comment = "SIF precursor confirmed based on barrier failure exposure."
            rev_date = (base_date - timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M")
        else:
            status = STATUS_REJECTED
            reviewer = REVIEWER_NAMES[4]
            comment = "Housekeeping/controlled activity — not classified as SIF."
            rev_date = (base_date - timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M")
            
        records.append((
            report_id,
            "DEMO",
            date_str,
            demo["site"],
            demo["report_type"],
            demo["text"],
            analysis["activity"],
            analysis["sif_level"],
            int(analysis["priority_score"]),
            analysis["life_saving_rule"],
            analysis["hazard"],
            analysis["barrier"],
            analysis["barrier_failure"],
            analysis["potential_consequence"],
            analysis["explanation"],
            json.dumps(analysis["extracted_evidence"]),
            analysis["recommended_action"],
            status,
            reviewer,
            comment,
            rev_date
        ))

    # Remaining counts:
    # 286 High SIF: 4 from demos (2 pending, 2 confirmed).
    # Remaining High: 286 - 4 = 282.
    # Exactly target_pending = 47 pending. We already have 2 pending in demos.
    # So we need 45 more pending in High SIF!
    # The other 282 - 45 = 237 High SIF will be CONFIRMED BY HSE!
    # Total Confirmed High SIF = 2 (demos) + 237 = 239! (Matches exactly 239 HSE Confirmed!)
    pending_high_remaining = target_pending - 2
    confirmed_high_remaining = 286 - 4 - pending_high_remaining  # 237
    
    report_num = 10
    
    # Generate High SIF records
    for i in range(282):
        tpl = random.choice(HIGH_SIF_TEMPLATES)
        text = tpl["narrative"].format(unit=random.randint(101, 899), height=random.choice([4.5, 6.0, 8.2, 12.0]))
        analysis = analyze_safety_report(text)
        
        report_id = f"OIL-DEMO-2026-{report_num:05d}"
        report_num += 1
        days_ago = random.randint(1, 180)
        date_str = (base_date - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).strftime("%Y-%m-%d %H:%M")
        site = random.choice(OIL_SITES)
        rpt_type = random.choice(["Near-Miss", "Unsafe Condition", "Unsafe Act"])
        
        if pending_high_remaining > 0:
            status = STATUS_PENDING
            reviewer = ""
            comment = ""
            rev_date = ""
            pending_high_remaining -= 1
        else:
            status = STATUS_CONFIRMED
            reviewer = random.choice(REVIEWER_NAMES)
            comment = tpl.get("comment", "Confirmed SIF precursor by HSE panel.")
            rev_date = (base_date - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M")
            
        records.append((
            report_id,
            "DEMO",
            date_str,
            site,
            rpt_type,
            text,
            tpl["activity"],
            "HIGH",
            random.randint(tpl["score_range"][0], tpl["score_range"][1]),
            tpl["rule"],
            tpl["hazard"],
            tpl["barrier"],
            tpl["barrier_failure"],
            tpl["consequence"],
            analysis["explanation"] if analysis["explanation"] else f"High consequence potential involving {tpl['rule']}.",
            json.dumps(analysis["extracted_evidence"]),
            tpl["action"],
            status,
            reviewer,
            comment,
            rev_date
        ))

    # Generate Medium SIF records (340 records)
    for i in range(medium_count):
        tpl = random.choice(MEDIUM_SIF_TEMPLATES)
        text = tpl["narrative"].format(unit=random.randint(101, 899))
        analysis = analyze_safety_report(text)
        
        report_id = f"OIL-DEMO-2026-{report_num:05d}"
        report_num += 1
        days_ago = random.randint(1, 180)
        date_str = (base_date - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).strftime("%Y-%m-%d %H:%M")
        site = random.choice(OIL_SITES)
        rpt_type = random.choice(["Unsafe Condition", "Unsafe Act", "Near-Miss"])
        
        # Mix of statuses for medium
        if i % 5 == 0:
            status = STATUS_NEEDS_REVIEW
            reviewer = random.choice(REVIEWER_NAMES)
            comment = "Additional field inspection requested on degraded barrier."
            rev_date = date_str
        elif i % 4 == 0:
            status = STATUS_REJECTED
            reviewer = random.choice(REVIEWER_NAMES)
            comment = "Medium risk mitigated at shift level; does not meet SIF threshold."
            rev_date = date_str
        else:
            status = STATUS_CONFIRMED
            reviewer = random.choice(REVIEWER_NAMES)
            comment = "Medium priority observation reviewed and logged."
            rev_date = date_str
            
        records.append((
            report_id,
            "DEMO",
            date_str,
            site,
            rpt_type,
            text,
            tpl["activity"],
            "MEDIUM",
            random.randint(tpl["score_range"][0], tpl["score_range"][1]),
            tpl["rule"],
            tpl["hazard"],
            tpl["barrier"],
            tpl["barrier_failure"],
            tpl["consequence"],
            analysis["explanation"] if analysis["explanation"] else f"Moderate risk exposure under {tpl['rule']}.",
            json.dumps(analysis["extracted_evidence"]),
            tpl["action"],
            status,
            reviewer,
            comment,
            rev_date
        ))

    # Generate Low SIF records (658 - 2 = 656 records)
    low_remaining = low_count - 2
    for i in range(low_remaining):
        tpl = random.choice(LOW_SIF_TEMPLATES)
        text = tpl["narrative"].format(unit=random.randint(101, 899))
        analysis = analyze_safety_report(text)
        
        report_id = f"OIL-DEMO-2026-{report_num:05d}"
        report_num += 1
        days_ago = random.randint(1, 180)
        date_str = (base_date - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).strftime("%Y-%m-%d %H:%M")
        site = random.choice(OIL_SITES)
        rpt_type = random.choice(["Safe Observation", "Unsafe Condition", "Safe Observation"])
        
        status = STATUS_REJECTED if "housekeeping" in text.lower() or "papers" in text.lower() else STATUS_CONFIRMED
        reviewer = random.choice(REVIEWER_NAMES) if i % 2 == 0 else ""
        comment = "Safe barrier observation closed out." if status == STATUS_CONFIRMED else "Low severity routine task."
        rev_date = date_str if reviewer else ""
            
        records.append((
            report_id,
            "DEMO",
            date_str,
            site,
            rpt_type,
            text,
            tpl["activity"],
            "LOW" if tpl["rule"] == "None / General Safety" else "LOW / NON-SIF",
            random.randint(tpl["score_range"][0], tpl["score_range"][1]),
            tpl["rule"],
            tpl["hazard"],
            tpl["barrier"],
            tpl["barrier_failure"],
            tpl["consequence"],
            analysis["explanation"] if analysis["explanation"] else "Low severity observation with controlled risks.",
            json.dumps(analysis["extracted_evidence"]),
            tpl["action"],
            status,
            reviewer,
            comment,
            rev_date
        ))

    # Bulk insert
    cursor.executemany("""
    INSERT INTO reports (
        report_id, data_source, date, site, report_type, narrative, activity,
        sif_level, priority_score, life_saving_rule, hazard,
        barrier, barrier_failure, potential_consequence, explanation,
        evidence, recommended_action, review_status, reviewer_name, reviewer_comment, review_date
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)
    
    conn.commit()
    
    # Final counts check
    cursor.execute("SELECT COUNT(*) FROM reports")
    final_total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM reports WHERE data_source = 'DEMO'")
    final_demo = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM reports WHERE data_source = 'LIVE'")
    final_live = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM reports WHERE sif_level = 'HIGH'")
    final_high = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM reports WHERE review_status = ?", (STATUS_PENDING,))
    final_pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM reports WHERE review_status = ? AND sif_level = 'HIGH'", (STATUS_CONFIRMED,))
    final_confirmed_high = cursor.fetchone()[0]
    
    conn.close()
    print(f"Database seeded successfully:")
    print(f"  Total: {final_total} (Demo: {final_demo}, Live: {final_live})")
    print(f"  High-SIF: {final_high} ({final_high/final_total*100:.1f}%)")
    print(f"  Pending HSE Review: {final_pending}")
    print(f"  High-SIF Confirmed by HSE: {final_confirmed_high}")


if __name__ == "__main__":
    from db import init_db
    init_db(force_reseed=True)
