"""CliHax - a command reference manager for hackers and pentesters."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("clihax")
except PackageNotFoundError:  # running from a source tree that is not installed
    __version__ = "0.0.0+unknown"
