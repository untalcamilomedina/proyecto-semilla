from __future__ import annotations

import hashlib


def username_from_email(email: str, *, max_length: int = 150) -> str:
    normalized = email.strip().lower()
    if len(normalized) <= max_length:
        return normalized

    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:10]
    prefix_len = max_length - 1 - len(digest)
    return f"{normalized[:prefix_len]}-{digest}"

