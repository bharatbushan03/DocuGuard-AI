import pytest
from app.services.confidence_scorer import calculate_confidence

def test_calculate_confidence_insufficient_info():
    score = calculate_confidence([], 0.0, "I could not find enough information in the provided documents")
    assert score == 0.0

def test_calculate_confidence_empty_chunks():
    score = calculate_confidence([], 1.0, "Here is an answer.")
    assert score == 0.0

def test_calculate_confidence_high_score():
    chunks = [
        {"score": 0.9, "access_level": "private"},
        {"score": 0.95, "access_level": "private"},
        {"score": 0.88, "access_level": "internal"},
        {"score": 0.92, "access_level": "private"},
        {"score": 0.91, "access_level": "confidential"}
    ]
    # avg_sim = 0.912
    # chunk_factor = 1.0 (5 chunks)
    # citation_coverage = 1.0
    # trusted_ratio = 1.0
    # score = (0.912 * 0.35) + (1.0 * 0.35) + (1.0 * 0.15) + (1.0 * 0.15)
    # score = 0.3192 + 0.35 + 0.15 + 0.15 = 0.9692
    score = calculate_confidence(chunks, 1.0, "This is a supported answer.")
    assert score > 0.75
    assert score <= 1.0

def test_calculate_confidence_medium_score():
    chunks = [
        {"score": 0.6, "access_level": "public"},
        {"score": 0.5, "access_level": "public"}
    ]
    # avg_sim = 0.55
    # chunk_factor = 2/5 = 0.4
    # citation_coverage = 0.5
    # trusted_ratio = 0.0
    # score = (0.55 * 0.35) + (0.5 * 0.35) + (0.4 * 0.15) + (0.0 * 0.15)
    # score = 0.1925 + 0.175 + 0.06 + 0 = 0.4275
    score = calculate_confidence(chunks, 0.5, "This is a partially supported answer.")
    assert score < 0.45

def test_calculate_confidence_low_score():
    chunks = [
        {"score": 0.3, "access_level": "public"}
    ]
    # avg_sim = 0.3
    # chunk_factor = 0.2
    # citation_coverage = 0.1
    # trusted_ratio = 0.0
    # score = (0.3 * 0.35) + (0.1 * 0.35) + (0.2 * 0.15) = 0.105 + 0.035 + 0.03 = 0.17
    score = calculate_confidence(chunks, 0.1, "This is a poorly supported answer.")
    assert score < 0.45
