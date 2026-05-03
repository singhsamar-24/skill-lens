from __future__ import annotations

from app.models.mentor import MentorChatRequest, MentorChatResponse
from app.rag.manager import RAGManager
from app.services.groq_service import GroqService


class MentorService:
    def __init__(self, rag: RAGManager, groq: GroqService) -> None:
        self.rag = rag
        self.groq = groq

    async def chat(self, request: MentorChatRequest) -> MentorChatResponse:
        routed, route_reason = self.rag.route_with_reason(request.message, request.sources)
        snippets = self.rag.retrieve(request.message, routed, top_k=5)
        context = "\n\n".join(
            f"Source={snippet.source_label}; Chunk={snippet.chunk_id}; Title={snippet.title}; Text={snippet.text}" for snippet in snippets
        )
        profile = request.profile_context or {}
        system = (
            "You are the SkillLens Principal Mentor. You provide high-signal, evidence-driven career strategy. "
            "Analyze the USER_QUESTION using both the provided RETRIEVED_CONTEXT and the user's specific PROFILE_CONTEXT. "
            "If the user has gaps, suggest specific code-based ways to prove those skills. "
            "If the user has verified strengths, explain how to articulate them for high-end engineering roles. "
            "Be direct, technically precise, and actionable. Cite source titles inline using [Title] format."
        )
        prompt = (
            f"USER_QUESTION: {request.message}\n\n"
            f"USER_PROFILE_CONTEXT:\n{profile}\n\n"
            f"RETRIEVED_KNOWLEDGE:\n{context}\n\n"
            f"Provide a strategic mentoring response that bridges their current evidence with their target career path."
        )
        answer = await self.groq.complete_text(system, prompt, max_tokens=1200)
        citations = list(dict.fromkeys(f"{snippet.source_label}: {snippet.title}" for snippet in snippets))
        return MentorChatResponse(routed_sources=routed, route_reason=route_reason, answer=answer, citations=citations, snippets=snippets)
