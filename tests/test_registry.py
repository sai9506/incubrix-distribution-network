import pytest

from app.connectors.registry import ConnectorRegistry
from app.connectors.manual import ManualConnector
from app.connectors.webhook import WebhookConnector


def test_register_and_get_connector():
    registry = ConnectorRegistry()

    manual = ManualConnector()
    registry.register("manual", manual)

    assert registry.get("manual") is manual


def test_platform_name_is_case_insensitive():
    registry = ConnectorRegistry()

    manual = ManualConnector()
    registry.register("Manual", manual)

    assert registry.get("MANUAL") is manual


def test_unsupported_platform():
    registry = ConnectorRegistry()

    with pytest.raises(ValueError):
        registry.get("unknown")


def test_multiple_connectors():
    registry = ConnectorRegistry()

    registry.register("manual", ManualConnector())
    registry.register(
        "webhook",
        WebhookConnector("https://example.com", "test-secret")
    )

    assert len(registry.supported_platforms()) == 2