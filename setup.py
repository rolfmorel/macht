#!/usr/bin/env python

from setuptools import setup, find_packages

import macht


setup(
    name='macht',
    version=macht.__version__,
    author="Rolf Morel",
    author_email="rolfmorel@gmail.com",
    packages=find_packages(exclude=["tests"]),
    license='LGPLv3',
    install_requires=['blessed'],
    platforms=['Linux'],
    entry_points={'console_scripts': ('macht = macht.term:main')},
    description=("A 2048 clone in python with terminal ui frontend")
)
