"""
Setup file for Synapse module
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in cauldron_synapse/__init__.py
from cauldron_synapse import __version__ as version

setup(
    name="cauldron_synapse",
    version=version,
    description="Predictive & Prescriptive Business Intelligence Module",
    author="Your Organization",
    author_email="your-email@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)"""
Setup file for Synapse module
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in cauldron_synapse/__init__.py
from cauldron_synapse import __version__ as version

setup(
    name="cauldron_synapse",
    version=version,
    description="Predictive & Prescriptive Business Intelligence Module",
    author="Your Organization",
    author_email="your-email@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)