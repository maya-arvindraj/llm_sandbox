from __future__ import annotations

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from core.config import get_settings


def configure_rate_limiter(
    app: FastAPI,
    limit_per_minute: int | None = None,
) -> None:
    """
    Attach a Redis-backed rate limiter to the app.

    The rate limit is enforced per session ID, which is already stored in Redis
    for the chat API. This keeps the limit consistent across app instances and
    matches the app's existing architecture.
    """

    settings = get_settings()
    rate_limit_per_minute = (
        limit_per_minute
        if limit_per_minute is not None
        else settings.rate_limit_per_minute
    )

    app.state.rate_limit_per_minute = rate_limit_per_minute
    app.state.rate_limit_window_seconds = 60
    app.state.rate_limit_enabled = rate_limit_per_minute > 0

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        if not getattr(app.state, "rate_limit_enabled", False):
            return await call_next(request)

        if request.url.path == "/health":
            return await call_next(request)

        session_id = (
            request.headers.get("x-session-id")
            or request.query_params.get("session_id")
            or ""
        ).strip()

        if not session_id:
            return await call_next(request)

        try:
            from dependencies import redis_client
        except Exception:
            return await call_next(request)

        if redis_client is None:
            return await call_next(request)

        key = f"rate_limit:session:{session_id}"
        current_count = await redis_client.incr(key)

        if current_count == 1:
            await redis_client.expire(key, app.state.rate_limit_window_seconds)

        if current_count > app.state.rate_limit_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        f"Rate limit exceeded for session {session_id}. "
                        f"Maximum {app.state.rate_limit_per_minute} requests per minute."
                    )
                },
            )

        return await call_next(request)
