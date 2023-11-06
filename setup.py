from setuptools import setup

setup(
    # Application name:
    name="mop",

    # Version number (initial):
    version="0.0.0",

    # Application author details:
    author="Quentin Guilloteau",
    author_email="Quentin.Guilloteau@univ-grenoble-alpes.fr",

    # Packages
    packages=["app"],

    # Include additional files into the package
    # include_package_data=True,
    entry_points={
        'console_scripts': ['mop=app.mop:main'],
    },

    # Details
    url="https://github.com/Nix4Science/n4s",

    #
    # license="LICENSE.txt",
    description="Creates Nix shells with desired package versions",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "pyyaml", "requests"
    ],
    include_package_data=True,
)
