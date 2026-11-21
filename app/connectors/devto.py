
import httpx

from app.connectors.base import BaseConnector


class DevToConnector(BaseConnector):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://dev.to"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def publish(self, content: dict) -> dict:
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

        article = {
            "title": content["title"],
            "body_markdown": content.get("body", ""),
            "published": False,
            "tags": content.get("tags", [])[:4]
        }

        payload = {"article": article}

        try:
            response = httpx.post(
                f"{self.base_url}/api/articles",
                headers=headers,
                json=payload,
                timeout=10
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
            return {
                "status": "failed",
                "message": "Dev.to request failed"
            }

    def validate(self) -> bool:
        return bool(self.api_key and self.base_url)
