from abc import ABC, abstractmethod
from typing import Any

class AbstractCantorSet(ABC):

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def add(self, item: Any) -> None:
        pass

    @abstractmethod
    def remove(self, item: Any) -> None:
        pass

    @abstractmethod
    def power_set(self) -> 'AbstractCantorSet':
        pass