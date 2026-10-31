"""CliHax - a command reference manager for hackers and pentesters."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("clihax")
except PackageNotFoundError:  # running from a source tree that is not installed
    __version__ = "0.0.0+unknown"

# Project details shown by `clihax info` (a test keeps these equal to pyproject.toml).
__author__ = "Harikrishnan-P97"
__license__ = "MIT"
__repo_url__ = "https://github.com/Harikrishnan-P97/clihax"
