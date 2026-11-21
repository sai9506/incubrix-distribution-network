from app.connectors.lemmy import LemmyConnector


def test_lemmy_validation():
    connector = LemmyConnector(
        "https://example.com",
        "test-token",
        1
    )

    assert connector.validate() is True


def test_lemmy_invalid_validation():
    connector = LemmyConnector("", "", 0)

    assert connector.validate() is False