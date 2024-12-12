from setuptools import setup, find_packages

setup(
    name='my_project',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A description of your project.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my_project',
    packages=find_packages(),
    install_requires=[
        # Add dependencies here
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
