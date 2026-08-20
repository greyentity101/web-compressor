from setuptools import setup, find_packages

setup(
    name="web-compressor-pro",
    version="2.0.0",
    description="Production-grade, semantic-preserving web asset compressor for HTML, CSS, and JavaScript",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mohit Kumar",
    license="MIT",
    py_modules=["compressor", "js_compressor", "css_compressor", "html_compressor", "cli", "cache", "benchmark"],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "web-compressor=cli:main",
            "webcompress=cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Software Development :: Build Tools",
        "Development Status :: 4 - Beta",
    ],
)
