'''
Created on 25 apr 2019

@author: Matteo
'''
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="asyncio-orvibo",
    version="1.4",
    author="p3g4asus",
    author_email="fulminedipegasus@gmail.com",
    description="Asyncio module for Orvibo devices control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/p3g4asus/asyncio-orvibo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)