from app.services.risk_classifier import classify_risk

def test_classify_risk_high():
    question = "Can I share customer PII with our new vendor?"
    answer = "Yes, you can share PII according to the policy."
    result = classify_risk(question, answer, [])
    
    assert result["risk_level"] == "high"
    assert result["requires_human_review"] == True
    assert "pii" in result["reason"].lower()

def test_classify_risk_medium():
    question = "What is the policy interpretation for working from home?"
    answer = "The policy interpretation depends on your manager."
    result = classify_risk(question, answer, [])
    
    assert result["risk_level"] == "medium"
    assert result["requires_human_review"] == False
    assert "policy interpretation" in result["reason"].lower()

def test_classify_risk_low():
    question = "Where can I find the employee handbook?"
    answer = "You can find it on the company intranet."
    result = classify_risk(question, answer, [])
    
    assert result["risk_level"] == "low"
    assert result["requires_human_review"] == False
    assert "No high or medium risk" in result["reason"]
