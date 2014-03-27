#!/usr/bin/env python

import os
from setuptools import setup, find_packages

import macht


setup(
    name='macht',
    version=macht.__version__,
    description="A 2048 clone in python with terminal ui frontend",
    long_description=open(os.path.join(os.path.dirname(__file__),
                          'README.rst')).read(),
    author="Rolf Morel",
    author_email="rolfmorel@gmail.com",
    url="https://github.com/polyphemus/macht",
    packages=find_packages(exclude=["tests"]),
    license='LGPLv3',
    install_requires=['blessed', 'enum34'],
    entry_points={'console_scripts': ('macht = macht.term:main')},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Games/Entertainment :: Puzzle Games',
        'Topic :: Terminals'
        ]
)
