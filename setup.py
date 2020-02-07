#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

requirements_dev = [
    'pip',
    'bump2version',
    'wheel',
    'watchdog',
    'flake8',
    'tox',
    'coverage',
    'Sphinx',
    'twine',
    'pytest',
]

setup_requirements = []

test_requirements = ['pytest>=3', ]

setup(
    author="Goncalo Magno",
    author_email='goncalo@gmagno.dev',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A CLI tool to monitor temp while running a child process",
    entry_points={
        'console_scripts': [
            'tmon=tmon.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='tmon',
    name='tmon',
    packages=find_packages(include=['tmon', 'tmon.*']),
    setup_requires=setup_requirements,
    extras_require={
            'dev': requirements_dev,
    },
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/gmagno/tmon',
    version='0.3.4',
    zip_safe=False,
)
