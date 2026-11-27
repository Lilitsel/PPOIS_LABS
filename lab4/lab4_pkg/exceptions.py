"""Исключения для контейнера ориентированного графа."""


class GraphError(Exception):
    """Базовое исключение ошибок графа."""


class EmptyGraphError(GraphError):
    """Выбрасывается при операции над пустым графом."""


class VertexNotFoundError(GraphError):
    """Выбрасывается, если вершина отсутствует в графе."""


class DuplicateVertexError(GraphError):
    """Выбрасывается при попытке добавить существующую вершину."""


class DuplicateEdgeError(GraphError):
    """Выбрасывается при попытке добавить дублирующее ребро."""


class InvalidIteratorError(GraphError):
    """Выбрасывается при некорректном итераторе или удалении по нему."""
