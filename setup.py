from setuptools import setup, find_packages

setup(
    name="softmatch",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "regex",
    ],
    entry_points={
        "console_scripts": [
            "softmatch=softmatch.cli:main",
        ],
    },
    python_requires=">=3.6",
)
