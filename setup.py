from setuptools import setup, find_packages
import os

# Helper function to read requirements.txt
def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read the requirements from requirements.txt
requirements = parse_requirements('requirements.txt')

setup(
    name="HDF5_BLS",
    version="0.1.0",
    description="A package to read and write HDF5 files for the BioBrillouin lab",
    author="Pierre Bouvet",
    author_email="pierre.bouvet@meduniwien.ac.at",
    packages=find_packages(),
    install_requires=requirements,  # Use parsed requirements
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)