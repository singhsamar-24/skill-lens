from fastapi.testclient import TestClient

from app.main import create_app
from app.models.codeforces import CodeforcesAnalysis
from app.models.compare import CompareResponse
from app.models.github import GitHubAnalysis
from app.models.leetcode import LeetCodeAnalysis
from app.models.mentor import MentorChatResponse
from app.models.recruiter import RecruiterEvaluateResponse, RecruiterRankResponse, RecruiterUploadResponse
from app.models.resume import ResumeAnalysis
from app.models.roadmap import MarketRoadmapResponse, RoadmapResponse
from app.rag.manager import RAGManager
from app.services.recruiter_service import RecruiterService


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
    market_roadmap = MarketRoadmapResponse(companies=[])
    mentor = MentorChatResponse(routed_sources=["learning"], answer="mocked", citations=[], snippets=[])
    recruiter_upload = RecruiterUploadResponse(uploaded=1, candidates=[])
    recruiter_evaluate = RecruiterEvaluateResponse(target_role="Software Engineer", evaluated=0, results=[])
    recruiter_rank = RecruiterRankResponse(target_role="Software Engineer", candidates=[])

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

    class MarketRoadmapFake:
        async def generate_company_roadmap(self, _payload):
            return market_roadmap

    class MentorFake:
        async def chat(self, _payload):
            return mentor

    class RecruiterFake:
        async def upload_resumes(self, _files):
            return recruiter_upload

        async def evaluate_candidates(self, _target_role):
            return recruiter_evaluate

        async def rank_candidates(self, _target_role=None):
            return recruiter_rank

    with TestClient(app) as client:
        app.state.github_service = GitHubFake()
        app.state.resume_service = ResumeFake()
        app.state.leetcode_service = LeetCodeFake()
        app.state.codeforces_service = CodeforcesFake()
        app.state.roadmap_service = RoadmapFake()
        app.state.market_roadmap_service = MarketRoadmapFake()
        app.state.mentor_service = MentorFake()
        app.state.recruiter_service = RecruiterFake()

        assert client.post("/api/github/analyze", json={"username": "dev"}).json()["username"] == "dev"
        assert client.post("/api/resume/analyze", files={"file": ("resume.pdf", b"%PDF", "application/pdf")}).json()["file_name"] == "resume.pdf"
        assert client.post("/api/leetcode/analyze", json={"username": "dev"}).json()["status"] == "unavailable"
        assert client.post("/api/codeforces/analyze", json={"username": "dev"}).json()["status"] == "unavailable"

        compare_body = client.post("/api/compare", json={"github": github.model_dump(), "resume": resume.model_dump(), "target_role": "Software Engineer"}).json()
        assert "evidence_score" in compare_body

        assert client.post("/api/roadmap", json={"comparison": comparison.model_dump(), "target_role": "Software Engineer"}).json()["mentor_note"] == "mocked"
        assert client.post("/api/roadmap/market", json={"target_role": "Backend Engineer", "user_skills": ["Python"]}).json()["companies"] == []
        assert client.post("/api/mentor/chat", json={"message": "how do I learn testing?"}).json()["answer"] == "mocked"
        assert client.post("/api/recruiter/upload", files=[("files", ("resume.pdf", b"%PDF", "application/pdf"))]).json()["uploaded"] == 1
        assert client.post("/api/recruiter/evaluate", json={"target_role": "Software Engineer"}).json()["evaluated"] == 0
        assert client.get("/api/recruiter/rank?target_role=Software%20Engineer").json()["target_role"] == "Software Engineer"


def test_recruiter_score_uses_selected_role_fit_not_only_github_evidence():
    comparison = CompareResponse(
        target_role="AI Engineer",
        evidence_score=0,
        career_matches=[
            {
                "role": "AI Engineer",
                "match": 29,
                "salary": "12-30 LPA",
                "reason": "Python is visible, but LLMs and RAG are missing.",
                "matched_skills": ["Python"],
                "missing_skills": ["LLMs", "RAG"],
            }
        ],
    )

    class CandidateStub:
        id = 1
        name = "Arjun Singh"
        email = None
        github_username = None

    result = RecruiterService._result_from_comparison(CandidateStub(), comparison)

    assert result.match_score == 29
    assert result.explanations["evidence_score"] == 0
    assert result.explanations["role_fit_score"] == 29
