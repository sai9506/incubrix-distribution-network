import httpx

from app.connectors.base import BaseConnector


class LemmyConnector(BaseConnector):

    def __init__(self, base_url: str, auth_token: str, community_id: int):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.community_id = community_id

    def validate(self) -> bool:
        return bool(self.base_url and self.auth_token and self.community_id)

    def publish(self, content: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "post": {
                "name": content["title"],
                "body": content["body"],
                "community_id": self.community_id
            }
        }

        try:
            response = httpx.post(
                f"{self.base_url}/api/v3/post",
                headers=headers,
                json=payload,
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
            return {
                "status": "failed",
                "message": "Connection error"
            }