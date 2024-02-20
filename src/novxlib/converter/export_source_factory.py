"""Provide a factory class for a novx file object to read.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import os

from novxlib.converter.file_factory import FileFactory
from novxlib.novx_globals import Error
from novxlib.novx_globals import _
from novxlib.novx_globals import norm_path


class ExportSourceFactory(FileFactory):
    """A factory class that instantiates a novx file object to read."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion from a novelibre project.

        Positional arguments:
            sourcePath: str -- path to the source file to convert.

        Return a tuple with two elements:
        - sourceFile: a NovxFile subclass instance
        - targetFile: None

        Raise the "Error" exception in case of error. 
        """
        __, fileExtension = os.path.splitext(sourcePath)
        for fileClass in self._fileClasses:
            if fileClass.EXTENSION == fileExtension:
                sourceFile = fileClass(sourcePath, **kwargs)
                return sourceFile, None

        raise Error(f'{_("File type is not supported")}: "{norm_path(sourcePath)}".')
