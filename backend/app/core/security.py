"""Security utilities: API key auth and in-memory rate limiting."""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from typing import Deque, Dict, Tuple

from fastapi import HTTPException, Request, status

from app.core.config import get_settings


class InMemoryRateLimiter:
    """Simple per-client in-memory sliding-window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> Tuple[bool, int]:
        """
        Return (allowed, retry_after_seconds).
        retry_after_seconds is 0 when allowed.
        """
        now = monotonic()

        with self._lock:
            bucket = self._requests[key]
            while bucket and (now - bucket[0]) >= self.window_seconds:
                bucket.popleft()

            if len(bucket) >= self.max_requests:
                retry_after = int(max(1, self.window_seconds - (now - bucket[0])))
                return False, retry_after

            bucket.append(now)
            return True, 0


settings = get_settings()
_api_keys = set(settings.parse_csv_setting(settings.api_keys))

PUBLIC_PATH_PREFIXES = (
    "/",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
)


def is_public_path(path: str) -> bool:
    """Allow unauthenticated access to health/docs/root paths."""
    if path == "/":
        return True
    return any(path.startswith(prefix) for prefix in PUBLIC_PATH_PREFIXES[1:])


def get_client_identifier(request: Request) -> str:
    """Extract best-effort client identifier for rate limiting."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def require_api_key(request: Request) -> None:
    """Raise HTTP 401 when API key is missing/invalid on protected routes."""
    if is_public_path(request.url.path):
        return

    provided_key = request.headers.get(settings.api_key_header)
    if not provided_key or provided_key not in _api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
