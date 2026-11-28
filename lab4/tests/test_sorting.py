import random

import pytest

from lab4_pkg.sorting import TaskRecord, bozo_sort, merge_sort


def test_merge_sort_primitives_and_in_place() -> None:
    arr = [5, 2, 9, 1, 5, 6]
    sorted_copy = merge_sort(arr)
    assert sorted_copy == [1, 2, 5, 5, 6, 9]
    assert arr == [5, 2, 9, 1, 5, 6]

    merge_sort(arr, reverse=True, in_place=True)
    assert arr == [9, 6, 5, 5, 2, 1]


def test_merge_sort_custom_class_and_key() -> None:
    t1 = TaskRecord(task_id=1, priority=1, title="Alpha")
    t2 = TaskRecord(task_id=2, priority=2, title="Beta")
    t3 = TaskRecord(task_id=3, priority=1, title="Gamma")
    tasks = [t2, t1, t3]

    assert t1 < t2
    assert t1 <= t2
    assert t2 > t1
    assert t2 >= t1
    assert t1.__lt__("other") is NotImplemented
    assert t1.__le__("other") is NotImplemented
    assert t1.__gt__("other") is NotImplemented
    assert t1.__ge__("other") is NotImplemented

    by_default = merge_sort(tasks)
    assert [item.title for item in by_default] == ["Alpha", "Gamma", "Beta"]

    by_title = merge_sort(tasks, key=lambda item: item.title)
    assert [item.title for item in by_title] == ["Alpha", "Beta", "Gamma"]

    rev_by_title = merge_sort(tasks, key=lambda item: item.title, reverse=True)
    assert [item.title for item in rev_by_title] == ["Gamma", "Beta", "Alpha"]


def test_bozo_sort_deterministic_and_edge_cases() -> None:
    assert bozo_sort([], rng=random.Random(1)) == []
    assert bozo_sort([42], rng=random.Random(1)) == [42]

    data = [3, 1, 2]
    res = bozo_sort(data, rng=random.Random(7), in_place=True)
    assert res == [1, 2, 3]
    assert data == [1, 2, 3]

    desc = bozo_sort([1, 3, 2], reverse=True, rng=random.Random(7))
    assert desc == [3, 2, 1]


def test_bozo_sort_errors() -> None:
    with pytest.raises(ValueError):
        bozo_sort([1, 2], max_attempts=0)
    with pytest.raises(RuntimeError):
        bozo_sort([5, 4, 3, 2, 1], rng=random.Random(1), max_attempts=1)
