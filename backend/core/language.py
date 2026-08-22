LANGUAGE_ALIASES = {
    "chinese": "zh",
    "english": "en",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "japanese": "ja",
    "korean": "ko",
    "simplified chinese": "zh-CN",
    "spanish": "es",
    "traditional chinese": "zh-TW",
}


def normalize_language_code(value: str) -> str:
    """Normalize language names and common BCP-47 spellings for storage."""

    cleaned = " ".join(value.strip().split())
    if not cleaned:
        raise ValueError("preferred_language cannot be empty")

    alias = LANGUAGE_ALIASES.get(cleaned.casefold())
    if alias is not None:
        return alias

    parts = cleaned.replace("_", "-").split("-")
    primary = parts[0].casefold()
    if len(primary) < 2 or not primary.isalpha():
        raise ValueError("preferred_language must be a language name or code")
    normalized = [primary]
    for part in parts[1:]:
        normalized.append(part.upper() if len(part) == 2 else part)
    result = "-".join(normalized)
    if len(result) > 16:
        raise ValueError("preferred_language must not exceed 16 characters")
    return result


def primary_language(value: str) -> str:
    return normalize_language_code(value).split("-", 1)[0]
