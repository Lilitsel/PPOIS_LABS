from io import StringIO

from lab4_pkg.cli import demo_sorting, format_graph_report, run_cli
from lab4_pkg.graph import OrthogonalGraph


def test_demo_and_report() -> None:
    sorting_out = demo_sorting([3, 1, 2])
    assert "Merge sort:    [1, 2, 3]" in sorting_out
    assert "Bozo sort:     [1, 2, 3]" in sorting_out

    graph = OrthogonalGraph[str]()
    graph.add_vertex("X")
    graph.add_vertex("Y")
    graph.add_edge("X", "Y")
    report = format_graph_report(graph)
    assert "Vertices (2): ['X', 'Y']" in report
    assert "Edges (1):    [('X', 'Y')]" in report


def test_run_cli_commands_and_error_handling() -> None:
    script = "\n".join(
        [
            "1",
            "3",
            "Start",
            "3",
            "Start",
            "3",
            "End",
            "4",
            "Start",
            "End",
            "2",
            "5",
            "Start",
            "99",
            "0",
        ]
    ) + "\n"
    out = StringIO()
    code = run_cli(StringIO(script), out)
    output = out.getvalue()
    assert code == 0
    assert "Added vertex: Start" in output
    assert "Error:" in output
    assert "Added edge: Start -> End" in output
    assert "Removed vertex: Start" in output
    assert "Unknown command" in output
