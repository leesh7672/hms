#!/usr/bin/env python3
import io
from setuptools import find_packages, setup

def long_description():
    with io.open('README', 'r', encoding='utf-8') as f:
        readme = f.read()
    return readme

setup(
    name='hcl',
    version='1.0',
    description='HCL Management software rewritten into python.',
    long_description=long_description(),
    author='Seho Lee',
    author_email='leesh7672@knou.ac.kr',
    packages=find_packages('cihai'),
    zip_safe=True
    )
