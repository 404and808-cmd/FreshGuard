
import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class TavilyClient:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = os.getenv(
            "TAVILY_BASE_URL",
            "https://api.tavily.com",
        )

        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is missing from .env")

    async def search(self, query: str, max_results: int = 5) -> dict:
        payload = {
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": False,
            "include_raw_content": False,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/search",
                json=payload,
                headers=headers,
            )

            response.raise_for_status()
            return response.json()
