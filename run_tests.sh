#!/usr/bin/env bash
set -e

VENV_DIR="venv"
PYTHON="$VENV_DIR/bin/python3"
PIP="$VENV_DIR/bin/pip"
PYTEST="$VENV_DIR/bin/pytest"

if [ ! -d "$VENV_DIR" ]; then
    echo "Создаём виртуальное окружение..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Устанавливаем зависимости..."
$PIP install --upgrade pip
$PIP install -r requirements.txt

export PYTHONPATH=$(pwd)

echo "Запуск pytest..."
$PYTEST -v --durations=10
