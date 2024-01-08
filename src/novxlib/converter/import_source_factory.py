"""Provide a factory class for a document object to read.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.converter.file_factory import FileFactory
from novxlib.novx_globals import Error
from novxlib.novx_globals import _


class ImportSourceFactory(FileFactory):
    """A factory class that instantiates a documente object to read."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion to a noveltree project.       

        Positional arguments:
            sourcePath: str -- path to the source file to convert.

        Return a tuple with two elements:
        - sourceFile: a Novel subclass instance, or None in case of error
        - targetFile: None

        Raise the "Error" exception in case of error. 
        """
        for fileClass in self._fileClasses:
            if fileClass.SUFFIX is not None:
                if sourcePath.endswith(f'{fileClass.SUFFIX }{fileClass.EXTENSION}'):
                    sourceFile = fileClass(sourcePath, **kwargs)
                    return sourceFile, None

        raise Error(f'{_("This document is not meant to be written back")}.')
