#!/usr/bin/env bash
pandoc readme.md --from markdown --to rst -s -o readme.rst
python3 -m pip install --upgrade twine
python3 -m pip install --upgrade build
python3 -m build
python3 -m twine upload --repository pypi dist/*

