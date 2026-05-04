from app.models.compare import CompareResponse, MissingSkill
from app.models.roadmap import RoadmapRequest
from app.services.roadmap_service import RoadmapService


def test_seed_roadmap_specializes_broad_testing_and_system_design_gaps():
    comparison = CompareResponse(
        target_role="Backend Engineer",
        evidence_score=35,
        missing_skills=[
            MissingSkill(
                name="Testing",
                priority="medium",
                reason="Testing is needed for backend confidence.",
                usage=["CI quality gates"],
                impact="Reduces regressions.",
            ),
            MissingSkill(
                name="System Design",
                priority="medium",
                reason="System Design is needed for backend roles.",
                usage=["architecture reviews"],
                impact="Improves scalability decisions.",
            ),
        ],
    )

    service = RoadmapService(groq=None, rag=None)  # type: ignore[arg-type]
    roadmap = service._build_seed_roadmap(RoadmapRequest(comparison=comparison, target_role="Backend Engineer"))

    focus_names = [skill.skill for skill in roadmap.focus_skills]
    milestone_titles = [milestone.title for milestone in roadmap.milestones]

    assert "Testing" not in focus_names
    assert "System Design" not in focus_names
    assert "Automated quality engineering" in focus_names
    assert "Scalable service architecture" in focus_names
    assert "Build a regression-safe delivery pipeline" in milestone_titles
    assert "Design and ship a scalable service slice" in milestone_titles
    assert all(len(milestone.tasks) >= 3 for milestone in roadmap.milestones)


def test_seed_roadmap_falls_back_to_case_study_when_no_gaps_exist():
    comparison = CompareResponse(target_role="Software Engineer", evidence_score=88)

    service = RoadmapService(groq=None, rag=None)  # type: ignore[arg-type]
    roadmap = service._build_seed_roadmap(RoadmapRequest(comparison=comparison, target_role="Software Engineer"))

    assert roadmap.focus_skills[0].skill == "Software Engineer portfolio proof"
    assert "case study" in roadmap.portfolio_projects[0].lower()
