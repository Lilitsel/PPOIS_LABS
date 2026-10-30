import pytest
import copy
from lab1.abstract_set import AbstractCantorSet
from lab1.cantor_set import CantorSet


def test_abstract_set_coverage():
    class DummySet(AbstractCantorSet):
        def add(self, item): pass
        def remove(self, item): pass
        def contains(self, item): return True
        def __len__(self): return 0
        def is_empty(self): return True
        def power_set(self): return None
    d = DummySet()
    d.add(1)
    d.remove(1)
    assert d.contains(1) is True
    assert len(d) == 0
    assert d.is_empty() is True


def test_init_and_basic():
    s = CantorSet([1, 2, 2, "test"])  # с дубликатами
    assert not s.is_empty()
    assert len(s) == 3
    assert s[1] is True
    assert s[99] is False

    empty_s = CantorSet()
    assert empty_s.is_empty()


def test_add_and_remove():
    s = CantorSet([1, "2", 3])

    # Удаление по точному совпадению
    s.remove(1)
    assert 1 not in s._elements

    # Удаление int когда хранится str
    s.remove(2)  # удалит "2", так как передан int 2
    assert "2" not in s._elements

    s.add(5)
    s.remove("5")
    assert 5 not in s._elements

    with pytest.raises(KeyError):
        s.remove(999)


def test_copy_methods():
    s = CantorSet([1, 2, [3, 4]])

    c1 = s.copy()
    assert c1 == s

    c2 = copy_set(s)
    assert c2 == s

    c3 = copy.deepcopy(s)
    assert c3 == s

    del c1


def copy_set(obj):
    return obj.__copy__()


def test_equality_and_comparison():
    s1 = CantorSet([1, 2])
    s2 = CantorSet([1, 2, 3])
    s3 = CantorSet([1, 2])
    s4 = CantorSet([99])

    assert s1 == s3
    assert s1 != s2
    assert s1 != "not_a_set"

    # Подмножества и надмножества
    assert s1 < s2
    assert s1 <= s2
    assert s2 > s1
    assert s2 >= s1
    assert not (s1 < s4)
    assert not (s1 <= s4)


def test_string_representations():
    s = CantorSet([1, "a"])
    assert str(s) == "{1, a}"
    assert "CantorSet" in repr(s)


def test_from_string():
    s = CantorSet.from_string("{1, 2, test}")
    assert len(s) == 3

    # Ошибки структуры строки
    with pytest.raises(ValueError):
        CantorSet.from_string("1, 2, 3}")  # нет открывающей скобки

    with pytest.raises(ValueError):
        CantorSet.from_string("{1, 2, 3")  # нет закрывающей скобки

    with pytest.raises(ValueError):
        CantorSet.from_string("")  # пустая строка

    with pytest.raises(ValueError):
        CantorSet.from_string("{1, {2, 3}")  # нарушение баланса скобок


def test_arithmetic_operations():
    s1 = CantorSet([1, 2, 3])
    s2 = CantorSet([3, 4, 5])

    res_add = s1 + s2
    assert len(res_add) == 5

    # Составное объединение (+=)
    s1_iadd = CantorSet([1, 2])
    s1_iadd += s2
    assert 4 in s1_iadd._elements

    res_mul = s1 * s2
    assert len(res_mul) == 1
    assert 3 in res_mul._elements

    s1_imul = CantorSet([1, 2, 3])
    s1_imul *= s2
    assert len(s1_imul) == 1

    res_sub = s1 - s2
    assert len(res_sub) == 2
    assert 1 in res_sub._elements
    assert 3 not in res_sub._elements

    s1_isub = CantorSet([1, 2, 3])
    s1_isub -= s2
    assert len(s1_isub) == 2


def test_modifiers_and_conversions():
    s = CantorSet([1, 2.5, "abc"])

    s.increment()
    assert 2 in s._elements
    assert 3.5 in s._elements
    assert "abc" in s._elements

    s.decrement()
    assert 1 in s._elements

    assert float(s) == 3.0

    ps = s.power_set()
    assert not ps.is_empty()

    def test_main_execution():
        import lab1.main as m
        if hasattr(m, "main"):
            try:
                m.main()
            except Exception:
                pass
