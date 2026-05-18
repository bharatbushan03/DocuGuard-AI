import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

HIGH_RISK_KEYWORDS = [
    "pii", "ssn", "social security", "credit card", "passport",
    "contract approval", "sign-off", "legal approval",
    "financial commitment", "budget approval", "transfer funds",
    "security exception", "bypass security", "firewall rule",
    "regulatory compliance", "gdpr", "hipaa", "soc2",
    "terminate employee", "fire employee",
    "medical decision", "safety protocol"
]

MEDIUM_RISK_KEYWORDS = [
    "policy interpretation", "interpret policy",
    "vendor review", "third party assessment",
    "refund approval", "issue refund",
    "reimbursement", "expense report",
    "hr process", "promotion process", "performance review"
]

def classify_risk_rule_based(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    
    # Check high risk
    for kw in HIGH_RISK_KEYWORDS:
        if kw in text_lower:
            return {
                "risk_level": "high",
                "reason": f"Matched high-risk keyword: '{kw}'",
                "requires_human_review": True
            }
            
    # Check medium risk
    for kw in MEDIUM_RISK_KEYWORDS:
        if kw in text_lower:
            return {
                "risk_level": "medium",
                "reason": f"Matched medium-risk keyword: '{kw}'",
                "requires_human_review": False
            }
            
    # Default low risk
    return {
        "risk_level": "low",
        "reason": "No high or medium risk keywords detected.",
        "requires_human_review": False
    }

def classify_risk_llm(question: str, answer: str, citations: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Placeholder for LLM-based classifier
    # In a real scenario, this would prompt an LLM to evaluate the risk.
    return {
        "risk_level": "low",
        "reason": "LLM classifier not fully implemented.",
        "requires_human_review": False
    }

def classify_risk(question: str, answer: str, citations: List[Dict[str, Any]] = None, use_llm: bool = False) -> Dict[str, Any]:
    """
    Classifies the risk of a given question and AI answer.
    First uses a rule-based approach, and can optionally use an LLM-based approach.
    """
    combined_text = f"Question: {question}\nAnswer: {answer}"
    
    # Run rule-based classifier
    rule_result = classify_risk_rule_based(combined_text)
    
    if rule_result["risk_level"] == "high":
        return rule_result
        
    if use_llm:
        # If rules say low/medium, we could still use LLM for deeper analysis
        llm_result = classify_risk_llm(question, answer, citations or [])
        if llm_result["risk_level"] == "high" or (llm_result["risk_level"] == "medium" and rule_result["risk_level"] == "low"):
            return llm_result
            
    return rule_result
