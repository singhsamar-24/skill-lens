import httpx
import pytest

from app.core.settings import Settings
from app.services.codeforces_service import CodeforcesService


@pytest.mark.asyncio
async def test_codeforces_user_analysis_computes_solved_and_topics():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/user.info"):
            return httpx.Response(
                200,
                json={
                    "status": "OK",
                    "result": [
                        {
                            "handle": "tourist",
                            "rank": "legendary grandmaster",
                            "rating": 3800,
                            "maxRating": 3900,
                            "maxRank": "legendary grandmaster",
                            "contribution": 100,
                            "friendOfCount": 10,
                        }
                    ],
                },
            )
        if request.url.path.endswith("/user.rating"):
            return httpx.Response(200, json={"status": "OK", "result": [{"contestId": 1}, {"contestId": 2}]})
        return httpx.Response(
            200,
            json={
                "status": "OK",
                "result": [
                    {
                        "verdict": "OK",
                        "problem": {"contestId": 1, "index": "A", "name": "A", "tags": ["dp", "math"]},
                    },
                    {
                        "verdict": "WRONG_ANSWER",
                        "problem": {"contestId": 1, "index": "B", "name": "B", "tags": ["graphs"]},
                    },
                    {
                        "verdict": "OK",
                        "problem": {"contestId": 1, "index": "A", "name": "A", "tags": ["dp", "math"]},
                    },
                ],
            },
        )

    service = CodeforcesService(
        Settings(codeforces_api_base="https://codeforces.test/api"),
        transport=httpx.MockTransport(handler),
    )

    result = await service.analyze_user("tourist")

    assert result.status == "ok"
    assert result.solved_count == 1
    assert result.attempted_count == 2
    assert result.accepted_submissions == 2
    assert result.topics[0].topic == "dp"
    assert result.problem_solving_signal == "strong"


@pytest.mark.asyncio
async def test_codeforces_unavailable_degrades_cleanly():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "FAILED", "comment": "not found"})

    service = CodeforcesService(
        Settings(codeforces_api_base="https://codeforces.test/api"),
        transport=httpx.MockTransport(handler),
    )

    result = await service.analyze_user("missing")

    assert result.status == "unavailable"
    assert result.problem_solving_signal == "unknown"
    assert result.warning
