import sys
import re
from setuptools import setup

_version_re = re.compile(r"(?<=^__version__ = (\"|'))(.+)(?=\"|')")


def get_version(rel_path: str) -> str:
    """
    Searches for the ``__version__ = `` line in a source code file.

    https://packaging.python.org/en/latest/guides/single-sourcing-package-version/
    """
    with open(rel_path, "r") as f:
        matches = map(_version_re.search, f)
        filtered = filter(lambda m: m is not None, matches)
        version = next(filtered, None)
        if version is None:
            raise RuntimeError(f"Could not find __version__ in {rel_path}")
        return version.group(0)


requirements = []
with open("requirements.txt") as f:
    requirements = [
        line.strip()
        for line in f.readlines()
        if line.strip() and not line.strip().startswith("#")
    ]

# Make sure we are running python3.5+
if 10 * sys.version_info[0] + sys.version_info[1] < 35:
    sys.exit("Sorry, only Python 3.5+ is supported.")


def readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name="pfmongo",
    version=get_version("pfmongo/__main__.py"),
    description='A mongodb (portable) "pf" client',
    long_description=readme(),
    author="FNNDSC",
    author_email="dev@babymri.org",
    url="https://github.com/FNNDSC/pfmongo",
    packages=[
        "pfmongo",
        "pfmongo/commands",
        "pfmongo/commands/fop",
        "pfmongo/commands/dbop",
        "pfmongo/commands/clop",
        "pfmongo/commands/docop",
        "pfmongo/commands/stateop",
        "pfmongo/commands/slib",
        "pfmongo/db",
        "pfmongo/config",
        "pfmongo/models",
    ],
    install_requires=requirements,
    data_files=[
        ("", ["requirements.txt"]),
    ],
    entry_points={
        "console_scripts": [
            "pfmongo = pfmongo.__main__:main",
            "smashes = pfmongo.smashes:main",
        ]
    },
    license="MIT",
    zip_safe=False,
)
