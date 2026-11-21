
from app.connectors.base import BaseConnector


class ManualConnector(BaseConnector):

    def publish(self, content: dict) -> dict:

        manual_pack = {
            "title": content.get("title", ""),
            "body": content.get("body", ""),
            "tags": content.get("tags", []),
            "disclosures": {
                "ai_generated": content.get("ai_generated", False),
                "ai_disclosure": content.get("ai_disclosure", False),
                "self_promotion": content.get("is_self_promotion", False),
                "self_promo_disclosure": content.get(
                    "self_promo_disclosure", False
                )
            },
            "publishing_checklist": [
                "Review the content before publishing",
                "Check the destination community rules",
                "Verify links and formatting",
                "Include required AI disclosure",
                "Include required self-promotion disclosure",
                "Obtain permission before posting",
                "Publish manually and record the result"
            ]
        }

        return {
            "status": "manual_required",
            "message": "Manual publishing package prepared",
            "manual_pack": manual_pack
        }

    def validate(self) -> bool:
        return True
