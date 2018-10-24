"""kaml-remote script"""
from setuptools import setup, find_packages

setup(
    name='kaml-remote',
    version='0.0.1',
    description='The script run kaml in Kubernetes as a job',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'kubernetes',
    ],
    url="https://github.com/stas-kabam/kaml-remote"
)