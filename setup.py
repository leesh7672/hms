#!/usr/bin/env python3
import io
from setuptools import find_packages, setup

def long_description():
    return '''
    HCL Management software
    '''

setup(
    name='hms',
    version='2.0',
    description='HCL Management software rewritten into python.',
    long_description=long_description(),
    author='Seho Lee',
    author_email='leesh7672@knou.ac.kr',
    packages=find_packages(),
    install_requires=['cihai', 'lxml'],
    zip_safe=True
    )
