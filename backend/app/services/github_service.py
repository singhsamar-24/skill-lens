from __future__ import annotations

import asyncio
import base64
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.cache import cache
from app.core.errors import SkillLensError
from app.core.normalization import normalize_skill
from app.core.settings import Settings
from app.models.common import EvidenceItem, SkillCredibility, SkillEvidence, WarningMessage
from app.models.github import CommitEvidence, GitHubAnalysis, RateLimitInfo, RepositoryEvidence
from app.services.skill_catalog import keyword_skill_hits


class GitHubService:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.settings = settings
        self.transport = transport
        self._semaphore = asyncio.Semaphore(6)

    async def analyze_user(self, username: str) -> GitHubAnalysis:
        cache_key = f"github:{username.lower()}"
        stale = cache.peek(cache_key)
        cached = cache.get(cache_key)
        if isinstance(cached, GitHubAnalysis):
            return cached

        try:
            async with httpx.AsyncClient(
                base_url=self.settings.github_api_base,
                timeout=self.settings.external_timeout_seconds,
                headers=self._headers(),
                transport=self.transport,
            ) as client:
                profile, rate = await self._get(client, f"/users/{username}")
                repos, rate = await self._get(
                    client,
                    f"/users/{username}/repos",
                    params={"type": "owner", "sort": "pushed", "direction": "desc", "per_page": 40},
                )

                selected = self._select_repositories(repos)
                repo_evidence = await self._analyze_repositories(client, selected)
                language_totals = self._language_totals(repo_evidence)
                skills = self._derive_skills(repo_evidence, language_totals)

                warnings: list[WarningMessage] = []
                if not selected:
                    warnings.append(WarningMessage(code="github_no_repos", message="No public non-fork repositories were found."))
                if len(repos) > len(selected):
                    warnings.append(
                        WarningMessage(
                            code="github_limited_repos",
                            message=f"Analyzed {len(selected)} recently active repositories to respect GitHub API limits.",
                        )
                    )

                analysis = GitHubAnalysis(
                    username=username,
                    profile_url=profile.get("html_url", f"https://github.com/{username}"),
                    avatar_url=profile.get("avatar_url"),
                    public_repos=profile.get("public_repos", 0),
                    analyzed_repos=repo_evidence,
                    language_totals=language_totals,
                    skills=skills,
                    warnings=warnings,
                    rate_limit=rate,
                )
                cache.set(cache_key, analysis, ttl_seconds=30 * 60)
                return analysis
        except SkillLensError as exc:
            if exc.detail.get("code") == "github_rate_limited" and isinstance(stale, GitHubAnalysis):
                stale.warnings.append(
                    WarningMessage(
                        code="github_cached_fallback",
                        message="GitHub rate limit was reached, so SkillLens reused the last cached analysis.",
                    )
                )
                return stale
            raise

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "SkillLens-MVP",
        }
        if self.settings.github_token:
            headers["Authorization"] = f"Bearer {self.settings.github_token}"
        return headers

    async def _get(self, client: httpx.AsyncClient, path: str, params: dict[str, Any] | None = None) -> tuple[Any, RateLimitInfo]:
        async with self._semaphore:
            response = await client.get(path, params=params)
        rate = RateLimitInfo(
            remaining=self._int_header(response, "x-ratelimit-remaining"),
            reset_epoch=self._int_header(response, "x-ratelimit-reset"),
            resource=response.headers.get("x-ratelimit-resource"),
        )
        if response.status_code in {403, 429} and response.headers.get("x-ratelimit-remaining") == "0":
            raise SkillLensError("github_rate_limited", "GitHub API rate limit reached. Try again later.", 429)
        if response.status_code == 404:
            raise SkillLensError("github_not_found", "GitHub user or repository was not found.", 404)
        if response.status_code >= 400:
            raise SkillLensError("github_api_failure", "GitHub API request failed.", 502)
        return response.json(), rate

    @staticmethod
    def _int_header(response: httpx.Response, name: str) -> int | None:
        value = response.headers.get(name)
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def _select_repositories(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
        candidates = [repo for repo in repos if not repo.get("fork") and not repo.get("archived")]
        return sorted(
            candidates,
            key=lambda repo: (repo.get("pushed_at") or "", repo.get("stargazers_count") or 0),
            reverse=True,
        )[:12]

    async def _analyze_repositories(self, client: httpx.AsyncClient, repos: list[dict[str, Any]]) -> list[RepositoryEvidence]:
        commit_limits: list[int] = []
        remaining = 30
        for repo in repos:
            per_repo = min(5, remaining)
            commit_limits.append(per_repo)
            remaining -= per_repo
        return list(await asyncio.gather(*(self._analyze_repository(client, repo, limit) for repo, limit in zip(repos, commit_limits))))

    async def _analyze_repository(self, client: httpx.AsyncClient, repo: dict[str, Any], commit_limit: int) -> RepositoryEvidence:
        owner = repo["owner"]["login"]
        name = repo["name"]
        languages: dict[str, int] = {}
        readme_excerpt: str | None = None
        commits: list[CommitEvidence] = []

        try:
            languages_data, _ = await self._get(client, f"/repos/{owner}/{name}/languages")
            languages = {str(k): int(v) for k, v in languages_data.items()}
        except SkillLensError:
            languages = {}

        try:
            readme, _ = await self._get(client, f"/repos/{owner}/{name}/readme")
            if isinstance(readme, dict):
                raw_content = readme.get("content") or ""
                try:
                    decoded = base64.b64decode(raw_content).decode("utf-8", errors="ignore")
                except Exception:
                    decoded = repo.get("description") or ""
                readme_excerpt = decoded[:500]
            elif isinstance(readme, str):
                readme_excerpt = readme[:500]
        except SkillLensError:
            readme_excerpt = repo.get("description")

        if commit_limit > 0:
            try:
                commit_data, _ = await self._get(
                    client,
                    f"/repos/{owner}/{name}/commits",
                    params={"per_page": commit_limit},
                )
                for item in commit_data[:commit_limit]:
                    commit = item.get("commit", {})
                    commits.append(
                        CommitEvidence(
                            message=(commit.get("message") or "").splitlines()[0][:160],
                            url=item.get("html_url", repo.get("html_url")),
                            date=(commit.get("author") or {}).get("date"),
                        )
                    )
            except SkillLensError:
                pass

        return RepositoryEvidence(
            name=name,
            full_name=repo.get("full_name", f"{owner}/{name}"),
            url=repo.get("html_url", f"https://github.com/{owner}/{name}"),
            description=repo.get("description"),
            stars=repo.get("stargazers_count", 0),
            forks=repo.get("forks_count", 0),
            pushed_at=repo.get("pushed_at"),
            languages=languages,
            topics=repo.get("topics") or [],
            readme_excerpt=readme_excerpt,
            commits=commits,
        )

    @staticmethod
    def _language_totals(repos: list[RepositoryEvidence]) -> dict[str, int]:
        totals: dict[str, int] = defaultdict(int)
        for repo in repos:
            for language, amount in repo.languages.items():
                totals[normalize_skill(language)] += amount
        return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def _derive_skills(repos: list[RepositoryEvidence], language_totals: dict[str, int]) -> list[SkillEvidence]:
        evidence: dict[str, list[EvidenceItem]] = defaultdict(list)
        skill_repos: dict[str, set[str]] = defaultdict(set)
        skill_repo_commits: dict[str, dict[str, int]] = defaultdict(dict)
        skill_recent_repos: dict[str, set[str]] = defaultdict(set)
        skill_last_seen: dict[str, str] = {}
        language_share: dict[str, float] = defaultdict(float)

        total_bytes = sum(language_totals.values()) or 1
        repo_by_name = {repo.full_name: repo for repo in repos}

        for repo in repos:
            recent = GitHubService._is_recent(repo.pushed_at)
            for language, amount in repo.languages.items():
                skill = normalize_skill(language)
                share = amount / total_bytes
                language_share[skill] += share
                GitHubService._record_skill_repo(skill, repo, recent, skill_repos, skill_repo_commits, skill_recent_repos, skill_last_seen)

            combined_text = " ".join(
                [
                    repo.name,
                    repo.description or "",
                    " ".join(repo.topics),
                    repo.readme_excerpt or "",
                    " ".join(commit.message for commit in repo.commits),
                ]
            )
            for skill in keyword_skill_hits(combined_text):
                GitHubService._record_skill_repo(skill, repo, recent, skill_repos, skill_repo_commits, skill_recent_repos, skill_last_seen)
                evidence[skill].append(EvidenceItem(source=repo.full_name, detail=f"Found {skill} signals in repository metadata or README.", url=repo.url, weight=2.0))

        for skill, share in language_share.items():
            evidence[skill].insert(
                0,
                EvidenceItem(
                    source="language",
                    detail=f"{skill} represents {share:.0%} of analyzed code across {len(skill_repos[skill])} repositories.",
                    weight=min(5.0, 1.0 + share * 8),
                ),
            )

        output: list[SkillEvidence] = []
        all_skills = set(skill_repos) | set(language_share)
        for skill in all_skills:
            repo_count = len(skill_repos[skill])
            commit_count = sum(skill_repo_commits[skill].values())
            recent_count = len(skill_recent_repos[skill])
            share = min(1.0, language_share.get(skill, 0.0))
            score = GitHubService._credibility_score(repo_count, commit_count, recent_count, share)
            if score >= 72:
                level = "strong"
            elif score >= 42:
                level = "moderate"
            else:
                level = "exposure"
            repo_names = sorted(skill_repos[skill])
            if repo_names:
                example_repo = repo_by_name.get(repo_names[0])
                evidence[skill].append(
                    EvidenceItem(
                        source="activity",
                        detail=f"{repo_count} repos, {commit_count} recent commits, {recent_count} recently updated repos support this signal.",
                        url=example_repo.url if example_repo else None,
                        weight=3.0,
                    )
                )
            output.append(
                SkillEvidence(
                    name=skill,
                    normalized=normalize_skill(skill),
                    level=level,
                    confidence=score / 100,
                    credibility=SkillCredibility(
                        score=score,
                        repo_count=repo_count,
                        commit_count=commit_count,
                        recent_repo_count=recent_count,
                        language_share=share,
                        last_seen_at=skill_last_seen.get(skill),
                    ),
                    evidence=evidence[skill][:5],
                )
            )
        return sorted(output, key=lambda item: item.credibility.score, reverse=True)[:18]

    @staticmethod
    def _record_skill_repo(
        skill: str,
        repo: RepositoryEvidence,
        recent: bool,
        skill_repos: dict[str, set[str]],
        skill_repo_commits: dict[str, dict[str, int]],
        skill_recent_repos: dict[str, set[str]],
        skill_last_seen: dict[str, str],
    ) -> None:
        skill_repos[skill].add(repo.full_name)
        skill_repo_commits[skill][repo.full_name] = len(repo.commits)
        if recent:
            skill_recent_repos[skill].add(repo.full_name)
        if repo.pushed_at and (skill not in skill_last_seen or repo.pushed_at > skill_last_seen[skill]):
            skill_last_seen[skill] = repo.pushed_at

    @staticmethod
    def _is_recent(pushed_at: str | None) -> bool:
        if not pushed_at:
            return False
        try:
            pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        except ValueError:
            return False
        return (datetime.now(timezone.utc) - pushed).days <= 365

    @staticmethod
    def _credibility_score(repo_count: int, commit_count: int, recent_repo_count: int, language_share_value: float) -> int:
        language_component = min(40.0, language_share_value * 100)
        repo_component = min(25.0, repo_count * 8.0)
        commit_component = min(20.0, commit_count * 1.5)
        recency_component = min(15.0, recent_repo_count * 5.0)
        score = int(round(language_component + repo_component + commit_component + recency_component))
        return max(8 if repo_count else 0, min(98, score))
