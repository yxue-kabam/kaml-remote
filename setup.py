"""kaml-remote script"""
from setuptools import setup, find_packages

setup(
    name='kaml-remote',
    version='0.0.1',
    description='Kaml remote',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
        'kubernetes',
    ],
    url="https://github.com/stas-kabam/kaml-remote",
    entry_points={
        'console_scripts': [
            'kaml-remote=kaml_remote:main',
        ],
    },
)
