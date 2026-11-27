"""Вариант 10 (Задание 1): обобщённые Merge sort и Bozo sort."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")
KeyFunc = Callable[[T], object]


@dataclass(frozen=True)
class TaskRecord:
    """Демонстрационный пользовательский класс задачи для сортировки."""

    task_id: int
    priority: int
    title: str

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, TaskRecord):
            return NotImplemented
        return (self.priority, self.task_id) < (other.priority, other.task_id)

    def __le__(self, other: object) -> bool:
        if not isinstance(other, TaskRecord):
            return NotImplemented
        return (self.priority, self.task_id) <= (other.priority, other.task_id)

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, TaskRecord):
            return NotImplemented
        return (self.priority, self.task_id) > (other.priority, other.task_id)

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, TaskRecord):
            return NotImplemented
        return (self.priority, self.task_id) >= (other.priority, other.task_id)


def _default_key(item: T) -> object:
    return item


def _merge_slices(
    left: list[T],
    right: list[T],
    key: KeyFunc,
    reverse: bool,
) -> list[T]:
    """Сливает два отсортированных списка в один."""
    merged: list[T] = []
    left_idx = 0
    right_idx = 0
    while left_idx < len(left) and right_idx < len(right):
        left_key = key(left[left_idx])
        right_key = key(right[right_idx])
        take_left = left_key >= right_key if reverse else left_key <= right_key
        if take_left:
            merged.append(left[left_idx])
            left_idx += 1
        else:
            merged.append(right[right_idx])
            right_idx += 1
    merged.extend(left[left_idx:])
    merged.extend(right[right_idx:])
    return merged


def _merge_sort_list(items: list[T], key: KeyFunc, reverse: bool) -> list[T]:
    """Возвращает новый отсортированный слиянием список."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    sorted_left = _merge_sort_list(items[:mid], key=key, reverse=reverse)
    sorted_right = _merge_sort_list(items[mid:], key=key, reverse=reverse)
    return _merge_slices(sorted_left, sorted_right, key=key, reverse=reverse)


def merge_sort(
    sequence: list[T],
    *,
    key: KeyFunc | None = None,
    reverse: bool = False,
    in_place: bool = False,
) -> list[T]:
    """Обобщённая сортировка слиянием для списков и массивоподобных последовательностей."""
    key_fn = key if key is not None else _default_key
    result = _merge_sort_list(list(sequence), key=key_fn, reverse=reverse)
    if in_place:
        sequence[:] = result
        return sequence
    return result


def _is_sorted(items: list[T], key: KeyFunc, reverse: bool) -> bool:
    """Проверяет упорядоченность последовательности."""
    for idx in range(len(items) - 1):
        first_key = key(items[idx])
        second_key = key(items[idx + 1])
        unordered = first_key < second_key if reverse else first_key > second_key
        if unordered:
            return False
    return True


def bozo_sort(
    sequence: list[T],
    *,
    key: KeyFunc | None = None,
    reverse: bool = False,
    in_place: bool = False,
    rng: random.Random | None = None,
    max_attempts: int = 100_000,
) -> list[T]:
    """Обобщённый Bozo sort (случайный обмен двух элементов до упорядочивания)."""
    if max_attempts <= 0:
        raise ValueError("max_attempts must be positive")
    key_fn = key if key is not None else _default_key
    generator = rng if rng is not None else random.Random()
    work_list = list(sequence)
    attempts = 0
    while not _is_sorted(work_list, key=key_fn, reverse=reverse):
        if attempts >= max_attempts:
            raise RuntimeError(f"Bozo sort exceeded {max_attempts} attempts")
        if len(work_list) >= 2:
            first_idx, second_idx = generator.sample(range(len(work_list)), 2)
            work_list[first_idx], work_list[second_idx] = work_list[second_idx], work_list[first_idx]
        attempts += 1
    if in_place:
        sequence[:] = work_list
        return sequence
    return work_list
