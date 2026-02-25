#!/bin/bash

# Pre Deploy script for JWT Authorizer API Gateway - prep Python environment
set -ex

mkdir package
cat requirements.txt ../spring_upgrade/requirements.txt > comb_requirements.txt
pip install -r comb_requirements.txt -t package/ --quiet \
    --platform manylinux2014_x86_64 \
    --implementation cp \
    --python-version 3.13 \
    --only-binary=:all: --upgrade
rm comb_requirements.txt
cd package
#Solve issue with Windows flavour of library. Runtime.ImportModuleError: Unable to import module 'authorizer': cannot import name 'ObjectIdentifier' from 'cryptography.hazmat.bindings._rust'
pip install \
    --platform manylinux2014_x86_64 \
    --target . \
    --implementation cp \
    --python-version 3.13 \
    --only-binary=:all: --upgrade \
    cryptography

