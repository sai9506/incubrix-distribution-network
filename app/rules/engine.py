import re


class PostingRulesEngine:

    def __init__(
        self,
        max_posts_per_day=3,
        max_links=5
    ):
        self.max_posts_per_day = max_posts_per_day
        self.max_links = max_links

    def evaluate(self, content: dict, recent_posts: int = 0) -> dict:

        errors = []

        # Rule 1: Frequency cap
        if recent_posts >= self.max_posts_per_day:
            errors.append("Daily posting limit reached")

        # Rule 2: Self-promotion disclosure
        if content.get("is_self_promotion", False):
            if not content.get("self_promo_disclosure", False):
                errors.append("Self-promotion disclosure required")

        # Rule 3: Link limit
        text = content.get("body", "")
        links = re.findall(r"https?://\S+", text)

        if len(links) > self.max_links:
            errors.append("Maximum link limit exceeded")

        # Rule 4: AI disclosure
        if content.get("ai_generated", False):
            if not content.get("ai_disclosure", False):
                errors.append("AI disclosure required")

        return {
            "allowed": len(errors) == 0,
            "errors": errors
        }