"""
Setup script for Code-Mixed Pedagogical Flow Extractor
Enables installation with: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name='pedagogical-flow-extractor',
    version='1.0.0',
    description='Extract pedagogical flow and concept dependencies from code-mixed educational videos',
    author='iREL 2026 Project',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'openai-whisper',
        'torch',
        'yt-dlp',
        'spacy>=3.7.0',
        'nltk>=3.8.1',
        'sentence-transformers',
        'networkx',
        'matplotlib',
        'pyvis',
        'pyyaml',
        'deep-translator',
        'httpx>=0.24.0',
    ],
    extras_require={
        'dev': [
            'pytest',
            'black',
            'flake8',
        ]
    },
    entry_points={
        'console_scripts': [
            'irel-extract=example_usage:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
