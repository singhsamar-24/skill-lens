from fastapi.testclient import TestClient

from app.main import create_app
from app.models.codeforces import CodeforcesAnalysis
from app.models.compare import CompareResponse
from app.models.github import GitHubAnalysis
from app.models.leetcode import LeetCodeAnalysis
from app.models.mentor import MentorChatResponse
from app.models.resume import ResumeAnalysis
from app.models.roadmap import RoadmapResponse
from app.rag.manager import RAGManager


def test_health_endpoint(monkeypatch):
    monkeypatch.setattr(RAGManager, "_load_model", staticmethod(lambda: None))
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["rag_ready"] is True


def test_public_api_endpoints_with_mocked_services(monkeypatch):
    monkeypatch.setattr(RAGManager, "_load_model", staticmethod(lambda: None))
    app = create_app()

    github = GitHubAnalysis(username="dev", profile_url="https://github.com/dev", public_repos=0)
    resume = ResumeAnalysis(file_name="resume.pdf", text_preview="resume")
    leetcode = LeetCodeAnalysis(username="dev", status="unavailable", warning="mocked")
    codeforces = CodeforcesAnalysis(username="dev", status="unavailable", warning="mocked")
    comparison = CompareResponse(target_role="Software Engineer", evidence_score=42, problem_solving_signal="unknown")
    roadmap = RoadmapResponse(target_role="Software Engineer", mentor_note="mocked")
    mentor = MentorChatResponse(routed_sources=["learning"], answer="mocked", citations=[], snippets=[])

    class GitHubFake:
        async def analyze_user(self, username: str):
            return github.model_copy(update={"username": username})

    class ResumeFake:
        async def analyze_upload(self, file):
            return resume.model_copy(update={"file_name": file.filename})

    class LeetCodeFake:
        async def analyze_user(self, username: str):
            return leetcode.model_copy(update={"username": username})

    class CodeforcesFake:
        async def analyze_user(self, username: str):
            return codeforces.model_copy(update={"username": username})

    class RoadmapFake:
        async def generate(self, _payload):
            return roadmap

    class MentorFake:
        async def chat(self, _payload):
            return mentor

    with TestClient(app) as client:
        app.state.github_service = GitHubFake()
        app.state.resume_service = ResumeFake()
        app.state.leetcode_service = LeetCodeFake()
        app.state.codeforces_service = CodeforcesFake()
        app.state.roadmap_service = RoadmapFake()
        app.state.mentor_service = MentorFake()

        assert client.post("/api/github/analyze", json={"username": "dev"}).json()["username"] == "dev"
        assert client.post("/api/resume/analyze", files={"file": ("resume.pdf", b"%PDF", "application/pdf")}).json()["file_name"] == "resume.pdf"
        assert client.post("/api/leetcode/analyze", json={"username": "dev"}).json()["status"] == "unavailable"
        assert client.post("/api/codeforces/analyze", json={"username": "dev"}).json()["status"] == "unavailable"

        compare_body = client.post("/api/compare", json={"github": github.model_dump(), "resume": resume.model_dump(), "target_role": "Software Engineer"}).json()
        assert "evidence_score" in compare_body

        assert client.post("/api/roadmap", json={"comparison": comparison.model_dump(), "target_role": "Software Engineer"}).json()["mentor_note"] == "mocked"
        assert client.post("/api/mentor/chat", json={"message": "how do I learn testing?"}).json()["answer"] == "mocked"
