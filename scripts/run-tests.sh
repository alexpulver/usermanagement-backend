#!/bin/bash

set -o errexit
set -o verbose

targets=("service" "tests" "toolchain" "app.py" "constants.py")

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
safety check -r service/api/requirements.txt -r requirements.txt -r requirements-dev.txt

# Static type checker (https://mypy.readthedocs.io)
MYPYPATH="${PWD}" mypy --config-file .mypy.ini --exclude service/api "${targets[@]}"
MYPYPATH="${PWD}/service/api" mypy --config-file .mypy.ini --explicit-package-bases service/api

# Check for errors, enforce a coding standard, look for code smells (http://pylint.pycqa.org)
PYTHONPATH="${PWD}" pylint --rcfile .pylintrc --ignore service/api "${targets[@]}"
PYTHONPATH="${PWD}/service/api" pylint --rcfile .pylintrc service/api

# Run tests and measure code coverage (https://coverage.readthedocs.io)
coverage run -m unittest discover -s tests
(cd "${PWD}/service/api"; coverage run -m unittest discover -s tests)
