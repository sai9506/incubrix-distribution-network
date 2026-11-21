import httpx

from app.connectors.base import BaseConnector


class DiscourseConnector(BaseConnector):

    def __init__(self, base_url: str, api_key: str, username: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.username = username

    def validate(self) -> bool:
        return bool(self.base_url and self.api_key and self.username)

    def publish(self, content: dict) -> dict:
        headers = {
            "Api-Key": self.api_key,
            "Api-Username": self.username,
            "Content-Type": "application/json"
        }

        payload = {
            "title": content["title"],
            "raw": content["body"],
            "category": content.get("category_id")
        }

        try:
            response = httpx.post(
                f"{self.base_url}/posts.json",
                headers=headers,
                data=payload,
                timeout=15
            )

            if response.is_success:
                return {
                    "status": "success",
                    "response": response.json()
                }

            return {
                "status": "failed",
                "status_code": response.status_code
            }

        except httpx.RequestError:
            return {"status": "failed", "message": "Connection error"}