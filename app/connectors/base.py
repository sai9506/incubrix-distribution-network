from abc import ABC, abstractmethod


class BaseConnector(ABC):

    @abstractmethod
    def publish(self, content: dict) -> dict:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass