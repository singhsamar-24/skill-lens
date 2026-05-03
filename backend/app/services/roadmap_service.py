from __future__ import annotations

from pydantic import ValidationError

from app.models.roadmap import RoadmapMilestone, RoadmapRequest, RoadmapResponse, RoadmapSkill
from app.rag.manager import RAGManager
from app.services.groq_service import GroqService


class RoadmapService:
    def __init__(self, groq: GroqService, rag: RAGManager) -> None:
        self.groq = groq
        self.rag = rag

    async def generate(self, request: RoadmapRequest) -> RoadmapResponse:
        snippets = self.rag.retrieve(request.target_role + " roadmap required skills", ["learning", "job"], top_k=5)
        context = "\n\n".join(f"[{snippet.source}:{snippet.title}] {snippet.text}" for snippet in snippets)
        system = (
            "You are an elite Engineering Career Architect. You create high-fidelity, high-intensity skill roadmaps. "
            "Your goal is to turn gaps into provable expertise as quickly as possible. "
            "Return strict JSON with keys: "
            "target_role, focus_skills, milestones, portfolio_projects, mentor_note. "
            "focus_skills items need skill, priority, rationale. "
            "milestones need week, title, tasks (at least 3 technical tasks), project, outcomes (measurable results). "
            "portfolio_projects should be complex, full-stack/system-level project ideas that prove mastery. "
            "mentor_note should be encouraging yet professional, sounding like a senior principal engineer."
        )
        prompt = (
            f"TARGET_ROLE: {request.target_role}\n"
            f"IDENTIFIED GAPS & VERIFIED STATUS:\n{request.comparison.model_dump_json()}\n"
            f"RAG KNOWLEDGE CONTEXT:\n{context}\n\n"
            f"Create a 4-week aggressive acceleration roadmap to bridge these specific gaps."
        )
        data = await self.groq.complete_json(system, prompt, max_tokens=2800)
        try:
            return RoadmapResponse.model_validate(data)
        except ValidationError:
            missing = request.comparison.missing_skills[:4]
            return RoadmapResponse(
                target_role=request.target_role,
                focus_skills=[RoadmapSkill(skill=item.name, priority=item.priority, rationale=item.reason) for item in missing],
                milestones=[
                    RoadmapMilestone(
                        week=f"Week {index + 1}",
                        title=f"Prove {item.name}",
                        tasks=[f"Build a small {item.name} feature", "Write tests", "Document decisions in README"],
                        project=f"{item.name} evidence project",
                        outcomes=[f"Public repository showing {item.name}", "Resume bullet with measurable proof"],
                    )
                    for index, item in enumerate(missing[:4])
                ],
                portfolio_projects=["Evidence-first portfolio project based on the highest-priority missing skill."],
                mentor_note="Groq returned a malformed roadmap, so SkillLens generated a conservative validated fallback from the comparison gaps.",
            )
