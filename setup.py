#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requirements = [
    "snakemake",
]

test_requirements = [
]


setup(
    name='snakemk_util',
    version='0.0.1',
    description="utility functions for snakemake",
    author="Florian Hölzlwimmer",
    author_email='git.ich@frhoelzlwimmer.de',
    url='https://github.com/Hoeze/snakemk_util',
    long_description="utility functions for snakemake",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "develop": ["bumpversion",
                    "wheel",
                    "pytest",
                    "pytest-pep8",
                    "pytest-cov"],
    },
    license="MIT license",
    zip_safe=False,
    test_suite='tests',
    tests_require=test_requirements
)
