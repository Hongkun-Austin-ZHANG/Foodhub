from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ImagePolicy:
    max_bytes: int = 10 * 1024 * 1024
    allowed_content_types: tuple[str, ...] = ("image/jpeg", "image/png", "image/webp")


def validate_image(
    content: bytes, content_type: str, policy: ImagePolicy | None = None
) -> None:
    active_policy = policy or ImagePolicy()
    if content_type not in active_policy.allowed_content_types:
        raise ValueError("unsupported image content type")
    if not content:
        raise ValueError("image is empty")
    if len(content) > active_policy.max_bytes:
        raise ValueError("image exceeds maximum size")
