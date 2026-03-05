import httpx
import json
from typing import List, Dict, Any

class GitHubClient:
    def __init__(self, token: str, repository: str):
        self.repository = repository
        self.base_url = f"https://api.github.com/repos/{repository}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def get_pr_diff(self, pr_number: int) -> str:
        async with httpx.AsyncClient(headers={"Authorization": self.headers["Authorization"], "Accept": "application/vnd.github.v3.diff"}) as client:
            resp = await client.get(f"{self.base_url}/pulls/{pr_number}")
            resp.raise_for_status()
            return resp.text

    async def get_pr_metadata(self, pr_number: int) -> Dict[str, Any]:
        async with httpx.AsyncClient(headers=self.headers) as client:
            resp = await client.get(f"{self.base_url}/pulls/{pr_number}")
            resp.raise_for_status()
            return resp.json()

    async def create_review(self, pr_number: int, comments: List[Dict[str, Any]], body: str, event: str = "COMMENT"):
        # comments: list of {path, line, side, body}
        async with httpx.AsyncClient(headers=self.headers) as client:
            payload = {
                "body": body,
                "event": event,
                "comments": comments
            }
            resp = await client.post(f"{self.base_url}/pulls/{pr_number}/reviews", json=payload)
            resp.raise_for_status()
            return resp.json()
