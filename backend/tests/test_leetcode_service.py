import httpx
import pytest

from app.core.settings import Settings
from app.services.leetcode_service import LeetCodeService


@pytest.mark.asyncio
async def test_leetcode_unavailable_degrades_cleanly():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"errors": [{"message": "blocked"}]})

    service = LeetCodeService(
        Settings(leetcode_graphql_url="https://leetcode.test/graphql"),
        transport=httpx.MockTransport(handler),
    )

    result = await service.analyze_user("blocked")

    assert result.status == "unavailable"
    assert result.problem_solving_signal == "unknown"
    assert result.warning
