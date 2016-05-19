#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import mattersend
from setuptools import setup

README = os.path.realpath(os.path.sep.join([__file__, os.path.pardir, 'README.rst']))

setup(
    name=mattersend.name,
    py_modules=['mattersend'],
    entry_points={
        'console_scripts': [
            'mattersend=mattersend:main',
        ],
    },
    install_requires=["setproctitle", "requests"],
    tests_require=["nose", "coverage", "pyfakefs"],
    test_suite="nose.collector",
    version=mattersend.version,
    description=mattersend.description,
    long_description=open(README, 'r').read(),
    author="Massimiliano Torromeo",
    author_email="massimiliano.torromeo@gmail.com",
    url=mattersend.url,
    download_url="{}/tarball/v{}".format(mattersend.url, mattersend.version),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
        "Topic :: Utilities"
    ],
    license="MIT License"
)
