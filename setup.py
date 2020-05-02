# -*- coding: utf-8 -*-

# based on: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ablib',
    version='0.1.0',
    description='My common utility and tools',
    long_description=readme,
    author='Dr. Zej B',
    author_email='borand@borowiec.ca',
    url='https://github.com/borand/ablib',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
