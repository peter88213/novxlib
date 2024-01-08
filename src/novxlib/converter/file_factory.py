"""Provide a base class for factories that instantiate conversion objects.

Converter-specific file factories inherit from this class.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from abc import ABC, abstractmethod


class FileFactory(ABC):
    """Base class for conversion object factory classes."""

    def __init__(self, fileClasses=[]):
        """Write the parameter to a "private" instance variable.

        Optional arguments:
            _fileClasses -- list of classes from which an instance can be returned.
        """
        self._fileClasses = fileClasses

    @abstractmethod
    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion from a noveltree project.

        Positional arguments:
            sourcePath: str -- path to the source file to convert.
        """
        pass
