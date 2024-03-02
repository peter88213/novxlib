"""Provide a class for ODS item list import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import re

from novxlib.model.world_element import WorldElement
from novxlib.novx_globals import ITEMLIST_SUFFIX
from novxlib.novx_globals import ITEM_PREFIX
from novxlib.novx_globals import IT_ROOT
from novxlib.novx_globals import _
from novxlib.novx_globals import string_to_list
from novxlib.ods.ods_reader import OdsReader


class OdsRItemList(OdsReader):
    """ODS item list reader."""
    DESCRIPTION = _('Item list')
    SUFFIX = ITEMLIST_SUFFIX
    _columnTitles = ['ID', 'Name', 'Description', 'Aka', 'Tags']

    def read(self):
        """Parse the file and get the instance variables.
        
        Parse the ODS file located at filePath, fetching the item attributes contained.
        Raise the "Error" exception in case of error. 
        Extends the superclass method.
        """
        super().read()
        self.novel.tree.delete_children(IT_ROOT)
        for cells in self._rows:
            if ITEM_PREFIX in cells[0]:
                itId = re.search(f'({ITEM_PREFIX}[0-9]+)', cells[0]).group(1)
                self.novel.tree.append(IT_ROOT, itId)
                if not itId in self.novel.items:
                    self.novel.items[itId] = WorldElement()
                if self.novel.items[itId].title or cells[1]:
                    self.novel.items[itId].title = cells[1].rstrip()
                if self.novel.items[itId].desc or cells[2]:
                    self.novel.items[itId].desc = cells[2].rstrip()
                if self.novel.items[itId].aka or cells[3]:
                    self.novel.items[itId].aka = cells[3].rstrip()
                if self.novel.items[itId].tags or cells[4]:
                    self.novel.items[itId].tags = string_to_list(cells[4], divider=self._DIVIDER)
