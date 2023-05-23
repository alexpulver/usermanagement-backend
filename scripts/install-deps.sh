#!/bin/bash

set -o errexit
set -o verbose

# Install AWS CDK Toolkit locally
npm install

# Install project dependencies
pip install \
  -r infrastructure/requirements.txt \
  -r runtime/api/requirements.txt \
  -r requirements-dev.txt
