#!/bin/bash

set -o errexit
set -o verbose

# Install AWS CDK CLI locally
npm install

# Install project dependencies
pip install -r service/api/requirements.txt -r requirements.txt -r requirements-dev.txt
