#!/bin/bash 
# does this really need an license header it's just two commands lol

# This file is intended for developer usage

# Make sure you're using a venv with the absolutely minimum
# required to run MMV

# cd where the script is located, one folder above
cd "$(dirname "$0")"/../mmv

# Dump the stuff installed to a file
pip-chill > ./requirements-dev.txt
pip-chill > ./requirements.txt

# Remove pip-chill dependency for end user
sed -i '/^pip-chill/d' ./requirements.txt
