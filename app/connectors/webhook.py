import hmac
import hashlib
import json
import os
import httpx

from app.connectors.base import BaseConnector


class WebhookConnector(BaseConnector):

    def __init__(self, webhook_url: str, secret: str):
        self.webhook_url = webhook_url
        self.secret = secret

    def generate_signature(self, payload: str) -> str:
        signature = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def publish(self, content: dict) -> dict:
        payload = json.dumps(content, separators=(",", ":"))
        signature = self.generate_signature(payload)

        headers = {
            "Content-Type": "application/json",
            "X-IncuBrix-Signature": f"sha256={signature}"
        }

        try:
            response = httpx.post(
                self.webhook_url,
                content=payload,
                headers=headers,
                timeout=10
            )

            return {
                "status": "success" if response.is_success else "failed",
                "status_code": response.status_code
            }

        except httpx.RequestError:
            return {
                "status": "failed",
                "message": "Webhook request failed"
            }

    def validate(self) -> bool:
        return bool(self.webhook_url and self.secret)