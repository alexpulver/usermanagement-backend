#!/bin/bash

set -o errexit
set -o verbose

targets=("service" "tests" "toolchain" "constants.py" "main.py")

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
# See https://data.safetycli.com/v/70612/97c/ for 70612 ignore reason.
safety check -i 70612 -r service/api/app/requirements.txt -r requirements.txt -r requirements-dev.txt

# Static type checker (https://mypy.readthedocs.io)
MYPYPATH="${PWD}" mypy --config-file .mypy.ini --exclude service/api/app "${targets[@]}"
MYPYPATH="${PWD}/service/api/app" mypy --config-file .mypy.ini --explicit-package-bases service/api/app

# Check for errors, enforce a coding standard, look for code smells (http://pylint.pycqa.org)
PYTHONPATH="${PWD}" pylint --rcfile .pylintrc --ignore service/api/app "${targets[@]}"
PYTHONPATH="${PWD}/service/api/app" pylint --rcfile .pylintrc service/api/app

# Run tests and measure code coverage (https://coverage.readthedocs.io)
coverage run -m unittest discover -s tests
(cd "${PWD}/service/api/app"; coverage run -m unittest discover -s tests)
