from setuptools import find_packages, setup

src_dir = "lib"

setup(
    name="sccm",
    version="0.1.0",
    package_dir={"": src_dir},
    packages=find_packages(where=src_dir),
    python_requires=">=3.7.*",
    install_requires=["vg>=1.7", "solidpython>=0.4", "numpy>=1.18"],
)
