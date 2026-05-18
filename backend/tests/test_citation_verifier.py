from app.services.citation_verifier import verify_claim, verify_and_rewrite_answer

def test_verify_claim_supported():
    claim = "The company allows employees to work from home."
    chunks = [{"content": "Employees are permitted to work from home up to two days a week."}]
    assert verify_claim(claim, chunks, overlap_threshold=0.3) == True

def test_verify_claim_unsupported():
    claim = "The company provides free lunches every day."
    chunks = [{"content": "Employees are permitted to work from home up to two days a week."}]
    assert verify_claim(claim, chunks, overlap_threshold=0.3) == False

def test_verify_and_rewrite_answer_partial():
    answer = "Employees can work from home. Also, the company provides free lunches."
    chunks = [{"content": "Employees are permitted to work from home up to two days a week."}]
    rewritten, coverage = verify_and_rewrite_answer(answer, chunks)
    
    assert "free lunches" not in rewritten
    assert "work from home" in rewritten
    assert coverage == 0.5 # 1 out of 2 claims supported

def test_verify_and_rewrite_answer_full():
    answer = "Employees can work from home."
    chunks = [{"content": "Employees are permitted to work from home up to two days a week."}]
    rewritten, coverage = verify_and_rewrite_answer(answer, chunks)
    
    assert "work from home" in rewritten
    assert coverage == 1.0

def test_verify_and_rewrite_answer_none():
    answer = "The company provides free lunches every day."
    chunks = [{"content": "Employees are permitted to work from home up to two days a week."}]
    rewritten, coverage = verify_and_rewrite_answer(answer, chunks)
    
    assert coverage == 0.0
    assert "could not find enough information" in rewritten
