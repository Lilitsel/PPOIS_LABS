# Лабораторная работа №4 (Вариант 10)

- **Задание 1:** обобщённые функции `merge_sort` и `bozo_sort` для списков/массивов встроенных и пользовательских типов (`TaskRecord`).
- **Задание 2:** ориентированный граф на ортогональном списке смежности (`OrthogonalGraph[T]`) с двунаправленными прямыми, обратными и read-only итераторами.

## Запуск тестов и сборка из консоли

Выполните в каталоге `lab4`:
1. `python3 -m pip install -e ".[dev]" || python3 -m pip install pytest pytest-cov ruff build`
2. `pytest`
3. `ruff check .`
4. `python3 -m build`
5. `python3 -m lab4_pkg.cli`

## Additional Details (Option 10)

- **Sorting Algorithms**: `merge_sort` (stable, supports `key`, `reverse`, and `in_place`) and `bozo_sort` (randomized swaps with deterministic `rng` and `max_attempts` guard), plus `TaskRecord` comparisons.
- **Orthogonal Directed Graph**: `OrthogonalGraph[T]` with orthogonal edge links (`tail_value`, `head_value`, `next_out`, `next_in`, `active`), degree calculations (`in_degree`, `out_degree`, `vertex_degree`, `edge_degree`), `copy` / `assign_from`, comparison operators (`==`, `!=`, `<`, `<=`, `>`, `>=`), bidirectional/read-only iterators (`_BidirectionalIter`), iterator-based deletion (`remove_vertex_at`, `remove_edge_at`), and `ReadOnlyOrthogonalGraph[T]`.
- **CLI & Testing**: interactive `run_cli` menu (`demo_sorting`, `format_graph_report`, vertex/edge management) and `pytest` + `ruff` + `build` checks configured in `pyproject.toml`.
