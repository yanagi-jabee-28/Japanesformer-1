from setuptools import setup, find_packages

setup(
    name="japanesformer",
    version="0.1.0",
    description="Vowel-fixed, reversible Japanese text transformer",
    author="Japanesformer Contributors",
    packages=find_packages(),
    install_requires=[
        "pykakasi>=2.2.1",
    ],
    entry_points={
        "console_scripts": [
            "japanesformer=japanesformer.cli:main",
            "japanesformer-gui=japanesformer.gui:main",
        ],
    },
    python_requires=">=3.9",
)
