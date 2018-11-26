import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='python-systemair-savecair',
    version='1.0.0',
    author="Per-Arne Andersen",
    author_email="per@sysx.no",
    description="A Systemair-savecair API Wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/perara/python-systemair-savecair",
    packages=setuptools.find_packages(),
    license='MIT',
    install_requires=[
        'websockets==6.0'
    ],
    package_data = {
        '': ['*parameters.txt']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
