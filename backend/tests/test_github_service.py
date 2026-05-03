import httpx
import pytest

from app.core.settings import Settings
from app.services.github_service import GitHubService


@pytest.mark.asyncio
async def test_github_no_repos_returns_stable_warning():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/users/empty":
            return httpx.Response(
                200,
                json={"login": "empty", "html_url": "https://github.com/empty", "public_repos": 0},
                headers={"x-ratelimit-remaining": "59"},
            )
        if request.url.path == "/users/empty/repos":
            return httpx.Response(200, json=[], headers={"x-ratelimit-remaining": "58"})
        return httpx.Response(404, json={})

    service = GitHubService(Settings(github_api_base="https://api.github.test"), transport=httpx.MockTransport(handler))
    result = await service.analyze_user("empty")

    assert result.analyzed_repos == []
    assert result.warnings[0].code == "github_no_repos"


@pytest.mark.asyncio
async def test_github_rate_limit_maps_to_stable_code():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"message": "rate limit"}, headers={"x-ratelimit-remaining": "0"})

    service = GitHubService(Settings(github_api_base="https://api.github.test"), transport=httpx.MockTransport(handler))

    with pytest.raises(Exception) as error:
        await service.analyze_user("limited")

    assert error.value.detail["code"] == "github_rate_limited"
