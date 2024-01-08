"""Provide a class for ODS character list import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import re

from novxlib.model.character import Character
from novxlib.novx_globals import CHARACTER_PREFIX
from novxlib.novx_globals import CHARLIST_SUFFIX
from novxlib.novx_globals import CR_ROOT
from novxlib.novx_globals import _
from novxlib.novx_globals import string_to_list
from novxlib.ods.ods_reader import OdsReader


class OdsRCharList(OdsReader):
    """ODS character list reader."""
    DESCRIPTION = _('Character list')
    SUFFIX = CHARLIST_SUFFIX
    _rowTitles = ['ID', 'Name', 'Full name', 'Aka', 'Description', 'Bio', 'Goals', 'Importance', 'Tags', 'Notes']

    def read(self):
        """Parse the file and get the instance variables.
        
        Parse the ODS file located at filePath, fetching the Character attributes contained.
        Raise the "Error" exception in case of error. 
        Extends the superclass method.
        """
        super().read()
        self.novel.tree.delete_children(CR_ROOT)
        for cells in self._rows:
            if CHARACTER_PREFIX in cells[0]:
                crId = re.search(f'({CHARACTER_PREFIX}[0-9]+)', cells[0]).group(1)
                self.novel.tree.append(CR_ROOT, crId)
                if not crId in self.novel.characters:
                    self.novel.characters[crId] = Character()
                if self.novel.characters[crId].title or cells[1]:
                    self.novel.characters[crId].title = cells[1]
                if self.novel.characters[crId].fullName or cells[2]:
                    self.novel.characters[crId].fullName = cells[2]
                if self.novel.characters[crId].aka or cells[3]:
                    self.novel.characters[crId].aka = cells[3]
                if self.novel.characters[crId].desc or cells[4]:
                    self.novel.characters[crId].desc = cells[4].rstrip()
                if self.novel.characters[crId].bio or cells[5]:
                    self.novel.characters[crId].bio = cells[5].rstrip()
                if self.novel.characters[crId].goals  or cells[6]:
                    self.novel.characters[crId].goals = cells[6].rstrip()
                if Character.MAJOR_MARKER in cells[7]:
                    self.novel.characters[crId].isMajor = True
                else:
                    self.novel.characters[crId].isMajor = False
                if self.novel.characters[crId].tags or cells[8]:
                    self.novel.characters[crId].tags = string_to_list(cells[8], divider=self._DIVIDER)
                if self.novel.characters[crId].notes or cells[9]:
                    self.novel.characters[crId].notes = cells[9].rstrip()
