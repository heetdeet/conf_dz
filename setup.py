from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="conf_dz",
    version="1.0.0",
    author="Студент ИКБО-51-24 Малофеев Г.А.",
    description="Транслятор конфигурационного языка в XML (Вариант 16)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/heetdeet/conf_dz",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "lark-parser>=1.1.2",
    ],
    entry_points={
        "console_scripts": [
            "config-translator=src.config_parser:main",
        ],
    },
    test_suite="tests",
)