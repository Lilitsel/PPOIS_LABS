#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

echo "=== 1. Linter (flake8) ==="
flake8 computer_system tests run_cli.py

echo "=== 2. Tests & Coverage (pytest >= 90%) ==="
pytest --cov=computer_system --cov-report=term-missing --cov-fail-under=90

echo "=== 3. Build artifact (zipapp) ==="
python3 -m zipapp computer_system -m "computer_system.cli.menu:run_cli" -o computer_system.pyz
ls -lh computer_system.pyz

echo "=== All checks and build succeeded ==="
