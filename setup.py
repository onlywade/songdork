import io

from setuptools import find_packages
from setuptools import setup

setup(
    name="twongs",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask"],
    extras_require={"test": ["pytest", "coverage"]},
)
