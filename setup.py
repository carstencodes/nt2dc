#!/usr/bin/env python

from setuptools import setup, find_packages

__VERSION__ = "0.6.0"

long_description: str = ""
with open("README.md", "r") as read_me_file:
    long_description = read_me_file.read()

setup(
    name="nt2dc",
    version=__VERSION__,
    license="BSD 3-Clause",
    author="Carsten Igel",
    author_email="cig@bite-that-bit.de",
    description="Converter for dataclasses and named tuples",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    url="https://github.com/carstencodes/nt2dc",
    install_requires=[],
    package_dir={"": "src"},
    keywords="NamedTuple DataClasses",
    python_requires=">=3.8, < 4",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System",
        "Typing :: Typed",
    ],
)