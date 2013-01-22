# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

setup(
    name='trunk',
    version='0.2.0',
    description='Making postgres listen/notify easier.',
    long_description=readme,
    author='Timothée Peignier',
    author_email='timothee.peignier@tryphon.org',
    url='https://github.com/cyberdelia/trunk',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'psycopg2>=2.3.0',
    ],
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
