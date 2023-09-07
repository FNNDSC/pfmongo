from importlib.metadata import Distribution
# from . import pfdb, persair

__pkg: Distribution         = Distribution.from_name(__package__)
__version__: str            = __pkg.version
