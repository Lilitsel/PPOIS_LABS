"""Вариант 2.1.10: ориентированный граф на ортогональном списке смежности."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeVar

from lab4_pkg.exceptions import (
    DuplicateEdgeError,
    DuplicateVertexError,
    EmptyGraphError,
    InvalidIteratorError,
    VertexNotFoundError,
)

T = TypeVar("T")
EdgePair: TypeAlias = tuple[T, T]


@dataclass
class _OrthoEdge(Generic[T]):
    """Узел ребра в ортогональном списке смежности (u -> v)."""

    tail_value: T
    head_value: T
    next_out: _OrthoEdge[T] | None = None
    next_in: _OrthoEdge[T] | None = None
    active: bool = True

    def as_pair(self) -> EdgePair[T]:
        """Возвращает пару вершин (источник, приёмник)."""
        return (self.tail_value, self.head_value)


@dataclass
class VertexNode(Generic[T]):
    """Публичное представление вершины графа."""

    value: T
    in_degree: int
    out_degree: int

    @property
    def degree(self) -> int:
        """Суммарная степень вершины."""
        return self.in_degree + self.out_degree


@dataclass(frozen=True)
class EdgeView(Generic[T]):
    """Публичное представление ребра графа."""

    source: T
    target: T
    degree: int

    def as_pair(self) -> EdgePair[T]:
        """Возвращает пару вершин (источник, приёмник)."""
        return (self.source, self.target)


class _BidirectionalIter(Generic[T]):
    """Двунаправленный итератор с поддержкой прямого и обратного обхода."""

    def __init__(self, items: list[T], *, reverse: bool = False, read_only: bool = False) -> None:
        self._items = list(items)
        self._reverse = reverse
        self._read_only = read_only
        self._index = len(self._items) - 1 if reverse else 0

    @property
    def is_read_only(self) -> bool:
        """Возвращает признак константного (только чтение) итератора."""
        return self._read_only

    def __iter__(self) -> _BidirectionalIter[T]:
        return self

    def __next__(self) -> T:
        if not self.has_current():
            raise StopIteration
        value = self._items[self._index]
        self.next()
        return value

    def has_current(self) -> bool:
        """Проверяет, указывает ли итератор на существующий элемент."""
        return 0 <= self._index < len(self._items)

    def current(self) -> T:
        """Возвращает текущий элемент без сдвига итератора."""
        if not self.has_current():
            raise InvalidIteratorError("Iterator is out of range")
        return self._items[self._index]

    def next(self) -> _BidirectionalIter[T]:
        """Сдвигает итератор на следующий элемент в текущем направлении."""
        self._index += -1 if self._reverse else 1
        return self

    def prev(self) -> _BidirectionalIter[T]:
        """Сдвигает итератор на предыдущий элемент в текущем направлении."""
        self._index += 1 if self._reverse else -1
        return self


class OrthogonalGraph(Generic[T]):
    """Ориентированный граф на ортогональном списке смежности."""

    ValueType: TypeAlias = T
    EdgeType: TypeAlias = EdgePair[T]

    def __init__(self) -> None:
        self._vertices: list[T] = []
        self._first_out: dict[T, _OrthoEdge[T] | None] = {}
        self._first_in: dict[T, _OrthoEdge[T] | None] = {}
        self._edges: list[_OrthoEdge[T]] = []

    def copy(self) -> OrthogonalGraph[T]:
        """Создаёт глубокую копию графа."""
        cloned: OrthogonalGraph[T] = OrthogonalGraph()
        for vertex in self._vertices:
            cloned.add_vertex(vertex)
        for edge in self._edges:
            if edge.active:
                cloned.add_edge(edge.tail_value, edge.head_value)
        return cloned

    def assign_from(self, other: OrthogonalGraph[T]) -> OrthogonalGraph[T]:
        """Копирует состояние из другого графа в текущий объект."""
        if self is other:
            return self
        snapshot = other.copy()
        self._vertices = snapshot._vertices
        self._first_out = snapshot._first_out
        self._first_in = snapshot._first_in
        self._edges = snapshot._edges
        return self

    def is_empty(self) -> bool:
        """Проверяет, пуст ли граф."""
        return len(self._vertices) == 0

    def clear(self) -> None:
        """Удаляет все вершины и рёбра."""
        self._vertices.clear()
        self._first_out.clear()
        self._first_in.clear()
        self._edges.clear()

    def vertex_count(self) -> int:
        """Возвращает количество вершин."""
        return len(self._vertices)

    def edge_count(self) -> int:
        """Возвращает количество активных рёбер."""
        return sum(1 for edge in self._edges if edge.active)

    def has_vertex(self, vertex: T) -> bool:
        """Проверяет наличие вершины в графе."""
        return vertex in self._first_out

    def _ensure_vertex(self, vertex: T) -> None:
        if not self.has_vertex(vertex):
            raise VertexNotFoundError(f"Vertex {vertex!r} not found")

    def has_edge(self, source: T, target: T) -> bool:
        """Проверяет наличие ориентированного ребра source -> target."""
        if not (self.has_vertex(source) and self.has_vertex(target)):
            return False
        return self._find_edge(source, target) is not None

    def _find_edge(self, source: T, target: T) -> _OrthoEdge[T] | None:
        curr = self._first_out.get(source)
        while curr is not None:
            if curr.active and curr.head_value == target:
                return curr
            curr = curr.next_out
        return None

    def in_degree(self, vertex: T) -> int:
        """Возвращает полустепень захода вершины."""
        self._ensure_vertex(vertex)
        count = 0
        curr = self._first_in.get(vertex)
        while curr is not None:
            if curr.active:
                count += 1
            curr = curr.next_in
        return count

    def out_degree(self, vertex: T) -> int:
        """Возвращает полустепень исхода вершины."""
        self._ensure_vertex(vertex)
        count = 0
        curr = self._first_out.get(vertex)
        while curr is not None:
            if curr.active:
                count += 1
            curr = curr.next_out
        return count

    def vertex_degree(self, vertex: T) -> int:
        """Возвращает суммарную степень вершины."""
        return self.in_degree(vertex) + self.out_degree(vertex)

    def edge_degree(self, source: T, target: T) -> int:
        """Возвращает степень ребра (сумма степеней его концевых вершин)."""
        self._ensure_vertex(source)
        self._ensure_vertex(target)
        if not self.has_edge(source, target):
            raise VertexNotFoundError(f"Edge ({source!r} -> {target!r}) not found")
        return self.vertex_degree(source) + self.vertex_degree(target)

    def get_vertex(self, vertex: T) -> VertexNode[T]:
        """Возвращает информацию о вершине."""
        self._ensure_vertex(vertex)
        return VertexNode(
            value=vertex,
            in_degree=self.in_degree(vertex),
            out_degree=self.out_degree(vertex),
        )

    def get_edge(self, source: T, target: T) -> EdgeView[T]:
        """Возвращает информацию о ребре."""
        degree = self.edge_degree(source, target)
        return EdgeView(source=source, target=target, degree=degree)

    def add_vertex(self, vertex: T) -> None:
        """Добавляет новую вершину в граф."""
        if self.has_vertex(vertex):
            raise DuplicateVertexError(f"Vertex {vertex!r} already exists")
        self._vertices.append(vertex)
        self._first_out[vertex] = None
        self._first_in[vertex] = None

    def add_edge(self, source: T, target: T) -> None:
        """Добавляет ориентированное ребро source -> target."""
        self._ensure_vertex(source)
        self._ensure_vertex(target)
        if self.has_edge(source, target):
            raise DuplicateEdgeError(f"Edge ({source!r} -> {target!r}) already exists")
        edge = _OrthoEdge(
            tail_value=source,
            head_value=target,
            next_out=self._first_out[source],
            next_in=self._first_in[target],
            active=True,
        )
        self._first_out[source] = edge
        self._first_in[target] = edge
        self._edges.append(edge)

    def _unlink_edge(self, edge: _OrthoEdge[T]) -> None:
        edge.active = False
        self._edges = [item for item in self._edges if item is not edge and item.active]
        for vertex in self._vertices:
            self._first_out[vertex] = self._filter_out_chain(self._first_out[vertex], edge)
            self._first_in[vertex] = self._filter_in_chain(self._first_in[vertex], edge)

    def _filter_out_chain(
        self,
        head: _OrthoEdge[T] | None,
        target_edge: _OrthoEdge[T],
    ) -> _OrthoEdge[T] | None:
        first: _OrthoEdge[T] | None = None
        prev: _OrthoEdge[T] | None = None
        curr = head
        while curr is not None:
            nxt = curr.next_out
            if curr is not target_edge and curr.active:
                curr.next_out = None
                if first is None:
                    first = curr
                elif prev is not None:
                    prev.next_out = curr
                prev = curr
            curr = nxt
        return first

    def _filter_in_chain(
        self,
        head: _OrthoEdge[T] | None,
        target_edge: _OrthoEdge[T],
    ) -> _OrthoEdge[T] | None:
        first: _OrthoEdge[T] | None = None
        prev: _OrthoEdge[T] | None = None
        curr = head
        while curr is not None:
            nxt = curr.next_in
            if curr is not target_edge and curr.active:
                curr.next_in = None
                if first is None:
                    first = curr
                elif prev is not None:
                    prev.next_in = curr
                prev = curr
            curr = nxt
        return first

    def remove_edge(self, source: T, target: T) -> None:
        """Удаляет ориентированное ребро source -> target."""
        self._ensure_vertex(source)
        self._ensure_vertex(target)
        edge = self._find_edge(source, target)
        if edge is None:
            raise VertexNotFoundError(f"Edge ({source!r} -> {target!r}) not found")
        self._unlink_edge(edge)

    def remove_vertex(self, vertex: T) -> None:
        """Удаляет вершину и все инцидентные ей рёбра."""
        self._ensure_vertex(vertex)
        incident = [
            edge
            for edge in self._edges
            if edge.active and (edge.tail_value == vertex or edge.head_value == vertex)
        ]
        for edge in incident:
            self._unlink_edge(edge)
        self._vertices = [item for item in self._vertices if item != vertex]
        self._first_out.pop(vertex, None)
        self._first_in.pop(vertex, None)

    def remove_vertex_at(self, iterator: _BidirectionalIter[T]) -> None:
        """Удаляет вершину, на которую указывает итератор вершин."""
        if iterator.is_read_only:
            raise InvalidIteratorError("Cannot mutate graph via read-only iterator")
        self.remove_vertex(iterator.current())

    def remove_edge_at(self, iterator: _BidirectionalIter[EdgePair[T]]) -> None:
        """Удаляет ребро, на которое указывает итератор рёбер."""
        if iterator.is_read_only:
            raise InvalidIteratorError("Cannot mutate graph via read-only iterator")
        source, target = iterator.current()
        self.remove_edge(source, target)

    def _active_edges(self) -> list[EdgePair[T]]:
        return [edge.as_pair() for edge in self._edges if edge.active]

    def _incident_edges(self, vertex: T) -> list[EdgePair[T]]:
        self._ensure_vertex(vertex)
        return [
            edge.as_pair()
            for edge in self._edges
            if edge.active and (edge.tail_value == vertex or edge.head_value == vertex)
        ]

    def _adjacent_vertices(self, vertex: T) -> list[T]:
        self._ensure_vertex(vertex)
        adjacent: list[T] = []
        curr = self._first_out.get(vertex)
        while curr is not None:
            if curr.active and curr.head_value not in adjacent:
                adjacent.append(curr.head_value)
            curr = curr.next_out
        return adjacent

    def vertices_iter(self, *, reverse: bool = False, read_only: bool = False) -> _BidirectionalIter[T]:
        """Возвращает двунаправленный итератор по вершинам."""
        return _BidirectionalIter(self._vertices, reverse=reverse, read_only=read_only)

    def edges_iter(
        self,
        *,
        reverse: bool = False,
        read_only: bool = False,
    ) -> _BidirectionalIter[EdgePair[T]]:
        """Возвращает двунаправленный итератор по рёбрам (пара источник-приёмник)."""
        return _BidirectionalIter(self._active_edges(), reverse=reverse, read_only=read_only)

    def incident_edges_iter(
        self,
        vertex: T,
        *,
        reverse: bool = False,
        read_only: bool = False,
    ) -> _BidirectionalIter[EdgePair[T]]:
        """Возвращает двунаправленный итератор по рёбрам, инцидентным вершине."""
        return _BidirectionalIter(self._incident_edges(vertex), reverse=reverse, read_only=read_only)

    def adjacent_vertices_iter(
        self,
        vertex: T,
        *,
        reverse: bool = False,
        read_only: bool = False,
    ) -> _BidirectionalIter[T]:
        """Возвращает двунаправленный итератор по смежным вершинам."""
        return _BidirectionalIter(self._adjacent_vertices(vertex), reverse=reverse, read_only=read_only)

    def __iter__(self) -> Iterator[T]:
        return iter(self.vertices_iter())

    def __str__(self) -> str:
        lines: list[str] = []
        for vertex in self.vertices_iter():
            inc_list = [f"{src}->{dst}" for src, dst in self.incident_edges_iter(vertex)]
            adj_list = [str(adj) for adj in self.adjacent_vertices_iter(vertex)]
            lines.append(f"V({vertex}): adj=[{', '.join(adj_list)}], inc=[{', '.join(inc_list)}]")
        return "\n".join(lines) if lines else "<empty graph>"

    def _snapshot_key(self) -> tuple[tuple[T, ...], tuple[EdgePair[T], ...]]:
        return (tuple(self._vertices), tuple(self._active_edges()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrthogonalGraph):
            return NotImplemented
        return self._snapshot_key() == other._snapshot_key()

    def __ne__(self, other: object) -> bool:
        eq = self.__eq__(other)
        return NotImplemented if eq is NotImplemented else not eq

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, OrthogonalGraph):
            return NotImplemented
        return self._snapshot_key() < other._snapshot_key()

    def __le__(self, other: object) -> bool:
        if not isinstance(other, OrthogonalGraph):
            return NotImplemented
        return self._snapshot_key() <= other._snapshot_key()

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, OrthogonalGraph):
            return NotImplemented
        return self._snapshot_key() > other._snapshot_key()

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, OrthogonalGraph):
            return NotImplemented
        return self._snapshot_key() >= other._snapshot_key()


class ReadOnlyOrthogonalGraph(Generic[T]):
    """Обёртка только для чтения вокруг ортогонального графа."""

    def __init__(self, graph: OrthogonalGraph[T]) -> None:
        self._graph = graph

    def is_empty(self) -> bool:
        """Проверяет пустоту графа."""
        return self._graph.is_empty()

    def vertex_count(self) -> int:
        """Возвращает число вершин."""
        return self._graph.vertex_count()

    def edge_count(self) -> int:
        """Возвращает число рёбер."""
        return self._graph.edge_count()

    def has_vertex(self, vertex: T) -> bool:
        """Проверяет наличие вершины."""
        return self._graph.has_vertex(vertex)

    def has_edge(self, source: T, target: T) -> bool:
        """Проверяет наличие ребра."""
        return self._graph.has_edge(source, target)

    def vertices_iter(self, *, reverse: bool = False) -> _BidirectionalIter[T]:
        """Возвращает read-only итератор вершин."""
        return self._graph.vertices_iter(reverse=reverse, read_only=True)

    def edges_iter(self, *, reverse: bool = False) -> _BidirectionalIter[EdgePair[T]]:
        """Возвращает read-only итератор рёбер."""
        return self._graph.edges_iter(reverse=reverse, read_only=True)

    def incident_edges_iter(self, vertex: T, *, reverse: bool = False) -> _BidirectionalIter[EdgePair[T]]:
        """Возвращает read-only итератор инцидентных рёбер."""
        return self._graph.incident_edges_iter(vertex, reverse=reverse, read_only=True)

    def adjacent_vertices_iter(self, vertex: T, *, reverse: bool = False) -> _BidirectionalIter[T]:
        """Возвращает read-only итератор смежных вершин."""
        return self._graph.adjacent_vertices_iter(vertex, reverse=reverse, read_only=True)

    def require_non_empty(self) -> None:
        """Проверяет, что граф не пуст."""
        if self._graph.is_empty():
            raise EmptyGraphError("Graph is empty")
