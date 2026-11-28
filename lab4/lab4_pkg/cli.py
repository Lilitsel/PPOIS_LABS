"""Консольный интерфейс (CLI) для демонстрации сортировок и графа."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import TextIO

from lab4_pkg.exceptions import GraphError
from lab4_pkg.graph import OrthogonalGraph, ReadOnlyOrthogonalGraph
from lab4_pkg.sorting import TaskRecord, bozo_sort, merge_sort

DEFAULT_TASKS: list[TaskRecord] = [
    TaskRecord(task_id=3, priority=2, title="Write tests"),
    TaskRecord(task_id=1, priority=1, title="Design orthogonal graph"),
    TaskRecord(task_id=4, priority=3, title="Prepare CLI"),
    TaskRecord(task_id=2, priority=1, title="Implement merge sort"),
]


def demo_sorting(numbers: list[int] | None = None, tasks: list[TaskRecord] | None = None) -> str:
    """Формирует отчёт по работе Merge sort и Bozo sort на числах и объектах."""
    raw_nums = list(numbers) if numbers is not None else [42, 7, 19, 3, 25]
    raw_tasks = list(tasks) if tasks is not None else list(DEFAULT_TASKS)
    sorted_nums = merge_sort(raw_nums)
    bozo_nums = bozo_sort(raw_nums, rng=random.Random(10))
    sorted_tasks = merge_sort(raw_tasks)
    sorted_by_title = merge_sort(raw_tasks, key=lambda item: item.title)
    return (
        f"Numbers input: {raw_nums}\n"
        f"Merge sort:    {sorted_nums}\n"
        f"Bozo sort:     {bozo_nums}\n"
        f"Tasks sorted:  {[t.title for t in sorted_tasks]}\n"
        f"By title:      {[t.title for t in sorted_by_title]}"
    )


def format_graph_report(graph: OrthogonalGraph[str]) -> str:
    """Формирует текстовый отчёт по графу и его итераторам."""
    ro_view = ReadOnlyOrthogonalGraph(graph)
    vertices = list(ro_view.vertices_iter())
    edges = list(ro_view.edges_iter())
    rev_edges = list(ro_view.edges_iter(reverse=True))
    return (
        f"Vertices ({ro_view.vertex_count()}): {vertices}\n"
        f"Edges ({ro_view.edge_count()}):    {edges}\n"
        f"Reverse edges: {rev_edges}\n"
        f"Details:\n{graph}"
    )


def run_cli(
    input_stream: TextIO,
    output_stream: TextIO,
    graph: OrthogonalGraph[str] | None = None,
) -> int:
    """Запускает интерактивное меню предметной области."""
    target_graph = graph if graph is not None else OrthogonalGraph[str]()
    handlers: dict[str, Callable[[], str]] = {
        "1": lambda: demo_sorting(),
        "2": lambda: format_graph_report(target_graph),
    }
    while True:
        output_stream.write(
            "\n1. Demo Merge sort & Bozo sort\n"
            "2. Show graph & iterators report\n"
            "3. Add vertex (v=<name>)\n"
            "4. Add directed edge (u->v)\n"
            "5. Remove vertex (v=<name>)\n"
            "0. Exit\n"
            "Choice: "
        )
        line = input_stream.readline()
        if not line:
            return 0
        choice = line.strip()
        if choice == "0":
            return 0
        if choice in handlers:
            output_stream.write(handlers[choice]() + "\n")
            continue
        output_stream.write(_handle_mutation(target_graph, choice, input_stream, output_stream) + "\n")


def _handle_mutation(
    graph: OrthogonalGraph[str],
    choice: str,
    input_stream: TextIO,
    output_stream: TextIO,
) -> str:
    try:
        if choice == "3":
            output_stream.write("Vertex name: ")
            name = input_stream.readline().strip()
            graph.add_vertex(name)
            return f"Added vertex: {name}"
        if choice == "4":
            output_stream.write("Source vertex: ")
            src = input_stream.readline().strip()
            output_stream.write("Target vertex: ")
            dst = input_stream.readline().strip()
            graph.add_edge(src, dst)
            return f"Added edge: {src} -> {dst}"
        if choice == "5":
            output_stream.write("Vertex to remove: ")
            name = input_stream.readline().strip()
            graph.remove_vertex(name)
            return f"Removed vertex: {name}"
        return "Unknown command"
    except GraphError as exc:
        return f"Error: {exc}"


def main() -> None:
    """Точка входа консольного приложения."""
    import sys

    run_cli(sys.stdin, sys.stdout)


if __name__ == "__main__":
    main()
