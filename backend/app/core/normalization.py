import re


ALIASES = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "react.js": "React",
    "reactjs": "React",
    "react": "React",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "py": "Python",
    "python": "Python",
    "fastapi": "FastAPI",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "llm": "LLMs",
    "llms": "LLMs",
    "rag": "RAG",
    "retrieval augmented generation": "RAG",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "github actions": "GitHub Actions",
    "apis": "REST APIs",
    "api": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "database": "Databases",
    "databases": "Databases",
    "db": "Databases",
    "sql": "SQL",
    "cache": "Caching",
    "caching": "Caching",
    "vector db": "Vector Databases",
    "vector database": "Vector Databases",
    "vector databases": "Vector Databases",
    "data pipeline": "Data Pipelines",
    "data pipelines": "Data Pipelines",
    "monitoring": "Monitoring",
    "prompt engineering": "Prompt Engineering",
    "model evaluation": "Model Evaluation",
    "system design": "System Design Fundamentals",
    "system design fundamentals": "System Design Fundamentals",
}


def normalize_skill(name: str) -> str:
    compact = re.sub(r"\s+", " ", name.strip()).strip(" .,_-")
    key = compact.lower()
    return ALIASES.get(key, compact[:1].upper() + compact[1:] if compact else compact)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
