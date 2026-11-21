from app.services.publishing import PublishingService
from app.connectors.registry import ConnectorRegistry
from app.connectors.manual import ManualConnector
from app.rules.engine import PostingRulesEngine


def create_service():
    registry = ConnectorRegistry()
    registry.register("manual", ManualConnector())

    rules = PostingRulesEngine()

    return PublishingService(registry, rules)


def test_successful_preview():
    service = create_service()

    result = service.publish(
        "manual",
        {
            "title": "Test Article",
            "body": "Testing distribution"
        }
    )

    assert result["status"] == "preview"


def test_blocked_content():
    service = create_service()

    result = service.publish(
        "manual",
        {
            "body": "Promotional content",
            "is_self_promotion": True,
            "self_promo_disclosure": False
        }
    )

    assert result["status"] == "blocked"


def test_unknown_platform():
    service = create_service()

    result = service.publish(
        "unknown",
        {"title": "Test", "body": "Test"}
    )

    assert result["status"] == "failed"


def test_manual_publish():
    service = create_service()

    result = service.publish(
        "manual",
        {
            "title": "Test Article",
            "body": "Testing distribution"
        },
        dry_run=False
    )

    assert result["status"] == "manual_required"