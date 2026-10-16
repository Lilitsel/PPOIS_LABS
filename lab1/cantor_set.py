import copy
import itertools
from typing import Any, List
from abstract_set import AbstractCantorSet


class CantorSet(AbstractCantorSet):


    def __init__(self, elements: List[Any] = None):
        self._elements: List[Any] = []
        if elements:
            for el in elements:
                self.add(el)

    def __del__(self):
        if hasattr(self, '_elements'):
            self._elements.clear()

    def __copy__(self):
        new_set = CantorSet()
        new_set._elements = self._elements[:]
        return new_set

    def __deepcopy__(self, memo):
        new_set = CantorSet()
        new_set._elements = copy.deepcopy(self._elements, memo)
        return new_set


    def copy(self) -> 'CantorSet':
        return copy.deepcopy(self)

    def is_empty(self) -> bool:
        return len(self._elements) == 0

    def add(self, item: Any) -> None:
        if item not in self._elements:
            self._elements.append(item)

    def remove(self, item: Any) -> None:
        if item in self._elements:
            self._elements.remove(item)
        else:
            raise KeyError(f"Элемент {item} не найден в множестве")

    def __len__(self) -> int:
        return len(self._elements)


    def __getitem__(self, item: Any) -> bool:
        return item in self._elements


    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CantorSet):
            return False
        if len(self) != len(other):
            return False
        return all(item in other._elements for item in self._elements)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    __hash__ = None  # Множество изменяемое, поэтому хеш отключается

    #Вывод
    def __str__(self) -> str:
        items_str = ", ".join(str(item) for item in self._elements)
        return f"{{{items_str}}}"

    def __repr__(self) -> str:
        return f"CantorSet({repr(self._elements)})"

    @classmethod
    def from_string(cls, text: str) -> 'CantorSet':
        text = text.replace(" ", "")
        if not text or text[0] != '{' or text[-1] != '}':
            raise ValueError("Строка должна начинаться с '{' и заканчиваться '}'")

        stack = []
        current_item = ""

        for char in text:
            if char == '{':
                stack.append(cls())
            elif char == '}':
                if current_item:
                    stack[-1].add(current_item)
                    current_item = ""
                finished_set = stack.pop()
                if stack:
                    stack[-1].add(finished_set)
                else:
                    return finished_set
            elif char == ',':
                if current_item:
                    stack[-1].add(current_item)
                    current_item = ""
            else:
                current_item += char

        raise ValueError("Нарушен баланс скобок")

    #Арифметические операции

    # Объединение
    def __add__(self, other: 'CantorSet') -> 'CantorSet':
        result = self.copy()
        for item in other._elements:
            result.add(item)
        return result

#Составное объединение
    def __iadd__(self, other: 'CantorSet') -> 'CantorSet':
        for item in other._elements:
            self.add(item)
        return self

#Пересечение
    def __mul__(self, other: 'CantorSet') -> 'CantorSet':
        result = CantorSet()
        for item in self._elements:
            if item in other._elements:
                result.add(item)
        return result

#Составное пересечение
    def __imul__(self, other: 'CantorSet') -> 'CantorSet':
        self._elements = [item for item in self._elements if item in other._elements]
        return self

#Pазность
    def __sub__(self, other: 'CantorSet') -> 'CantorSet':
        result = CantorSet()
        for item in self._elements:
            if item not in other._elements:
                result.add(item)
        return result

#Составная разность
    def __isub__(self, other: 'CantorSet') -> 'CantorSet':
        self._elements = [item for item in self._elements if item not in other._elements]
        return self

    #Операции сравнения порядка (выполняются прямо в памяти)
    #"Строгое подмножество <
    def __lt__(self, other: 'CantorSet') -> bool:
        return self <= other and len(self) < len(other)

    #Нестрогое подмножество <=
    def __le__(self, other: 'CantorSet') -> bool:
        return all(item in other._elements for item in self._elements)

    #Строгое надмножество >
    def __gt__(self, other: 'CantorSet') -> bool:
        return other < self

    #Нестрогое надмножество >=
    def __ge__(self, other: 'CantorSet') -> bool:
        return other <= self

    def increment(self) -> None:
        self._elements = [el + 1 if isinstance(el, (int, float)) else el for el in self._elements]

    def decrement(self) -> None:
        self._elements = [el - 1 if isinstance(el, (int, float)) else el for el in self._elements]

    #Приведение к типу float(мощность множества)
    def __float__(self) -> float:
        return float(len(self._elements))

#Построение булеана
    def power_set(self) -> 'CantorSet':
        result = CantorSet()
        for r in range(len(self) + 1):
            for combo in itertools.combinations(self._elements, r):
                subset = CantorSet(list(combo))
                result.add(subset)
        return result