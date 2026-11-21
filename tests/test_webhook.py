from app.connectors.webhook import WebhookConnector


def test_webhook_signature():
    connector = WebhookConnector(
        "https://example.com/webhook",
        "test-secret"
    )

    signature = connector.generate_signature('{"title":"Test"}')

    assert signature.startswith("")


def test_webhook_validation():
    connector = WebhookConnector(
        "https://example.com/webhook",
        "test-secret"
    )

    assert connector.validate() is True