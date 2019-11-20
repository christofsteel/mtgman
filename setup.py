from setuptools import setup, find_packages

setup(
        name="mtgman",
        version="0.1",
        packages=find_packages(),
        author="Christoph Stahl",
        author_email="christoph.stahl@tu-dortmund.de",
        install_requires=["sqlalchemy", "scrython", "ply"],
        entry_points = {
            "console_scripts": [
                "mtgman = mtgman.main:main"
                ]
            }
        )
