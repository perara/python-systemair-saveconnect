#!/usr/bin/env bash
python3 setup.py sdist bdist_wheel
python3 -m pip install --user --upgrade twine
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
