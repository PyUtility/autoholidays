#!/usr/bin/env python

import os
import sys

from setuptools import setup
from setuptools import find_packages

sys.path.append(
    os.path.join(os.path.dirname(__file__))
)

import autoholidays

setup(
    name = "autoholidays",
    version = autoholidays.__version__,
    description = "Intelligent algorithm-driven planner to calculate holidays.",
    long_description = open("README.md", "r").read(),
    long_description_content_type = "text/markdown",
    url = "https://github.com/PyUtility/autoholidays",
    packages = find_packages(
        exclude = ["tests*", "examples*"]
    ),
    install_requires = [
        "holidays>=0.92",
        "pydantic==2.12.5",
    ],
    classifiers = [
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        "Topic :: Office/Business",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires = ">=3.12"
)
