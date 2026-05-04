from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import codeforces, compare, github, leetcode, mentor, resume, roadmap
from app.core.cache import cache
from app.core.rate_limit import RateLimitMiddleware
from app.core.settings import get_settings
from app.rag.manager import RAGManager
from app.services.compare_service import CompareService
from app.services.codeforces_service import CodeforcesService
from app.services.github_service import GitHubService
from app.services.groq_service import GroqService
from app.services.leetcode_service import LeetCodeService
from app.services.mentor_service import MentorService
from app.services.resume_service import ResumeService
from app.services.roadmap_service import RoadmapService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    rag = RAGManager(Path(__file__).parent / "data" / "rag")
    rag.build()

    groq_service = GroqService(settings)
    app.state.settings = settings
    app.state.rag = rag
    app.state.groq_service = groq_service
    app.state.github_service = GitHubService(settings)
    app.state.resume_service = ResumeService(settings, groq_service)
    app.state.leetcode_service = LeetCodeService(settings)
    app.state.codeforces_service = CodeforcesService(settings)
    app.state.compare_service = CompareService(groq_service)
    app.state.roadmap_service = RoadmapService(groq_service, rag)
    app.state.mentor_service = MentorService(rag, groq_service)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
    origins = [origin.strip() for origin in settings.frontend_origin.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        RateLimitMiddleware,
        capacity=settings.api_rate_limit_capacity,
        refill_per_minute=settings.api_rate_limit_refill_per_minute,
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": {"code": "http_error", "message": str(exc.detail)}},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": {"code": "internal_error", "message": "SkillLens encountered an unexpected error."}},
        )

    @app.get("/health")
    async def health():
        rag = getattr(app.state, "rag", None)
        return {
            "status": "ok",
            "rag_ready": bool(rag and rag.ready),
            "rag_backend": getattr(rag, "backend", "unknown"),
            "github_token_configured": bool(settings.github_token),
            "groq_configured": bool(settings.groq_api_key),
            "cache_items": cache.size(),
        }

    app.include_router(github.router, prefix=settings.api_prefix)
    app.include_router(resume.router, prefix=settings.api_prefix)
    app.include_router(leetcode.router, prefix=settings.api_prefix)
    app.include_router(codeforces.router, prefix=settings.api_prefix)
    app.include_router(compare.router, prefix=settings.api_prefix)
    app.include_router(roadmap.router, prefix=settings.api_prefix)
    app.include_router(mentor.router, prefix=settings.api_prefix)
    return app


app = create_app()
