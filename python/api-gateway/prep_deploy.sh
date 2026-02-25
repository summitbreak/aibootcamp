#!/bin/bash

# Pre Deploy script for JWT Authorizer API Gateway - prep Python environment
set -e

mkdir package

pip install -r requirements.txt -t package/ --quiet \
    --platform manylinux2014_x86_64 \
    --implementation cp \
    --python-version 3.13 \
    --only-binary=:all: --upgrade

#Solve issue with Windows flavour of library. Runtime.ImportModuleError: Unable to import module 'authorizer': cannot import name 'ObjectIdentifier' from 'cryptography.hazmat.bindings._rust'
pip install \
    --platform manylinux2014_x86_64 \
    --target . \
    --implementation cp \
    --python-version 3.13 \
    --only-binary=:all: --upgrade \
    cryptography

