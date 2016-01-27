#!/usr/bin/env python
# -*- coding:utf-8 -*-

import mattersend
from setuptools import setup
from pathlib import Path

README = Path(__file__) / '..' / 'README.rst'
README = README.resolve()

setup(
    name=mattersend.name,
    py_modules=['mattersend'],
    entry_points={
        'console_scripts': [
            'mattersend=mattersend:main',
        ],
    },
    install_requires=["setproctitle", "requests"],
    version=mattersend.version,
    description=mattersend.description,
    long_description=README.open().read(),
    author="Massimiliano Torromeo",
    author_email="massimiliano.torromeo@gmail.com",
    url=mattersend.url,
    download_url="{}/tarball/v{}".format(mattersend.url, mattersend.version),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
        "Topic :: Utilities"
    ],
    license="MIT License"
)
