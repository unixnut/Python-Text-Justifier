#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'pyphen>=0.10.0']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Alastair Irvine",
    author_email='alastair@plug.org.au',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Justify and hyphenate text in files and/or standard input",
    entry_points={
        'console_scripts': [
            'text-justifier=justifier.cli:main',
            'justify=justifier.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='justifier, text formatting',
    name='text-justifier',
    packages=find_packages(include=['justifier', 'justifier.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/unixnut/Python-Text-Justifier',
    version='0.9.0',
    zip_safe=False,
)
