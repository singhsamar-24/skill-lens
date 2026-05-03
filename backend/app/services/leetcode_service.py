from __future__ import annotations

import httpx

from app.core.cache import cache
from app.core.settings import Settings
from app.models.leetcode import LeetCodeAnalysis, TopicCount


class LeetCodeService:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.settings = settings
        self.transport = transport

    async def analyze_user(self, username: str) -> LeetCodeAnalysis:
        cache_key = f"leetcode:{username.lower()}"
        cached = cache.get(cache_key)
        if isinstance(cached, LeetCodeAnalysis):
            return cached

        query = """
        query userProfileUserQuestionProgressV2($userSlug: String!) {
          userProfileUserQuestionProgressV2(userSlug: $userSlug) {
            numAcceptedQuestions { count difficulty }
          }
          matchedUser(username: $userSlug) {
            profile { ranking }
            tagProblemCounts { advanced { tagName problemsSolved } intermediate { tagName problemsSolved } fundamental { tagName problemsSolved } }
          }
        }
        """
        try:
            async with httpx.AsyncClient(timeout=self.settings.external_timeout_seconds, transport=self.transport) as client:
                response = await client.post(
                    self.settings.leetcode_graphql_url,
                    json={"query": query, "variables": {"userSlug": username}},
                    headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"},
                )
            if response.status_code >= 400:
                return self._unavailable(username, f"LeetCode returned HTTP {response.status_code}.")
            payload = response.json()
            progress = payload.get("data", {}).get("userProfileUserQuestionProgressV2")
            matched = payload.get("data", {}).get("matchedUser")
            if not progress or not matched:
                return self._unavailable(username, "LeetCode profile was not available.")

            counts = {item["difficulty"].lower(): int(item["count"]) for item in progress.get("numAcceptedQuestions", [])}
            total = sum(counts.values())
            topics = self._topics(matched.get("tagProblemCounts") or {})
            analysis = LeetCodeAnalysis(
                username=username,
                status="ok",
                total_solved=total,
                easy_solved=counts.get("easy", 0),
                medium_solved=counts.get("medium", 0),
                hard_solved=counts.get("hard", 0),
                ranking=(matched.get("profile") or {}).get("ranking"),
                topics=topics,
                problem_solving_signal=self._signal(total, counts.get("medium", 0), counts.get("hard", 0)),
            )
            cache.set(cache_key, analysis, ttl_seconds=30 * 60)
            return analysis
        except Exception as exc:
            return self._unavailable(username, f"LeetCode lookup failed: {exc.__class__.__name__}.")

    @staticmethod
    def _topics(tag_counts: dict) -> list[TopicCount]:
        output: list[TopicCount] = []
        for group_name in ("advanced", "intermediate", "fundamental"):
            for item in tag_counts.get(group_name, []) or []:
                solved = int(item.get("problemsSolved") or 0)
                if solved > 0:
                    output.append(TopicCount(topic=item.get("tagName", "Unknown"), solved=solved))
        return sorted(output, key=lambda item: item.solved, reverse=True)[:12]

    @staticmethod
    def _signal(total: int, medium: int, hard: int) -> str:
        if total >= 250 or hard >= 30:
            return "strong"
        if total >= 80 or medium >= 50:
            return "moderate"
        if total > 0:
            return "emerging"
        return "unknown"

    @staticmethod
    def _unavailable(username: str, warning: str) -> LeetCodeAnalysis:
        return LeetCodeAnalysis(username=username, status="unavailable", warning=warning)
