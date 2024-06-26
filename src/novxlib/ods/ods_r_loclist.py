"""Provide a class for ODS location list import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
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
    _idPrefix = LOCATION_PREFIX

    def read(self):
        """Parse the ODS file located at filePath, fetching the location attributes contained.
        
        Extends the superclass method.
        """
        super().read()
        for lcId in self.novel.locations:

            #--- name
            try:
                title = self._columns['Name'][lcId]
            except:
                pass
            else:
                self.novel.locations[lcId].title = title.rstrip()

            #--- desc
            try:
                desc = self._columns['Description'][lcId]
            except:
                pass
            else:
                self.novel.locations[lcId].desc = desc.rstrip()

            #--- aka
            try:
                desc = self._columns['Aka'][lcId]
            except:
                pass
            else:
                self.novel.locations[lcId].aka = desc.rstrip()

            #--- tags
            try:
                tags = self._columns['Tags'][lcId]
            except:
                pass
            else:
                if tags:
                    self.novel.locations[lcId].tags = string_to_list(tags, divider=self._DIVIDER)

