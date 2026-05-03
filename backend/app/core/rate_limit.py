from __future__ import annotations

import time
from dataclasses import dataclass
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp


@dataclass
class Bucket:
    tokens: float
    updated_at: float


class TokenBucketLimiter:
    def __init__(self, capacity: int, refill_per_minute: int) -> None:
        self.capacity = float(capacity)
        self.refill_per_second = float(refill_per_minute) / 60.0
        self.buckets: dict[str, Bucket] = {}

    def allow(self, key: str, cost: float) -> bool:
        now = time.time()
        bucket = self.buckets.get(key, Bucket(tokens=self.capacity, updated_at=now))
        elapsed = now - bucket.updated_at
        bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.refill_per_second)
        bucket.updated_at = now
        if bucket.tokens < cost:
            self.buckets[key] = bucket
            return False
        bucket.tokens -= cost
        self.buckets[key] = bucket
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, capacity: int, refill_per_minute: int) -> None:
        super().__init__(app)
        self.limiter = TokenBucketLimiter(capacity=capacity, refill_per_minute=refill_per_minute)

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        client_host = request.client.host if request.client else "unknown"
        cost = self._cost_for_path(request.url.path)
        if not self.limiter.allow(client_host, cost):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": {
                        "code": "rate_limited",
                        "message": "Too many requests. Please wait a moment before trying again.",
                    }
                },
            )
        return await call_next(request)

    @staticmethod
    def _cost_for_path(path: str) -> float:
        if "resume" in path or "roadmap" in path:
            return 8.0
        if "mentor" in path:
            return 5.0
        if "github" in path or "leetcode" in path:
            return 3.0
        return 1.0
