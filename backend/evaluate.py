import json
import csv
import sys
import os
from typing import List, Dict, Any

# Adjust path to find app imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app.db.base
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.crud.crud_user import get_user_by_email, create_user
from app.schemas.user import UserCreate

client = TestClient(app)

def get_jaccard_similarity(str1: str, str2: str) -> float:
    a = set(str1.lower().split())
    b = set(str2.lower().split())
    if not a and not b:
        return 1.0
    return len(a.intersection(b)) / len(a.union(b))

def setup_admin_user() -> str:
    """Ensure admin user exists and return an access token."""
    db = SessionLocal()
    try:
        user = get_user_by_email(db, "admin@docuguard.com")
        if not user:
            user_in = UserCreate(email="admin@docuguard.com", password="securepassword", role="admin")
            create_user(db, user_in)
    finally:
        db.close()
        
    response = client.post("/api/auth/login", data={
        "username": "admin@docuguard.com",
        "password": "securepassword"
    })
    return response.json()["access_token"]

def main():
    print("Setting up test user...")
    try:
        token = setup_admin_user()
    except Exception as e:
        print(f"Error during auth setup: {e}")
        sys.exit(1)
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Load dataset
    dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation_dataset.json")
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}")
        sys.exit(1)
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)
        
    results = []
    
    print(f"Loaded {len(test_cases)} test cases. Starting evaluation...")
    
    for idx, case in enumerate(test_cases):
        q = case["question"]
        print(f"[{idx+1}/{len(test_cases)}] Evaluating: {q}")
        
        try:
            # Query the RAG endpoint
            res = client.post("/api/chat/query", json={"question": q}, headers=headers)
            if res.status_code != 200:
                print(f"  Error: HTTP {res.status_code} - {res.text}")
                continue
                
            res_data = res.json()
            actual_answer = res_data.get("answer", "")
            actual_citations = res_data.get("citations", [])
            actual_risk = res_data.get("risk_level", "low")
            actual_requires_review = res_data.get("requires_human_review", False)
            
            # 1. Answer Similarity (Jaccard)
            similarity = get_jaccard_similarity(case["expected_answer"], actual_answer)
            
            # 2. Citation Correctness
            # Check if expected document name is cited
            expected_doc = case["expected_document"]
            citation_correct = False
            if not expected_doc:
                citation_correct = len(actual_citations) == 0
            else:
                citation_correct = any(
                    expected_doc.lower() in str(c.get("document", "")).lower() 
                    for c in actual_citations
                )
                
            # 3. Risk Level Correctness
            risk_correct = actual_risk.lower() == case["expected_risk_level"].lower()
            
            # 4. Refusal Correctness
            refusal_correct = True
            if not case["answerable_from_context"]:
                # Should contain refusal language
                refusal_correct = (
                    "could not find enough information" in actual_answer.lower() or 
                    "insufficient information" in actual_answer.lower()
                )
                
            # 5. Human Review Trigger Correctness
            human_review_correct = actual_requires_review == case["should_require_human_review"]
            
            results.append({
                "question": q,
                "expected_answer": case["expected_answer"],
                "actual_answer": actual_answer,
                "answer_similarity": similarity,
                "expected_document": expected_doc,
                "citation_correct": citation_correct,
                "expected_risk_level": case["expected_risk_level"],
                "actual_risk_level": actual_risk,
                "risk_correct": risk_correct,
                "should_require_human_review": case["should_require_human_review"],
                "actual_require_human_review": actual_requires_review,
                "human_review_correct": human_review_correct,
                "answerable_from_context": case["answerable_from_context"],
                "refusal_correct": refusal_correct,
                "status": "PASS" if (citation_correct and risk_correct and refusal_correct and human_review_correct) else "FAIL"
            })
            
        except Exception as ex:
            print(f"  Exception occurred: {ex}")
            
    # Calculate Overall Stats
    total = len(results)
    if total == 0:
        print("No evaluation results were recorded.")
        return
        
    passed = sum(1 for r in results if r["status"] == "PASS")
    avg_sim = sum(r["answer_similarity"] for r in results) / total
    citation_accuracy = sum(1 for r in results if r["citation_correct"]) / total
    risk_accuracy = sum(1 for r in results if r["risk_correct"]) / total
    refusal_accuracy = sum(
        1 for r in results 
        if not r["answerable_from_context"] and r["refusal_correct"]
    ) / max(sum(1 for r in results if not r["answerable_from_context"]), 1)
    
    report_summary = {
        "summary": {
            "total_questions": total,
            "passed_checks": passed,
            "pass_rate": passed / total,
            "average_answer_similarity": avg_sim,
            "citation_accuracy": citation_accuracy,
            "risk_classification_accuracy": risk_accuracy,
            "refusal_accuracy_unanswerable": refusal_accuracy
        },
        "results": results
    }
    
    # Save JSON Report
    report_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation_report.json")
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_summary, f, indent=2)
        
    # Save CSV Report
    report_csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation_report.csv")
    with open(report_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Question", "Answerable", "Status", "Similarity", 
            "Expected Doc", "Citation Correct", "Expected Risk", 
            "Actual Risk", "Risk Correct", "Expected Human Review", "Actual Human Review"
        ])
        for r in results:
            writer.writerow([
                r["question"],
                r["answerable_from_context"],
                r["status"],
                round(r["answer_similarity"], 2),
                r["expected_document"],
                r["citation_correct"],
                r["expected_risk_level"],
                r["actual_risk_level"],
                r["risk_correct"],
                r["should_require_human_review"],
                r["actual_require_human_review"]
            ])
            
    print("\n================ Evaluation Completed ================")
    print(f"Total Questions: {total}")
    print(f"Overall Pass Rate: {passed / total * 100:.1f}%")
    print(f"Average Answer Similarity: {avg_sim * 100:.1f}%")
    print(f"Citation Accuracy: {citation_accuracy * 100:.1f}%")
    print(f"Risk Classification Accuracy: {risk_accuracy * 100:.1f}%")
    print(f"Refusal Accuracy: {refusal_accuracy * 100:.1f}%")
    print(f"Reports saved to {report_json_path} and {report_csv_path}")

if __name__ == "__main__":
    main()
