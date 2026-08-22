from dataclasses import dataclass
from difflib import SequenceMatcher

from schemas.dish import ExternalDishCandidate, normalize_lookup_name


@dataclass(frozen=True, slots=True)
class DishMatchResult:
    candidate: ExternalDishCandidate | None
    score: float


def name_similarity(query: str, candidate: str) -> float:
    normalized_query = normalize_lookup_name(query)
    normalized_candidate = normalize_lookup_name(candidate)
    if not normalized_query or not normalized_candidate:
        return 0.0

    sequence_score = SequenceMatcher(
        None, normalized_query, normalized_candidate
    ).ratio()
    query_tokens = set(normalized_query.split())
    candidate_tokens = set(normalized_candidate.split())
    union = query_tokens | candidate_tokens
    token_score = len(query_tokens & candidate_tokens) / len(union) if union else 0.0
    return round((sequence_score * 0.7) + (token_score * 0.3), 4)


def select_best_candidate(
    canonical_name_en: str,
    candidates: list[ExternalDishCandidate],
    threshold: float,
) -> DishMatchResult:
    if not candidates:
        return DishMatchResult(candidate=None, score=0.0)

    scored = [
        (candidate, name_similarity(canonical_name_en, candidate.name))
        for candidate in candidates
    ]
    best_candidate, best_score = max(scored, key=lambda item: item[1])
    if best_score < threshold:
        return DishMatchResult(candidate=None, score=best_score)
    return DishMatchResult(candidate=best_candidate, score=best_score)
