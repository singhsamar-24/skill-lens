from app.models.common import EvidenceItem, ResumeSkill, SkillEvidence
from app.models.compare import CompareRequest
from app.models.github import GitHubAnalysis
from app.models.resume import ResumeAnalysis
from app.services.compare_service import CompareService


def test_compare_normalizes_aliases_and_verifies_overlap():
    github = GitHubAnalysis(
        username="dev",
        profile_url="https://github.com/dev",
        public_repos=1,
        skills=[
            SkillEvidence(
                name="JavaScript",
                normalized="JavaScript",
                level="strong",
                confidence=0.8,
                evidence=[EvidenceItem(source="repo", detail="JS code", weight=2)],
            )
        ],
    )
    resume = ResumeAnalysis(
        file_name="resume.pdf",
        text_preview="JS developer",
        skills=[ResumeSkill(name="JS", normalized="JavaScript", classification="claimed", confidence=0.75, evidence=["Listed JS"])],
    )

    result = CompareService().compare(CompareRequest(github=github, resume=resume, target_role="Frontend Engineer"))

    assert [skill.name for skill in result.verified_skills] == ["JavaScript"]
    assert result.claimed_unproven_skills == []
    assert result.evidence_score > 0
    assert result.insights
    assert result.career_matches
    assert all(match.match >= 0 for match in result.career_matches)


def test_compare_returns_explainable_gaps_and_role_matches_for_partial_profile():
    github = GitHubAnalysis(username="dev", profile_url="https://github.com/dev", public_repos=0)
    resume = ResumeAnalysis(
        file_name="resume.pdf",
        text_preview="Python backend developer",
        skills=[ResumeSkill(name="Python", normalized="Python", classification="project_backed", confidence=0.9, evidence=["Built APIs"])],
    )

    result = CompareService().compare(CompareRequest(github=github, resume=resume, target_role="Backend Engineer"))

    assert result.missing_skills
    assert all(skill.reason and skill.usage and skill.impact for skill in result.missing_skills)
    assert result.career_matches
    assert result.career_matches[0].salary
    assert result.career_matches[0].reason


def test_compare_handles_empty_resume_and_empty_github_without_crashing():
    github = GitHubAnalysis(username="dev", profile_url="https://github.com/dev", public_repos=0)
    resume = ResumeAnalysis(file_name="resume.pdf", text_preview="")

    result = CompareService().compare(CompareRequest(github=github, resume=resume, target_role="Software Engineer"))

    assert result.verified_skills == []
    assert result.claimed_unproven_skills == []
    assert result.github_only_skills == []
    assert result.missing_skills
    assert result.career_matches
    assert result.evidence_score >= 0
