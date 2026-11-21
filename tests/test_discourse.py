from app.connectors.discourse import DiscourseConnector


def test_discourse_validation():
    connector = DiscourseConnector(
        "https://example.com",
        "test-api-key",
        "test-user"
    )

    assert connector.validate() is True


def test_discourse_invalid_validation():
    connector = DiscourseConnector("", "", "")

    assert connector.validate() is False