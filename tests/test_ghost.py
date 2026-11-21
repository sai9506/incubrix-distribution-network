from app.connectors.ghost import GhostConnector


def test_ghost_validation():
    connector = GhostConnector(
        "https://example.com",
        "testid:abcdef123456"
    )

    assert connector.validate() is True


def test_ghost_invalid_validation():
    connector = GhostConnector("", "")
    assert connector.validate() is False