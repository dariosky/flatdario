#!/usr/bin/env bash
# Bootstrap a local virtualenv using uv with Python 3.6 and install project deps.
set -euo pipefail

# NOTE: Targeting Python 3.10 (supported on Apple Silicon and x86_64).

set -euo pipefail

# Clear pyenv overrides to avoid picking up shims.
unset PYENV_VERSION
PATH="$(echo "$PATH" | tr ':' '\n' | grep -v '\.pyenv' | paste -sd: -)"
export PATH

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required (https://github.com/astral-sh/uv). Install it and re-run." >&2
  exit 1
fi

PYTHON_VERSION="3.10"
VENV_PATH=".venv"
PY_CMD="python3.10"

if uv help 2>/dev/null | grep -q "uv python"; then
  echo "Ensuring uv-managed Python ${PYTHON_VERSION} is available..."
  uv python install "${PYTHON_VERSION}"
else
  echo "uv without 'python' subcommand detected. Using system ${PY_CMD} if present." >&2
  if ! command -v "${PY_CMD}" >/dev/null 2>&1; then
    echo "${PY_CMD} not found. Please install Python ${PYTHON_VERSION} or upgrade uv to a version with 'uv python'." >&2
    exit 1
  fi
fi

echo "Creating venv at ${VENV_PATH} with Python ${PYTHON_VERSION}..."
uv venv --python "${PY_CMD}" "${VENV_PATH}"
source "${VENV_PATH}/bin/activate"

echo "Installing dependencies from requirements.txt via uv..."
uv pip install -r requirements.txt

echo "Environment ready. Activate with: source ${VENV_PATH}/bin/activate"
