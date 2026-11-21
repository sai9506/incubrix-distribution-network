
from app.api.routes import registry


def test_manual_connector_is_always_available():
    platforms = registry.supported_platforms()
    assert "manual" in platforms


def test_configured_connectors_are_registered():
    platforms = registry.supported_platforms()

    expected_platforms = {
        "manual",
        "webhook",
        "discourse",
        "lemmy",
        "devto",
        "ghost"
    }

    assert set(platforms) == expected_platforms


def test_supported_platforms_are_unique():
    platforms = registry.supported_platforms()
    assert len(platforms) == len(set(platforms))
