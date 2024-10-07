import os
from datetime import datetime
from pathlib import Path

from setuptools import find_packages, setup

from version_tools import bump_version

PYTHON_VERSION = ">=3.9"

DEPENDENCIES = [
    "rich",
]

CURDIR = os.path.abspath(os.path.dirname(__file__))


setup(
    name="flatsearch",
    version=bump_version('flatsearch'),
    # version="1.0.0",
    author="Travis L. Seymour, PhD",
    author_email="nogard@ucsc.edu",
    description="Search for apps using flatpak and then install result with one click",
    long_description="Search for apps using flatpak and then install result with one click",
    long_description_content_type="text/markdown",
    url="https://github.com/travisseymour/flatsearch",
    packages=["flatsearch"],
    # include_package_data=False,
    # package_data={},
    # keywords=[],
    # scripts=[],
    entry_points={
        "console_scripts": ["flatsearch = flatsearch.__main__:main"],
    },
    # zip_safe=False,
    install_requires=DEPENDENCIES,
    # test_suite="",
    python_requires=PYTHON_VERSION,
    # license and classifier list:
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    license="License :: OSI Approved :: MIT License",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Utilities",
        "Topic :: Education",
    ],
)
