import httpx
import jwt
import time

from app.connectors.base import BaseConnector


class GhostConnector(BaseConnector):

    def __init__(self, base_url: str, admin_api_key: str):
        self.base_url = base_url.rstrip("/")
        self.admin_api_key = admin_api_key

    def validate(self) -> bool:
        return bool(self.base_url and ":" in self.admin_api_key)

    def generate_token(self) -> str:
        key_id, secret = self.admin_api_key.split(":")

        iat = int(time.time())

        return jwt.encode(
            {
                "iat": iat,
                "exp": iat + 300,
                "aud": "/admin/"
            },
            bytes.fromhex(secret),
            algorithm="HS256",
            headers={"kid": key_id}
        )

    def publish(self, content: dict) -> dict:
        token = self.generate_token()

        headers = {
            "Authorization": f"Ghost {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "posts": [{
                "title": content["title"],
                "html": content["body"],
                "status": "draft"
            }]
        }

        try:
            response = httpx.post(
                f"{self.base_url}/ghost/api/admin/posts/?source=html",
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