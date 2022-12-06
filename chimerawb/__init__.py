"""A pipeline to generate wideband TOAs from CHIME fold mode data."""

from . import exec, fileutils, session, toautils, validation, _version

__all__ = ["exec", "fileutils", "session", "toautils", "validation"]

__version__ = _version.get_versions()["version"]
