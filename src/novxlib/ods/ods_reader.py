"""Provide an abstract ODS file reader class.

Other ODS file readers inherit from this class.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from abc import ABC, abstractmethod

from novxlib.file.file_export import FileExport
from novxlib.novx_globals import Error
from novxlib.novx_globals import _
from novxlib.odf.odf_reader import OdfReader
from novxlib.ods.ods_parser import OdsParser


class OdsReader(OdfReader, ABC):
    """Abstract OpenDocument spreadsheet document reader."""
    EXTENSION = '.ods'
    # overwrites File.EXTENSION
    _SEPARATOR = ','
    # delimits data fields within a record.
    _columnTitles = []

    _DIVIDER = FileExport._DIVIDER

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath: str -- path to the file represented by the File instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._rows = []

    @abstractmethod
    def read(self):
        """Parse the file and get the instance variables.
        
        Parse the ODS file located at filePath, fetching the rows.
        Check the number of fields in each row.
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """
        self._rows = []
        cellsPerRow = len(self._columnTitles)
        parser = OdsParser()
        self._rows = parser.get_rows(self.filePath, cellsPerRow)
        for row in self._rows:
            if len(row) != cellsPerRow:
                print(row)
                print(len(row), cellsPerRow)
                raise Error(f'{_("Wrong table structure")}.')

        for i, colTitle in enumerate(self._columnTitles):
            if colTitle != self._rows[0][i]:
                print(f'\n{self._rows[0]}')
                print(self._columnTitles)
                raise Error(f'{_("Wrong table structure")}.')

