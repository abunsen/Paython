import os

# TODO Make paython importable
# it can't be imported since it tries to use suds
# import paython

from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "paython",
    version = "0.0.3",
    author = "Auston Bunsen, Igor Guerrero",
    author_email = "auston.bunsen@gmail.com",
    description = ("Trying to make it easy to accept payments in Python."),
    license = "MIT",
    keywords = "payments gateways creditcards processing",
    url = "https://github.com/abunsen/Paython",
    packages=find_packages(),
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        'paython.keys': ['*.pem-file'],
    },
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.6",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        'suds==0.4',
        'stripe==1.7.4',
        'samurai==0.6',
    ]
)
