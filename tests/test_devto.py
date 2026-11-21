from app.connectors.devto import DevToConnector


def test_devto_validation():
    connector = DevToConnector("test-api-key")
    assert connector.validate() is True


def test_devto_invalid_validation():
    connector = DevToConnector("")
    assert connector.validate() is False