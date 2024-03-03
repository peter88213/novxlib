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
    _idPrefix = '??'

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
        self._columns = {}
        # dict: {column title, {element ID, cell content}}

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
        rows = parser.get_rows(self.filePath, cellsPerRow)
        for row in rows:
            if len(row) != cellsPerRow:
                print(row)
                print(len(row), cellsPerRow)
                raise Error(f'{_("Wrong table structure")}.')

        for title in rows[0]:
            self._columns[title] = {}
        for row in rows:
            if row[0].startswith(self._idPrefix):
                for i, col in enumerate(self._columns):
                    self._columns[col][row[0]] = row[i]

