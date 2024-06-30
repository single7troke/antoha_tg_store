from abc import ABC, abstractmethod


class AbstractCache(ABC):
    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass
