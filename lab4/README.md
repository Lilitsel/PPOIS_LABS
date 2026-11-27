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
