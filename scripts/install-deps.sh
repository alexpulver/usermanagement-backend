#!/bin/bash

set -o errexit
set -o verbose

# Install AWS CDK Toolkit locally
npm install

# Install project dependencies
pip install -r backend/api/runtime/requirements.txt -r requirements.txt -r requirements-dev.txt
