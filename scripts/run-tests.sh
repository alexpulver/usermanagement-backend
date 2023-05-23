#!/bin/bash

set -o errexit
set -o verbose

targets=("${PWD}/infrastructure" "${PWD}/runtime")

# Find common security issues (https://bandit.readthedocs.io)
bandit --recursive "${targets[@]}"

# Python code formatter (https://black.readthedocs.io)
black --check --diff "${targets[@]}"

# Style guide enforcement (https://flake8.pycqa.org)
flake8 --config .flake8 "${targets[@]}"

# Sort imports (https://pycqa.github.io/isort)
isort --settings-path .isort.cfg --check --diff "${targets[@]}"

# Report code complexity (https://radon.readthedocs.io)
radon mi "${targets[@]}"

# Exit with non-zero status if code complexity exceeds thresholds (https://xenon.readthedocs.io)
xenon --max-absolute A --max-modules A --max-average A "${targets[@]}"

# Check dependencies for security issues (https://pyup.io/safety)
safety check \
  -r "${PWD}/infrastructure/requirements.txt" \
  -r "${PWD}/runtime/api/requirements.txt" \
  -r "${PWD}/requirements-dev.txt"

# Static type checker (https://mypy.readthedocs.io)
MYPYPATH="${PWD}/infrastructure" mypy --config-file .mypy.ini "${PWD}/infrastructure"
MYPYPATH="${PWD}/runtime/api" mypy --config-file .mypy.ini "${PWD}/runtime"

# Check for errors, enforce a coding standard, look for code smells (http://pylint.pycqa.org)
PYTHONPATH="${PWD}/infrastructure" pylint --rcfile .pylintrc "${PWD}/infrastructure"
PYTHONPATH="${PWD}/runtime/api" pylint --rcfile .pylintrc "${PWD}/runtime"

# Run tests and measure code coverage (https://coverage.readthedocs.io)
PYTHONPATH="${PWD}/infrastructure" coverage run -m unittest discover -v -s "${PWD}/infrastructure/tests"
PYTHONPATH="${PWD}/runtime/api" coverage run -m unittest discover -v -s "${PWD}/runtime/api/tests"
