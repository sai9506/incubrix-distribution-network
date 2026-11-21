from app.connectors.base import BaseConnector


class ConnectorRegistry:

    def __init__(self):
        self.connectors = {}

    def register(self, platform: str, connector: BaseConnector):
        self.connectors[platform.lower()] = connector

    def get(self, platform: str):
        connector = self.connectors.get(platform.lower())

        if connector is None:
            raise ValueError(f"Unsupported platform: {platform}")

        return connector

    def supported_platforms(self):
        return list(self.connectors.keys())