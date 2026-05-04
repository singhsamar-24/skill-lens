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
    "Vector Databases": ["vector database", "vector db", "faiss", "pinecone", "chroma", "qdrant", "embedding index"],
    "Prompt Engineering": ["prompt engineering", "prompt template", "few-shot", "tool calling", "structured output"],
    "Model Evaluation": ["eval", "evaluation", "benchmark", "hallucination", "groundedness"],
    "Data Structures": ["leetcode", "algorithm", "graph", "dynamic programming"],
    "REST APIs": ["rest", "api", "fastapi", "express", "endpoint"],
    "System Design Fundamentals": ["architecture", "scalable", "distributed", "cache", "queue"],
}


ROLE_SKILLS: dict[str, list[str]] = {
    "frontend": ["React", "TypeScript", "JavaScript", "Testing", "Tailwind CSS", "REST APIs"],
    "frontend engineer": ["React", "TypeScript", "JavaScript", "Testing", "Tailwind CSS", "REST APIs"],
    "backend": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "REST APIs", "System Design Fundamentals"],
    "backend engineer": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "REST APIs", "System Design Fundamentals"],
    "full stack": ["React", "TypeScript", "Node.js", "Python", "PostgreSQL", "REST APIs", "Docker"],
    "full stack engineer": ["React", "TypeScript", "Node.js", "Python", "PostgreSQL", "REST APIs", "Docker"],
    "ai engineer": ["Python", "LLMs", "RAG", "Vector Databases", "Prompt Engineering", "Model Evaluation", "FastAPI"],
    "software engineer": ["Python", "JavaScript", "REST APIs", "Data Structures", "Databases", "System Design Fundamentals"],
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
