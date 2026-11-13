import pathlib
from setuptools import setup, find_packages

# Resolve the absolute path to the repository root for consistency
HERE = pathlib.Path(__file__).parent.resolve()

setup(
    name="jarvis",
    version="0.1.0",
    description="Jarvis personal assistant",
    packages=find_packages(where="jarvis"),
    package_dir={"": "jarvis"},
    include_package_data=True,
    zip_safe=False,
    # Dependencies can be added here if needed; for now rely on existing environment
)

