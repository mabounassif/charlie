#!/usr/bin/env python3
"""
Setup script for the Chess Opening Recommendation System.
"""

from setuptools import setup, find_packages

setup(
    name="chess-recommender",
    version="0.1.0",
    description="Personalized chess opening recommendation system",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "python-chess>=1.10.0",
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "pyyaml>=6.0",
        "tqdm>=4.65.0",
    ],
    python_requires=">=3.8",
) 