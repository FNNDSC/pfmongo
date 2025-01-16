from importlib.metadata import Distribution, PackageNotFoundError

__version__ = "0.9.900"

__pkg: Distribution
__version__: str
__pkg_name__: str

try:
    __pkg = Distribution.from_name(__package__)
    __version__ = __pkg.version
    __pkg_name__ = __pkg.metadata["Name"]
except PackageNotFoundError:
    __pkg = None
    __pkg_name__ = "pfmongo"
