#!/usr/bin/env bash
set -o errexit  # exit on error

echo "Installing python dependencies"
pip3 install -r requirements.txt
python -m pip install --upgrade pip

echo "Collecting staticfiles"
python3 manage.py collectstatic

echo "Building Tailwind CSS"
python3 manage.py tailwind start

echo "Running database migrations"
python3 manage.py migrate