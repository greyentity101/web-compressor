from setuptools import setup, find_packages

setup(
    name="webcompressor-pro",
    version="1.0.0",
    description="Advanced web asset compaction algorithm surpassing industry standards",
    author="Mohit Kumar",
    author_email="mohitjat202@gmail.com",
    url="https://github.com/greyentity101/web-compressor",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "webcompressor=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
