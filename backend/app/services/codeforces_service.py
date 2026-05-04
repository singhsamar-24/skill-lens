from __future__ import annotations

from collections import Counter
from typing import Any

import httpx

from app.core.cache import cache
from app.core.settings import Settings
from app.models.codeforces import CodeforcesAnalysis, CodeforcesTopicCount


class CodeforcesService:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.settings = settings
        self.transport = transport

    async def analyze_user(self, username: str) -> CodeforcesAnalysis:
        cache_key = f"codeforces:{username.lower()}"
        cached = cache.get(cache_key)
        if isinstance(cached, CodeforcesAnalysis):
            return cached

        try:
            async with httpx.AsyncClient(
                base_url=self.settings.codeforces_api_base,
                timeout=self.settings.external_timeout_seconds,
                transport=self.transport,
            ) as client:
                info_payload = await self._get(client, "/user.info", {"handles": username})
                rating_payload = await self._get(client, "/user.rating", {"handle": username})
                status_payload = await self._get(client, "/user.status", {"handle": username})

            users = info_payload.get("result") or []
            if not users:
                return self._unavailable(username, "Codeforces profile was not available.")

            user = users[0]
            contests = rating_payload.get("result") or []
            submissions = status_payload.get("result") or []
            solved, attempted, accepted, topics = self._submission_stats(submissions)
            analysis = CodeforcesAnalysis(
                username=username,
                handle=user.get("handle", username),
                status="ok",
                rank=user.get("rank"),
                rating=user.get("rating"),
                max_rank=user.get("maxRank"),
                max_rating=user.get("maxRating"),
                contribution=user.get("contribution"),
                friend_of_count=user.get("friendOfCount"),
                contests=len(contests),
                solved_count=solved,
                attempted_count=attempted,
                accepted_submissions=accepted,
                topics=topics,
                problem_solving_signal=self._signal(solved, user.get("rating"), user.get("maxRating"), len(contests)),
            )
            cache.set(cache_key, analysis, ttl_seconds=30 * 60)
            return analysis
        except Exception as exc:
            return self._unavailable(username, f"Codeforces lookup failed: {exc.__class__.__name__}.")

    async def _get(self, client: httpx.AsyncClient, path: str, params: dict[str, str]) -> dict[str, Any]:
        response = await client.get(path, params=params)
        if response.status_code >= 400:
            raise httpx.HTTPStatusError("Codeforces API failure", request=response.request, response=response)
        payload = response.json()
        if payload.get("status") != "OK":
            comment = payload.get("comment") or "Codeforces API returned an error."
            raise ValueError(comment)
        return payload

    @staticmethod
    def _submission_stats(submissions: list[dict[str, Any]]) -> tuple[int, int, int, list[CodeforcesTopicCount]]:
        solved_keys: set[tuple[int | None, str]] = set()
        attempted_keys: set[tuple[int | None, str]] = set()
        accepted = 0
        tag_counter: Counter[str] = Counter()

        for submission in submissions:
            problem = submission.get("problem") or {}
            key = (problem.get("contestId"), str(problem.get("index") or problem.get("name") or ""))
            if not key[1]:
                continue
            attempted_keys.add(key)
            if submission.get("verdict") == "OK":
                accepted += 1
                if key not in solved_keys:
                    solved_keys.add(key)
                    tag_counter.update(str(tag) for tag in problem.get("tags") or [])

        topics = [
            CodeforcesTopicCount(topic=topic, solved=count)
            for topic, count in tag_counter.most_common(12)
            if topic
        ]
        return len(solved_keys), len(attempted_keys), accepted, topics

    @staticmethod
    def _signal(solved: int, rating: int | None, max_rating: int | None, contests: int) -> str:
        best_rating = max(value for value in [rating or 0, max_rating or 0])
        if best_rating >= 1600 or solved >= 300 or contests >= 35:
            return "strong"
        if best_rating >= 1200 or solved >= 100 or contests >= 12:
            return "moderate"
        if solved > 0 or contests > 0 or best_rating > 0:
            return "emerging"
        return "unknown"

    @staticmethod
    def _unavailable(username: str, warning: str) -> CodeforcesAnalysis:
        return CodeforcesAnalysis(username=username, status="unavailable", warning=warning)
