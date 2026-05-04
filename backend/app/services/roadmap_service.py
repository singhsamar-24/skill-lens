from __future__ import annotations

from collections.abc import Iterable

from pydantic import ValidationError

from app.core.normalization import normalize_skill
from app.models.compare import ComparedSkill, MissingSkill
from app.models.roadmap import RoadmapMilestone, RoadmapRequest, RoadmapResponse, RoadmapSkill
from app.rag.manager import RAGManager
from app.services.groq_service import GroqService


class RoadmapService:
    def __init__(self, groq: GroqService, rag: RAGManager) -> None:
        self.groq = groq
        self.rag = rag

    async def generate(self, request: RoadmapRequest) -> RoadmapResponse:
        seed = self._build_seed_roadmap(request)
        snippets = self.rag.retrieve(request.target_role + " roadmap required skills", ["learning", "job"], top_k=5)
        context = "\n\n".join(f"[{snippet.source}:{snippet.title}] {snippet.text}" for snippet in snippets)
        system = (
            "You are an elite Engineering Career Architect. You create high-fidelity, high-intensity skill roadmaps. "
            "Your goal is to turn gaps into provable expertise as quickly as possible. "
            "Build from the provided seed roadmap and keep every milestone project-specific. "
            "Do not repeat broad tracks such as Testing or System Design as standalone weekly goals; specialize them into concrete work. "
            "Return strict JSON with keys: "
            "target_role, focus_skills, milestones, portfolio_projects, mentor_note. "
            "focus_skills items need skill, priority, rationale. "
            "milestones need week, title, tasks (at least 3 technical tasks), project, outcomes (measurable results). "
            "portfolio_projects should be specific shipped artifacts with repositories, demos, metrics, and README evidence. "
            "mentor_note should be encouraging yet professional, sounding like a senior principal engineer."
        )
        prompt = (
            f"TARGET_ROLE: {request.target_role}\n"
            f"IDENTIFIED GAPS & VERIFIED STATUS:\n{request.comparison.model_dump_json()}\n"
            f"RAG KNOWLEDGE CONTEXT:\n{context}\n\n"
            f"SEED_ROADMAP_TO_REFINE:\n{seed.model_dump_json()}\n\n"
            f"Create a 4-week aggressive acceleration roadmap to bridge these specific gaps. "
            f"Preserve the concrete skill tracks from the seed unless you make them more specific."
        )
        try:
            data = await self.groq.complete_json(system, prompt, max_tokens=2800, temperature=0.18)
            generated = RoadmapResponse.model_validate(data)
            return self._repair_response(generated, seed)
        except (ValidationError, Exception):
            return seed

    def _build_seed_roadmap(self, request: RoadmapRequest) -> RoadmapResponse:
        tracks = self._select_tracks(request)
        milestones = [
            RoadmapMilestone(
                week=f"Week {index + 1}",
                title=track["title"],
                tasks=track["tasks"],
                project=track["project"],
                outcomes=track["outcomes"],
            )
            for index, track in enumerate(tracks)
        ]
        return RoadmapResponse(
            target_role=request.target_role,
            focus_skills=[
                RoadmapSkill(skill=track["skill"], priority=track["priority"], rationale=track["rationale"])
                for track in tracks
            ],
            milestones=milestones,
            portfolio_projects=[track["project"] for track in tracks[:3]],
            mentor_note=(
                "Ship one visible artifact per week, keep the README evidence-heavy, and connect each commit to the exact hiring signal you are trying to prove."
            ),
        )

    def _select_tracks(self, request: RoadmapRequest) -> list[dict[str, object]]:
        tracks: list[dict[str, object]] = []
        used: set[str] = set()

        for skill in request.comparison.missing_skills:
            self._append_track(tracks, used, self._track_for_missing(skill, request.target_role))

        for skill in request.comparison.claimed_unproven_skills:
            self._append_track(tracks, used, self._track_for_claimed(skill, request.target_role))

        if len(tracks) < 4:
            for skill in request.comparison.github_only_skills:
                self._append_track(tracks, used, self._track_for_github_only(skill, request.target_role))

        if not tracks:
            self._append_track(tracks, used, self._generic_track(request.target_role))

        return tracks[:4]

    @staticmethod
    def _append_track(tracks: list[dict[str, object]], used: set[str], track: dict[str, object]) -> None:
        key = normalize_skill(str(track["skill"]))
        if key not in used:
            tracks.append(track)
            used.add(key)

    def _track_for_missing(self, skill: MissingSkill, role: str) -> dict[str, object]:
        template = self._template_for(skill.name, role)
        return {
            "skill": template["skill"],
            "priority": skill.priority,
            "rationale": f"{skill.reason} Prove it through {template['proof']}.",
            "title": template["title"],
            "tasks": template["tasks"],
            "project": template["project"],
            "outcomes": template["outcomes"],
        }

    def _track_for_claimed(self, skill: ComparedSkill, role: str) -> dict[str, object]:
        template = self._template_for(skill.name, role)
        return {
            "skill": f"Evidence-backed {template['skill']}",
            "priority": "medium",
            "rationale": f"{skill.name} is claimed but not strongly proven yet. Turn it into reviewable repository evidence.",
            "title": f"Prove {template['skill']} with repository evidence",
            "tasks": template["tasks"],
            "project": template["project"],
            "outcomes": template["outcomes"],
        }

    def _track_for_github_only(self, skill: ComparedSkill, role: str) -> dict[str, object]:
        template = self._template_for(skill.name, role)
        return {
            "skill": f"Resume-ready {template['skill']}",
            "priority": "low",
            "rationale": f"GitHub already shows {skill.name}; package that strength into recruiter-readable proof.",
            "title": f"Package {template['skill']} as a case study",
            "tasks": [
                *template["tasks"][:2],
                "Write a README case study with architecture, tradeoffs, screenshots, and measurable results.",
            ],
            "project": template["project"],
            "outcomes": template["outcomes"],
        }

    @staticmethod
    def _template_for(skill: str, role: str) -> dict[str, object]:
        normalized = normalize_skill(skill)
        role_l = role.lower()
        templates: dict[str, dict[str, object]] = {
            "Testing": {
                "skill": "Automated quality engineering",
                "title": "Build a regression-safe delivery pipeline",
                "proof": "unit, API, and end-to-end tests wired into CI",
                "project": "Production-style test suite for a role-relevant app with CI status badges and coverage notes",
                "tasks": [
                    "Add unit tests around core business logic and edge cases.",
                    "Add API or component integration tests for the highest-risk user flow.",
                    "Run the suite in CI and document what each test layer protects.",
                ],
                "outcomes": [
                    "A public repo with passing CI and clear test commands.",
                    "At least one critical flow protected by automated regression tests.",
                ],
            },
            "System Design": {
                "skill": "Scalable service architecture",
                "title": "Design and ship a scalable service slice",
                "proof": "architecture diagrams plus a working vertical slice",
                "project": "Scalable service case study with API boundaries, storage choices, caching, and failure-mode notes",
                "tasks": [
                    "Define the core entities, API contracts, and data flow for one production use case.",
                    "Implement a working vertical slice with logging, validation, and error handling.",
                    "Document tradeoffs for scale, latency, reliability, and operational failure modes.",
                ],
                "outcomes": [
                    "A README that explains architecture decisions like an engineering design review.",
                    "A deployed or runnable service slice that proves the design is executable.",
                ],
            },
            "System Design Fundamentals": {
                "skill": "Scalable service architecture",
                "title": "Design and ship a scalable service slice",
                "proof": "architecture diagrams plus a working vertical slice",
                "project": "Scalable service case study with API boundaries, storage choices, caching, and failure-mode notes",
                "tasks": [
                    "Define the core entities, API contracts, and data flow for one production use case.",
                    "Implement a working vertical slice with logging, validation, and error handling.",
                    "Document tradeoffs for scale, latency, reliability, and operational failure modes.",
                ],
                "outcomes": [
                    "A README that explains architecture decisions like an engineering design review.",
                    "A deployed or runnable service slice that proves the design is executable.",
                ],
            },
            "REST APIs": {
                "skill": "Production REST API design",
                "title": "Ship a typed API contract",
                "proof": "validated endpoints, examples, and integration tests",
                "project": "Role-specific REST API with OpenAPI docs, validation, pagination/filtering, and integration tests",
                "tasks": [
                    "Design resource models, request validation, and consistent error responses.",
                    "Implement CRUD plus one real workflow endpoint with realistic sample data.",
                    "Add API tests and a README section with curl examples and response contracts.",
                ],
                "outcomes": [
                    "A reviewer can run the API and understand its contract in under five minutes.",
                    "Resume-ready proof of backend/frontend integration skill.",
                ],
            },
            "Data Structures": {
                "skill": "Interview-grade problem solving",
                "title": "Create a problem-solving proof pack",
                "proof": "well-explained solutions and complexity analysis",
                "project": "Algorithms proof pack with 12 curated problems, tests, explanations, and complexity notes",
                "tasks": [
                    "Solve three role-relevant problems covering arrays/hash maps, graphs, and dynamic programming.",
                    "Add tests for edge cases and document time and space complexity.",
                    "Write short solution notes that explain the pattern, not just the code.",
                ],
                "outcomes": [
                    "A visible repo showing repeatable problem-solving technique.",
                    "Clear interview stories for algorithmic tradeoffs.",
                ],
            },
            "Docker": {
                "skill": "Containerized delivery",
                "title": "Make the project production-runnable",
                "proof": "Dockerized local setup and deployment notes",
                "project": "Containerized full-stack app with compose, health checks, environment docs, and one-command setup",
                "tasks": [
                    "Create Dockerfiles for the app services with minimal production images.",
                    "Add compose configuration for local dependencies and environment variables.",
                    "Document setup, health checks, and deployment tradeoffs.",
                ],
                "outcomes": [
                    "One-command local startup for reviewers.",
                    "Clear proof that the project can run outside your machine.",
                ],
            },
            "PostgreSQL": {
                "skill": "Relational data modeling",
                "title": "Model and query production data",
                "proof": "schema, migrations, indexed queries, and seed data",
                "project": "Database-backed product feature with migrations, relational constraints, indexes, and reporting queries",
                "tasks": [
                    "Design tables, relationships, constraints, and indexes for a realistic feature.",
                    "Implement migrations and seed data for repeatable review.",
                    "Add query examples that show filtering, joins, and aggregate reporting.",
                ],
                "outcomes": [
                    "A schema reviewers can inspect and run locally.",
                    "Evidence of data modeling beyond simple JSON storage.",
                ],
            },
        }
        if normalized in templates:
            return templates[normalized]
        if "front" in role_l and normalized in {"React", "TypeScript", "JavaScript"}:
            return {
                "skill": f"Production {normalized}",
                "title": f"Build a polished {normalized} feature",
                "proof": "a responsive feature with typed state, error states, and tests",
                "project": f"{normalized} dashboard feature with API integration, loading/error states, accessibility checks, and tests",
                "tasks": [
                    "Build the feature with typed data flow and reusable components.",
                    "Add loading, empty, and error states for real product behavior.",
                    "Verify accessibility and add component or integration tests.",
                ],
                "outcomes": [
                    "A polished demo that behaves like a real product screen.",
                    "Clear README evidence for frontend engineering depth.",
                ],
            }
        return {
            "skill": normalized,
            "title": f"Ship practical proof of {normalized}",
            "proof": "a focused feature with tests, docs, and measurable behavior",
            "project": f"{normalized} portfolio feature with implementation, tests, README evidence, and deployment notes",
            "tasks": [
                f"Build one realistic {normalized} feature tied to the target role.",
                "Add tests or validation for the riskiest behavior.",
                "Document architecture decisions, setup steps, and measurable results.",
            ],
            "outcomes": [
                f"Public evidence that shows practical {normalized} ability.",
                "A concise resume bullet with repo and outcome metrics.",
            ],
        }

    @staticmethod
    def _generic_track(role: str) -> dict[str, object]:
        return {
            "skill": f"{role} portfolio proof",
            "priority": "medium",
            "rationale": "No major gap was detected, so the next win is stronger packaging of visible project evidence.",
            "title": "Turn your strongest project into a case study",
            "tasks": [
                "Pick the strongest existing project and identify the main hiring signal it proves.",
                "Improve the README with architecture, screenshots, setup, and tradeoff notes.",
                "Add one measurable improvement such as tests, performance, accessibility, or deployment reliability.",
            ],
            "project": f"{role} case study repo with demo, architecture notes, and measurable proof",
            "outcomes": [
                "Recruiter-readable evidence for your strongest skill cluster.",
                "A polished project story ready for interviews.",
            ],
        }

    @staticmethod
    def _repair_response(generated: RoadmapResponse, seed: RoadmapResponse) -> RoadmapResponse:
        if len(generated.milestones) < 3 or RoadmapService._has_repeated_generic_tracks(generated):
            return seed

        return generated.model_copy(
            update={
                "focus_skills": RoadmapService._dedupe_focus(generated.focus_skills, seed.focus_skills),
                "milestones": RoadmapService._usable_milestones(generated.milestones, seed.milestones),
                "portfolio_projects": generated.portfolio_projects[:3] or seed.portfolio_projects,
            }
        )

    @staticmethod
    def _dedupe_focus(generated: list[RoadmapSkill], seed: list[RoadmapSkill]) -> list[RoadmapSkill]:
        focus: list[RoadmapSkill] = []
        seen: set[str] = set()
        for item in [*generated, *seed]:
            key = normalize_skill(item.skill)
            if key not in seen:
                focus.append(item)
                seen.add(key)
            if len(focus) == 4:
                break
        return focus

    @staticmethod
    def _usable_milestones(generated: list[RoadmapMilestone], seed: list[RoadmapMilestone]) -> list[RoadmapMilestone]:
        milestones = [
            milestone
            for milestone in generated
            if len(milestone.tasks) >= 3 and milestone.project.strip() and milestone.outcomes
        ]
        return (milestones or seed)[:4]

    @staticmethod
    def _has_repeated_generic_tracks(response: RoadmapResponse) -> bool:
        generic = {"Testing", "System Design", "System Design Fundamentals"}
        hits = [
            title
            for title in RoadmapService._roadmap_text(response)
            if any(word.lower() == title.strip().lower() for word in generic)
        ]
        focus_names = [item.skill for item in response.focus_skills]
        broad_focus = sum(1 for name in focus_names if normalize_skill(name) in generic)
        return len(hits) >= 2 or broad_focus >= 2

    @staticmethod
    def _roadmap_text(response: RoadmapResponse) -> Iterable[str]:
        for item in response.focus_skills:
            yield item.skill
        for milestone in response.milestones:
            yield milestone.title
            yield milestone.project
