import os

import setuptools


def get_version():
    package_init = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "fastapi_listing", "__init__.py"
    )
    with open(package_init) as f:
        for line in f:
            if line.startswith("__version__ ="):
                return line.split("=")[1].strip().strip("\"'")


def get_long_description():
    with open("README.md", "r") as fh:
        return fh.read()


setuptools.setup(
    name="fastapi-listing",
    version=get_version(),
    author="Danish Hasan",
    author_email="dh813030@gmail.com",
    description="Advaned Data Listing Library for FastAPI",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/danielhasan1/fastapi-listing",
    packages=setuptools.find_packages(exclude=["tests.*"]),
    package_data={"fastapi_listing": ["py.typed"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    keywords=["starlette", "fastapi", "pydantic", "sqlalchemy"],
    extras_require={
        "test": [
            "requests",
            "pytest>=6.2.4",
            "mypy>=0.971",
            "pytest-env>=0.6.2",
            "flake8>=3.9.2",
            "isort>=5.10.1",
            "pydantic>=1.5.0",
            "starlette>=0.21.0",
            "sqlalchemy>=2.0.7",
            "starlite>=1.38.0",
            "httpx>=0.23.0",
            "pytest-mock>=3.6.1",
            "fastapi>=0.92.0",
            "mypy>=0.971",
            "pytest-mypy>=0.9.1",
        ],
    },
)
