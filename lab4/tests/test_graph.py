import pytest

from lab4_pkg.exceptions import (
    DuplicateEdgeError,
    DuplicateVertexError,
    EmptyGraphError,
    InvalidIteratorError,
    VertexNotFoundError,
)
from lab4_pkg.graph import OrthogonalGraph, ReadOnlyOrthogonalGraph


def _build_sample_graph() -> OrthogonalGraph[str]:
    graph: OrthogonalGraph[str] = OrthogonalGraph()
    for node in ("A", "B", "C"):
        graph.add_vertex(node)
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "C")
    return graph


def test_graph_basic_operations_and_degrees() -> None:
    graph = _build_sample_graph()
    assert not graph.is_empty()
    assert graph.vertex_count() == 3
    assert graph.edge_count() == 3
    assert graph.has_vertex("A")
    assert not graph.has_vertex("Z")
    assert graph.has_edge("A", "B")
    assert not graph.has_edge("B", "A")
    assert not graph.has_edge("Z", "A")

    assert graph.out_degree("A") == 2
    assert graph.in_degree("C") == 2
    assert graph.vertex_degree("B") == 2
    assert graph.edge_degree("A", "B") == graph.vertex_degree("A") + graph.vertex_degree("B")
    assert graph.get_vertex("A").degree == 2
    assert graph.get_edge("A", "B").as_pair() == ("A", "B")
    assert list(iter(graph)) == ["A", "B", "C"]


def test_graph_copy_assign_comparisons_and_clear() -> None:
    g1 = _build_sample_graph()
    g2 = g1.copy()
    assert g1 == g2
    assert g1 != OrthogonalGraph[str]()
    assert g1.__eq__("not-a-graph") is NotImplemented
    assert g1.__ne__("not-a-graph") is NotImplemented
    assert g1.__lt__("not-a-graph") is NotImplemented
    assert g1.__le__("not-a-graph") is NotImplemented
    assert g1.__gt__("not-a-graph") is NotImplemented
    assert g1.__ge__("not-a-graph") is NotImplemented

    g3 = OrthogonalGraph[str]()
    g3.assign_from(g1)
    assert g3 == g1
    assert g3.assign_from(g3) is g3

    g3.add_vertex("D")
    assert g1 < g3
    assert g1 <= g3
    assert g3 > g1
    assert g3 >= g1

    g3.clear()
    assert g3.is_empty()
    assert str(g3) == "<empty graph>"
    assert "V(A):" in str(g1)


def test_graph_iterators_and_remove_by_iterator() -> None:
    graph = _build_sample_graph()
    assert list(graph.vertices_iter()) == ["A", "B", "C"]
    assert list(graph.vertices_iter(reverse=True)) == ["C", "B", "A"]
    assert list(graph.edges_iter()) == [("A", "B"), ("A", "C"), ("B", "C")]
    assert list(graph.edges_iter(reverse=True)) == [("B", "C"), ("A", "C"), ("A", "B")]
    assert list(graph.incident_edges_iter("B")) == [("A", "B"), ("B", "C")]
    assert list(graph.incident_edges_iter("B", reverse=True)) == [("B", "C"), ("A", "B")]
    assert list(graph.adjacent_vertices_iter("A")) == ["C", "B"]
    assert list(graph.adjacent_vertices_iter("A", reverse=True)) == ["B", "C"]

    step_iter = graph.vertices_iter()
    assert step_iter.has_current()
    assert step_iter.next().current() == "B"
    assert step_iter.prev().current() == "A"

    rev_step_iter = graph.vertices_iter(reverse=True)
    assert rev_step_iter.current() == "C"
    assert rev_step_iter.next().current() == "B"
    assert rev_step_iter.prev().current() == "C"

    v_iter = graph.vertices_iter().next()
    assert v_iter.current() == "B"
    graph.remove_vertex_at(v_iter)
    assert not graph.has_vertex("B")
    assert not graph.has_edge("A", "B")

    e_iter = graph.edges_iter()
    graph.remove_edge_at(e_iter)
    assert not graph.has_edge("A", "C")

    graph.add_edge("A", "C")
    graph.remove_edge("A", "C")
    assert not graph.has_edge("A", "C")


def test_readonly_view_and_errors() -> None:
    graph = _build_sample_graph()
    ro = ReadOnlyOrthogonalGraph(graph)
    ro.require_non_empty()
    assert ro.vertex_count() == 3
    assert ro.edge_count() == 3
    assert ro.has_vertex("A")
    assert ro.has_edge("A", "B")
    assert list(ro.vertices_iter(reverse=True)) == ["C", "B", "A"]
    assert list(ro.edges_iter(reverse=True)) == [("B", "C"), ("A", "C"), ("A", "B")]
    assert list(ro.incident_edges_iter("A", reverse=True)) == [("A", "C"), ("A", "B")]
    assert list(ro.adjacent_vertices_iter("A", reverse=True)) == ["B", "C"]

    ro_iter = graph.vertices_iter(read_only=True)
    assert ro_iter.is_read_only
    with pytest.raises(InvalidIteratorError):
        graph.remove_vertex_at(ro_iter)

    ro_edge_iter = graph.edges_iter(read_only=True)
    with pytest.raises(InvalidIteratorError):
        graph.remove_edge_at(ro_edge_iter)

    out_iter = graph.vertices_iter()
    for _ in range(graph.vertex_count()):
        out_iter.next()
    with pytest.raises(InvalidIteratorError):
        out_iter.current()

    with pytest.raises(DuplicateVertexError):
        graph.add_vertex("A")
    with pytest.raises(DuplicateEdgeError):
        graph.add_edge("A", "B")
    with pytest.raises(VertexNotFoundError):
        graph.remove_vertex("NOPE")
    with pytest.raises(VertexNotFoundError):
        graph.remove_edge("A", "A")
    with pytest.raises(VertexNotFoundError):
        graph.edge_degree("A", "A")

    graph.clear()
    with pytest.raises(EmptyGraphError):
        ro.require_non_empty()
