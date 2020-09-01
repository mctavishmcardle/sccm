from setuptools import find_packages, setup

setup(
    name="sccm",
    version="0.1.0",
    package_dir={"": "."},
    packages=find_packages(where="."),
    python_requires=">=3.7.*",
    install_requires=["vg>=1.7", "solidpython>=0.4", "numpy>=1.18"],
)
