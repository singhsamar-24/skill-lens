from __future__ import annotations

from app.core.normalization import normalize_skill


SKILL_KEYWORDS: dict[str, list[str]] = {
    "React": ["react", "jsx", "tsx", "vite", "next.js", "nextjs"],
    "TypeScript": ["typescript", "tsconfig", ".ts", ".tsx"],
    "JavaScript": ["javascript", "node", "npm", "vite", "webpack"],
    "Python": ["python", "fastapi", "django", "flask", "pytest", "pydantic"],
    "FastAPI": ["fastapi", "uvicorn", "pydantic"],
    "Node.js": ["node.js", "nodejs", "express", "npm"],
    "Tailwind CSS": ["tailwind", "tailwindcss"],
    "PostgreSQL": ["postgres", "postgresql", "sqlalchemy"],
    "MongoDB": ["mongodb", "mongoose"],
    "Docker": ["docker", "dockerfile", "compose"],
    "Kubernetes": ["kubernetes", "k8s", "helm"],
    "AWS": ["aws", "lambda", "s3", "ec2", "cloudfront"],
    "CI/CD": ["ci/cd", "github actions", "workflow", "pipeline"],
    "Testing": ["pytest", "vitest", "jest", "playwright", "testing-library"],
    "RAG": ["rag", "retrieval augmented generation", "faiss", "embedding"],
    "LLMs": ["llm", "groq", "openai", "langchain", "agent"],
    "Data Structures": ["leetcode", "algorithm", "graph", "dynamic programming"],
    "REST APIs": ["rest", "api", "fastapi", "express", "endpoint"],
    "System Design": ["architecture", "scalable", "distributed", "cache", "queue"],
}


ROLE_SKILLS: dict[str, list[str]] = {
    "frontend": ["React", "TypeScript", "JavaScript", "Testing", "Tailwind CSS", "REST APIs"],
    "frontend engineer": ["React", "TypeScript", "JavaScript", "Testing", "Tailwind CSS", "REST APIs"],
    "backend": ["Python", "FastAPI", "PostgreSQL", "Docker", "Testing", "REST APIs", "System Design"],
    "backend engineer": ["Python", "FastAPI", "PostgreSQL", "Docker", "Testing", "REST APIs", "System Design"],
    "full stack": ["React", "TypeScript", "Python", "FastAPI", "PostgreSQL", "Docker", "Testing", "REST APIs"],
    "full stack engineer": ["React", "TypeScript", "Python", "FastAPI", "PostgreSQL", "Docker", "Testing", "REST APIs"],
    "ai engineer": ["Python", "LLMs", "RAG", "FastAPI", "Testing", "System Design", "Docker"],
    "software engineer": ["Python", "JavaScript", "Testing", "REST APIs", "System Design", "Data Structures"],
}


def skills_for_role(role: str | None) -> list[str]:
    if not role:
        return ROLE_SKILLS["software engineer"]
    key = role.strip().lower()
    if key in ROLE_SKILLS:
        return ROLE_SKILLS[key]
    if "front" in key:
        return ROLE_SKILLS["frontend engineer"]
    if "back" in key:
        return ROLE_SKILLS["backend engineer"]
    if "full" in key:
        return ROLE_SKILLS["full stack engineer"]
    if "ai" in key or "ml" in key:
        return ROLE_SKILLS["ai engineer"]
    return ROLE_SKILLS["software engineer"]


def keyword_skill_hits(text: str) -> set[str]:
    lowered = text.lower()
    hits: set[str] = set()
    for skill, keywords in SKILL_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            hits.add(normalize_skill(skill))
    return hits
