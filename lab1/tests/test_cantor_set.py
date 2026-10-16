import pytest
from lab1.cantor_set import CantorSet


def test_init_and_empty():
    s = CantorSet()
    assert s.is_empty()
    assert len(s) == 0

    s_with_elements = CantorSet([1, 2])
    assert not s_with_elements.is_empty()
    assert len(s_with_elements) == 2


def test_copy_methods():
    s1 = CantorSet([1, CantorSet([2])])
    s2 = s1.copy()
    s3 = s1.__copy__()
    assert s1 == s2
    assert s1 == s3


def test_add_remove():
    s = CantorSet()
    s.add(1)
    s.add(1)
    assert len(s) == 1

    s.remove(1)
    assert s.is_empty()

    with pytest.raises(KeyError):
        s.remove(99)


def test_membership_bracket():
    s = CantorSet([10, 20, 30])
    assert s[20] is True
    assert s[99] is False
    assert s[10] is True


def test_equality_and_inequality():
    s1 = CantorSet([1, 2])
    s2 = CantorSet([1, 2])
    s3 = CantorSet([1, 3])

    assert s1 == s2
    assert s1 != s3
    assert s1 != "not a set"
    assert CantorSet([1]) != CantorSet([1, 2])


def test_string_repr_and_parsing():
    s = CantorSet(["a", "b"])
    assert str(s) == "{a, b}"
    assert "CantorSet" in repr(s)

    parsed = CantorSet.from_string("{a, b, {c}}")
    assert parsed["a"] is True
    assert len(parsed) == 3

    with pytest.raises(ValueError):
        CantorSet.from_string("invalid_string")
    with pytest.raises(ValueError):
        CantorSet.from_string("{a, b")


def test_arithmetic_operators():
    s1 = CantorSet([1, 2])
    s2 = CantorSet([2, 3])

    assert s1 + s2 == CantorSet([1, 2, 3])

    s1_copy = CantorSet([1, 2])
    s1_copy += s2
    assert s1_copy == CantorSet([1, 2, 3])

    assert s1 * s2 == CantorSet([2])

    s1_copy = CantorSet([1, 2])
    s1_copy *= s2
    assert s1_copy == CantorSet([2])

    assert s1 - s2 == CantorSet([1])

    s1_copy = CantorSet([1, 2])
    s1_copy -= s2
    assert s1_copy == CantorSet([1])


def test_comparison_order():
    s1 = CantorSet([1])
    s2 = CantorSet([1, 2])
    s3 = CantorSet([1, 2])

    assert s1 < s2
    assert s1 <= s2
    assert s2 <= s3
    assert s2 > s1
    assert s2 >= s1
    assert s2 >= s3


def test_increment_decrement():
    s = CantorSet([5, "text", 10.0])
    s.increment()
    assert s[6] is True
    assert s["text"] is True
    assert s[11.0] is True

    s.decrement()
    assert s[5] is True
    assert s[10.0] is True


def test_float_conversion():
    s = CantorSet([1, 2, 3, 4])
    assert float(s) == 4.0


def test_power_set():
    s = CantorSet([1, 2])
    ps = s.power_set()
    assert len(ps) == 4