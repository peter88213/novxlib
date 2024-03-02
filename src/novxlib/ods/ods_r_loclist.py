"""Provide a class for ODS location list import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import re

from novxlib.model.world_element import WorldElement
from novxlib.novx_globals import LC_ROOT
from novxlib.novx_globals import LOCATION_PREFIX
from novxlib.novx_globals import LOCLIST_SUFFIX
from novxlib.novx_globals import _
from novxlib.novx_globals import string_to_list
from novxlib.ods.ods_reader import OdsReader


class OdsRLocList(OdsReader):
    """ODS location list reader. """
    DESCRIPTION = _('Location list')
    SUFFIX = LOCLIST_SUFFIX
    _columnTitles = ['ID', 'Name', 'Description', 'Aka', 'Tags']

    def read(self):
        """Parse the file and get the instance variables.
        
        Parse the ODS file located at filePath, fetching the location attributes contained.
        Raise the "Error" exception in case of error. 
        Extends the superclass method.
        """
        super().read()
        self.novel.tree.delete_children(LC_ROOT)
        for cells in self._rows:
            if LOCATION_PREFIX in cells[0]:
                lcId = re.search(f'({LOCATION_PREFIX}[0-9]+)', cells[0]).group(1)
                self.novel.tree.append(LC_ROOT, lcId)
                if not lcId in self.novel.locations:
                    self.novel.locations[lcId] = WorldElement()
                if self.novel.locations[lcId].title or cells[1]:
                    self.novel.locations[lcId].title = cells[1].rstrip()
                if self.novel.locations[lcId].desc or cells[2]:
                    self.novel.locations[lcId].desc = cells[2].rstrip()
                if self.novel.locations[lcId].aka or cells[3]:
                    self.novel.locations[lcId].aka = cells[3].rstrip()
                if self.novel.locations[lcId].tags or cells[4]:
                    self.novel.locations[lcId].tags = string_to_list(cells[4], divider=self._DIVIDER)
