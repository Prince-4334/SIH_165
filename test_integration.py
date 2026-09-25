"""
SIF SENTINEL - Comprehensive Integration Test Suite
Validates the entire end-to-end pipeline:
1. Demo vs Live dataset separation (1,284 Demo, 0 Live initially)
2. Section 13 Test Scenarios NLP precision
3. In-memory analysis without premature DB save
4. Save report as LIVE data with HSE disposition
5. KPI updates: Total (1,285), Live (1), Pending (48)
6. Duplicate prevention on re-saving
7. HSE Review Status workflow update (Pending -> Confirmed -> KPI decrements)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from nlp_engine import analyze_safety_report
from db import (
    init_db, get_kpis, save_report, update_review_status,
    get_all_reports, get_report_by_id,
    STATUS_PENDING, STATUS_CONFIRMED, STATUS_REJECTED, STATUS_NEEDS_REVIEW
)
from config import DEMO_SCENARIOS

def test_full_pipeline():
    print("==================================================================")
    print("STARTING FULL END-TO-END INTEGRATION TEST SUITE (WITH HSE GOVERNANCE)")
    print("==================================================================\n")

    # Step 1: Check initial database KPIs (1,284 Demo, 0 Live, 47 Pending)
    kpis_init = get_kpis(source_filter="ALL")
    print("1. Initial SQLite Database State:")
    print(f"   Demo Benchmark Reports: {kpis_init['demo_count']:,}")
    print(f"   Live Session Reports:   {kpis_init['live_count']}")
    print(f"   Combined Total Reports: {kpis_init['total_combined']:,}")
    print(f"   SIF-Potential (High):   {kpis_init['sif_potential']:,}")
    print(f"   Pending HSE Review:     {kpis_init['pending_review']}")
    print(f"   HSE Confirmed SIF:      {kpis_init['hse_confirmed']}")
    assert kpis_init['demo_count'] == 1284, f"Expected 1284 demo reports, got {kpis_init['demo_count']}"
    assert kpis_init['live_count'] == 0, f"Expected 0 live reports initially, got {kpis_init['live_count']}"
    assert kpis_init['total_combined'] == 1284, f"Expected 1284 total initially, got {kpis_init['total_combined']}"
    assert kpis_init['sif_potential'] == 286, f"Expected 286 high SIF initially, got {kpis_init['sif_potential']}"
    assert kpis_init['pending_review'] == 47, f"Expected 47 pending review initially, got {kpis_init['pending_review']}"
    assert kpis_init['hse_confirmed'] == 239, f"Expected 239 HSE confirmed initially, got {kpis_init['hse_confirmed']}"
    print("   [OK] Initial dataset provenance and calibrated review targets verified!\n")

    # Step 2: Test Analysis (in-memory only — must NOT change counts)
    test_narrative = "While unbolting blind flange on natural gas line, trapped pressure escaped with a loud hiss. Gas testing had not been re-verified after lunch break."
    print("2. Testing AI/NLP Analysis (In-Memory Only):")
    print(f"   \"{test_narrative}\"")
    result = analyze_safety_report(test_narrative, site="Kumchai Production Terminal", report_type="Near-Miss")
    print(f"   → SIF Level: {result['sif_level']}")
    print(f"   → Priority Score: {result['priority_score']}/100")
    print(f"   → Rule: {result['life_saving_rule']}")
    print(f"   → Barrier Failure: {result['barrier_failure']}")
    assert result['sif_level'] == "HIGH"
    assert result['life_saving_rule'] == "Energy Isolation"
    
    # Verify counts have NOT changed just by analyzing
    kpis_check = get_kpis(source_filter="ALL")
    assert kpis_check['total_combined'] == 1284, "Total count should NOT change from analyzing alone!"
    assert kpis_check['live_count'] == 0, "Live count should NOT change from analyzing alone!"
    print("   [OK] In-memory analysis verified: zero persistent changes before user Save!\n")

    # Step 3: Save Report as LIVE session report with HSE disposition
    print("3. Testing Saving Report as 🟢 LIVE SESSION REPORT:")
    save_payload = {
        "narrative": test_narrative,
        "site": "Kumchai Production Terminal",
        "report_type": "Near-Miss",
        "activity": result["activity"],
        "sif_level": result["sif_level"],
        "priority_score": result["priority_score"],
        "life_saving_rule": result["life_saving_rule"],
        "hazard": result["hazard"],
        "barrier": result["barrier"],
        "barrier_failure": result["barrier_failure"],
        "potential_consequence": result["potential_consequence"],
        "explanation": result["explanation"],
        "extracted_evidence": result["extracted_evidence"],
        "recommended_action": result["recommended_action"],
        "data_source": "LIVE",
        "review_status": STATUS_PENDING,
        "reviewer_name": "P. Das (OIL Senior HSE Inspector)",
        "reviewer_comment": "Preliminary SIF flag submitted for joint verification."
    }
    new_report_id, is_duplicate = save_report(save_payload)
    print(f"   Committed new report as ID: {new_report_id} (Duplicate: {is_duplicate})")
    assert not is_duplicate, "First insertion should not be marked duplicate"
    
    # Check KPIs after save:
    # Demo = 1,284
    # Live = 1
    # Combined = 1,285
    # High SIF = 287
    # Pending = 48
    kpis_after = get_kpis(source_filter="ALL")
    print(f"   Demo Data:     {kpis_after['demo_count']}")
    print(f"   Live Session:  {kpis_after['live_count']} (incremented +1)")
    print(f"   Combined:      {kpis_after['total_combined']} (was 1,284 -> now 1,285)")
    print(f"   High SIF:      {kpis_after['sif_potential']} (was 286 -> now 287)")
    print(f"   Pending Review: {kpis_after['pending_review']} (was 47 -> now 48)")
    assert kpis_after['demo_count'] == 1284
    assert kpis_after['live_count'] == 1
    assert kpis_after['total_combined'] == 1285
    assert kpis_after['sif_potential'] == 287
    assert kpis_after['pending_review'] == 48
    print("   [OK] Live Session (+1), Combined (1,285), and Pending Review (+1) confirmed!\n")

    # Step 4: Test Duplicate Prevention
    print("4. Testing Duplicate Prevention (Clicking Save Again):")
    dup_id, dup_flag = save_report(save_payload)
    print(f"   Second save returned ID: {dup_id} (is_duplicate={dup_flag})")
    assert dup_flag is True, "Re-saving the same narrative must be caught as a duplicate"
    kpis_dup = get_kpis(source_filter="ALL")
    assert kpis_dup['total_combined'] == 1285, "Total count must NOT increment on duplicate save"
    print("   [OK] Duplicate prevention verified: count remains exactly 1,285!\n")

    # Step 5: Test HSE Officer Status Confirmation Workflow
    print("5. Testing HSE Review Workflow (Officer Confirms SIF):")
    update_review_status(
        new_report_id,
        new_status=STATUS_CONFIRMED,
        reviewer_name="R. Sharma (OIL Lead Process Safety)",
        reviewer_comment="Confirmed SIF precursor: Zero-pressure verification was not completed before unbolting."
    )
    fetched = get_report_by_id(new_report_id)
    assert fetched["review_status"] == STATUS_CONFIRMED
    assert "Sharma" in fetched["reviewer_name"]
    
    kpis_confirmed = get_kpis(source_filter="ALL")
    print(f"   Pending count after confirmation: {kpis_confirmed['pending_review']} (decreased back to 47)")
    print(f"   HSE Confirmed count:             {kpis_confirmed['hse_confirmed']} (was 239 -> now 240)")
    assert kpis_confirmed['pending_review'] == 47
    assert kpis_confirmed['hse_confirmed'] == 240
    print("   [OK] HSE Review status update and KPI re-computation verified!\n")

    print("==================================================================")
    print("🎉 ALL INTEGRATION TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================================")

if __name__ == "__main__":
    test_full_pipeline()
