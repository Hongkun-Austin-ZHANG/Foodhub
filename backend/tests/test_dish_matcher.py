from schemas.dish import ExternalDishCandidate
from services.database.dish_matcher import name_similarity, select_best_candidate


def test_name_similarity_handles_punctuation_and_case() -> None:
    assert name_similarity("French Onion Soup", "french-onion soup") == 1.0


def test_best_candidate_requires_threshold() -> None:
    candidates = [
        ExternalDishCandidate(external_id="1", name="Onion Bhaji"),
        ExternalDishCandidate(external_id="2", name="French Onion Soup"),
    ]

    result = select_best_candidate("French Onion Soup", candidates, threshold=0.85)

    assert result.candidate is not None
    assert result.candidate.external_id == "2"
    assert result.score == 1.0
