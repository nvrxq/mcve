from setuptools import Extension, dist, find_packages, setup


if __name__ == "__main__":
    __version__ = "0.0.1"
    setup(
        name="mcve",
        version=__version__,
        package_dir={"": "mcve"},
        packages=find_packages("mcve"),
        description="Make Computer Vision Easy Lib",
    )
