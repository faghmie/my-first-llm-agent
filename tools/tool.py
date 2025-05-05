from abc import ABC, abstractmethod


class Tool(ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def use(self, *args, **kwargs):
        pass