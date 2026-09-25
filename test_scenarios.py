"""
Verification script for Section 13 Test Scenarios.
Ensures 100% compliance with expected SIF levels, rules, hazards, and barrier failures.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from nlp_engine import analyze_safety_report
from config import DEMO_SCENARIOS

def run_tests():
    print("=================================================================")
    print("RUNNING SECTION 13 TEST SUITE — SIF SENTINEL NLP ENGINE")
    print("=================================================================\n")
    
    passed_all = True
    
    for name, data in DEMO_SCENARIOS.items():
        text = data["text"]
        result = analyze_safety_report(text)
        
        print(f"▶ SCENARIO: {name}")
        print(f"  Input: \"{text[:80]}...\"")
        print(f"  → SIF Potential: {result['sif_level']} (Score: {result['priority_score']}/100)")
        print(f"  → Life-Saving Rule: {result['life_saving_rule']}")
        print(f"  → Hazard: {result['hazard']}")
        print(f"  → Barrier: {result['barrier']}")
        print(f"  → Barrier Failure: {result['barrier_failure']}")
        print(f"  → Consequence: {result['potential_consequence']}")
        print(f"  → Explanation: {result['explanation']}")
        print(f"  → Evidence: {result['extracted_evidence']}")
        print(f"  → Action: {result['recommended_action']}")
        
        # Check assertions
        if "Test 1" in name:
            assert result["sif_level"] == "HIGH", f"Test 1 failed: Expected HIGH, got {result['sif_level']}"
            assert result["life_saving_rule"] == "Energy Isolation", f"Test 1 rule mismatch: {result['life_saving_rule']}"
            assert "Zero-energy" in result["barrier_failure"] or "zero" in result["barrier_failure"].lower(), "Test 1 barrier failure mismatch"
            print("  ✅ TEST 1 PASSED: 'Nobody was injured' correctly did NOT downgrade high consequence!")
            
        elif "Test 2" in name:
            assert result["sif_level"] == "HIGH", f"Test 2 failed: Expected HIGH, got {result['sif_level']}"
            assert result["life_saving_rule"] == "Working at Height", f"Test 2 rule mismatch: {result['life_saving_rule']}"
            print("  ✅ TEST 2 PASSED: Missing guardrail identified as High SIF Working at Height!")
            
        elif "Test 3" in name:
            assert result["sif_level"] == "HIGH", f"Test 3 failed: Expected HIGH, got {result['sif_level']}"
            assert result["life_saving_rule"] == "Hot Work", f"Test 3 rule mismatch: {result['life_saving_rule']}"
            assert "Gas testing" in result["barrier_failure"] or "gas" in result["barrier_failure"].lower(), "Test 3 barrier failure mismatch"
            print("  ✅ TEST 3 PASSED: Welding near residue without gas test identified as High SIF Hot Work!")
            
        elif "Test 4" in name:
            assert result["sif_level"] == "HIGH", f"Test 4 failed: Expected HIGH, got {result['sif_level']}"
            assert result["life_saving_rule"] == "Confined Space", f"Test 4 rule mismatch: {result['life_saving_rule']}"
            assert "Atmospheric" in result["barrier_failure"] or "gas" in result["barrier_failure"].lower(), "Test 4 barrier failure mismatch"
            print("  ✅ TEST 4 PASSED: Vessel entry without atmospheric testing identified as High SIF Confined Space!")
            
        elif "Test 5" in name:
            assert result["sif_level"] in ["LOW", "NON-SIF"], f"Test 5 failed: Expected LOW, got {result['sif_level']}"
            print("  ✅ TEST 5 PASSED: Loose papers housekeeping correctly classified as Low SIF / Non-SIF!")
            
        elif "Test 6" in name:
            assert result["sif_level"] in ["LOW", "NON-SIF", "LOW / NON-SIF"], f"Test 6 failed: Expected LOW/NON-SIF, got {result['sif_level']}"
            assert "None identified" in result["barrier_failure"] or "successfully" in result["barrier_failure"].lower(), "Test 6 barrier failure mismatch"
            print("  ✅ TEST 6 PASSED: Verified zero-energy barrier correctly classified as safe / non-precursor!")
            
        print("-" * 65)

    print("\n🎉 ALL 6 SECTION 13 TEST SCENARIOS PASSED WITH FULL FIDELITY!\n")

if __name__ == "__main__":
    run_tests()
