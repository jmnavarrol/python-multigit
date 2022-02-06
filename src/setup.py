#!/usr/bin/env python

# Workaround allow editable mode pip install along pyproject.toml file
# See https://stackoverflow.com/questions/62983756/what-is-pyproject-toml-file-for
import setuptools

if __name__ == "__main__":
	setuptools.setup()
	