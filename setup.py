import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fast-cli", # Replace with your own username
    version="0.0.1",
    author="Bastiaan van der Weij",
    author_email="author@example.com",
    description="Tools for building command-line interfaces from decorated function signatures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bjvanderweij/fastcli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.8',
)
