#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
from setuptools import setup
from setuptools import find_packages

PKG = "autoholidays" # Edit with your package name

# Version File Implementation: https://stackoverflow.com/a/7071358
VERSIONFILE = os.path.join(PKG, "VERSION")
try:
    VERSION = open(VERSIONFILE, "r").read() # always read as str()
except FileNotFoundError as err:
    raise RuntimeError(f'is PKG = {PKG} correctly defined? {err}')

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name         = PKG,
    version      = VERSION,
    author       = "Debmalya Pramanik",
    author_email = "",

    description                   = "Create an Optimal Holiday Planner",
    long_description              = long_description,
    long_description_content_type = "text/markdown",

    url         = "https://github.com/ZenithClown/auto-holidays",
    packages    = find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires  = ">=3.10",  # Specify Requirement
    install_requires = [] # Add/Edit as Required
)
