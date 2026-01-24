"""
Setup script for AWS Sentinel
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aws-sentinel",
    version="0.1.2",
    author="Rishab Kumar",
    author_email="rishabkumar7@gmail.com",
    description="A security scanner for AWS resources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rishabkumar7/aws-sentinel",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "boto3>=1.34.0",
        "click>=8.0.0",
        "prettytable>=2.0.0",
        "colorama>=0.4.4",
    ],
    entry_points={
        "console_scripts": [
            "aws-sentinel=aws_sentinel.cli:main",
        ],
    },
)