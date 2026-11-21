from app.rules.engine import PostingRulesEngine
from app.connectors.registry import ConnectorRegistry


class PublishingService:

    def __init__(
        self,
        registry: ConnectorRegistry,
        rules_engine: PostingRulesEngine
    ):
        self.registry = registry
        self.rules_engine = rules_engine

    def publish(
        self,
        platform: str,
        content: dict,
        recent_posts: int = 0,
        dry_run: bool = True
    ) -> dict:

        # Step 1: Check posting rules
        rule_result = self.rules_engine.evaluate(
            content,
            recent_posts
        )

        if not rule_result["allowed"]:
            return {
                "status": "blocked",
                "errors": rule_result["errors"]
            }

        # Step 2: Get the connector
        try:
            connector = self.registry.get(platform)
        except ValueError as error:
            return {
                "status": "failed",
                "message": str(error)
            }

        # Step 3: Validate connector
        if not connector.validate():
            return {
                "status": "failed",
                "message": "Connector configuration is invalid"
            }

        # Step 4: Preview without external publishing
        if dry_run:
            return {
                "status": "preview",
                "platform": platform,
                "message": "Content passed validation"
            }

        # Step 5: Publish
        return connector.publish(content)