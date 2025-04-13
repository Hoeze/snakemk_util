#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requirements = [
    "snakemake>=7,<8",
]

test_requirements = [
    "pytest>=3.3.1",
    "pytest-xdist",
    "pytest-pep8",
    "pytest-mock",
    "pytest-cov",
]

dev_requirements = [
    "bumpversion",
    "wheel",
]

setup(
    name='snakemk_util',
    version='1.0.3',
    description="utility functions for snakemake",
    author="Florian Hölzlwimmer",
    author_email='git.ich@frhoelzlwimmer.de',
    url='https://github.com/Hoeze/snakemk_util',
    long_description="utility functions for snakemake",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "develop": dev_requirements,
    },
    license="MIT license",
    zip_safe=False,
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': ['snakemk_util = snakemk_util.main:main']
    }
)
