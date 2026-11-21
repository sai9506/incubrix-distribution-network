from app.connectors.manual import ManualConnector


def test_manual_connector():
    connector = ManualConnector()

    result = connector.publish({
        "title": "Test Article",
        "body": "Testing IncuBrix distribution"
    })

    assert result["status"] == "manual_required"
    assert connector.validate() is True