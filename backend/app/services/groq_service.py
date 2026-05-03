from __future__ import annotations

import asyncio
import json
import re
from typing import Any

import httpx

from app.core.errors import unavailable
from app.core.settings import Settings


class GroqService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._semaphore = asyncio.Semaphore(3)

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: int = 1800,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        if not self.settings.groq_api_key:
            raise unavailable("groq_unavailable", "GROQ_API_KEY is not configured.")

        payload = {
            "model": self.settings.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
        }
        text = await self._post_chat_completion(payload)
        return self._parse_json(text)

    async def complete_text(self, system_prompt: str, user_prompt: str, *, max_tokens: int = 1400) -> str:
        if not self.settings.groq_api_key:
            raise unavailable("groq_unavailable", "GROQ_API_KEY is not configured.")

        payload = {
            "model": self.settings.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.25,
            "max_completion_tokens": max_tokens,
        }
        return await self._post_chat_completion(payload)

    async def _post_chat_completion(self, payload: dict[str, Any]) -> str:
        headers = {
            "Authorization": f"Bearer {self.settings.groq_api_key}",
            "Content-Type": "application/json",
        }
        async with self._semaphore:
            async with httpx.AsyncClient(timeout=self.settings.external_timeout_seconds) as client:
                for attempt in range(2):
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    if response.status_code in {429, 500, 502, 503, 504} and attempt == 0:
                        await asyncio.sleep(0.8)
                        continue
                    if response.status_code >= 400:
                        raise unavailable("groq_unavailable", "Groq API request failed.")
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
        raise unavailable("groq_unavailable", "Groq API request failed.")

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if not match:
                raise unavailable("groq_unavailable", "Groq returned non-JSON output.")
            return json.loads(match.group(0))
