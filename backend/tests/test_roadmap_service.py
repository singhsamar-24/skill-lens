from app.models.compare import CompareResponse, MissingSkill
from app.models.roadmap import MarketRoadmapRequest, RoadmapRequest
from app.services.market_roadmap_service import MarketRoadmapService
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


def test_market_roadmap_scores_company_fit_from_user_skills():
    service = MarketRoadmapService(groq=None)

    response = service._fallback_response(
        ["Python", "FastAPI", "PostgreSQL", "REST APIs"],
        service.get_company_profiles("Backend Engineer")[:2],
    )

    assert response.companies
    assert response.companies[0].fit > 0
    assert response.companies[0].salary
    assert response.companies[0].process
    assert response.companies[0].prep_plan


def test_market_roadmap_supports_frontend_role_alias():
    service = MarketRoadmapService(groq=None)

    response = service._fallback_response(
        [{"name": "React", "weight": 1.2}, {"name": "TypeScript", "weight": 1.1}],
        service.get_company_profiles("Frontend Engineer")[:1],
    )

    assert response.companies[0].fit >= 20
