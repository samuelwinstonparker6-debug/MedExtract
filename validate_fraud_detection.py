import os
from app.services.template_extractor import generate_fingerprint
from app.services.template_matcher import calculate_similarity, evaluate_fraud

def validate():
    print("Initializing Fraud Validation...")
    
    p1 = "tests/fraud_samples/auth_city_hosp.png"
    p2 = "tests/fraud_samples/auth_generic_labs.png"
    p3 = "tests/fraud_samples/fraud_amber_mike.png"  # Same provider, different patient -> Genuine template usage
    p4 = "tests/fraud_samples/fraud_red_fake.png"    # Different provider, same template -> Fraud
    
    fp1 = generate_fingerprint(p1)
    fp2 = generate_fingerprint(p2)
    fp3 = generate_fingerprint(p3)
    fp4 = generate_fingerprint(p4)
    
    # Test 1: Genuine Pair (img1 vs img3)
    # Same layout, same provider ("City Hospital")
    score1 = calculate_similarity(fp1, fp3)
    flag1 = evaluate_fraud(score1, "City Hospital", "City Hospital")
    print(f"Test 1 (Genuine Pair): Score={score1}, Flag={flag1}")
    assert flag1 == "NONE", f"Expected NONE, got {flag1}"
    
    # Test 2: Fraud Pair (img1 vs img4)
    # Same layout, different provider ("Fake Clinic")
    score2 = calculate_similarity(fp1, fp4)
    flag2 = evaluate_fraud(score2, "City Hospital", "Fake Clinic")
    print(f"Test 2 (Fraud Pair): Score={score2}, Flag={flag2}")
    assert flag2 in ["AMBER", "RED"], f"Expected AMBER/RED, got {flag2}"
    
    # Test 3: Different Layouts (img1 vs img2)
    score3 = calculate_similarity(fp1, fp2)
    flag3 = evaluate_fraud(score3, "City Hospital", "Generic Labs")
    print(f"Test 3 (Different Layouts): Score={score3}, Flag={flag3}")
    assert flag3 == "NONE", f"Expected NONE, got {flag3}"
    
    print("\nSUCCESS: All fraud detection tests passed!")

if __name__ == "__main__":
    validate()
