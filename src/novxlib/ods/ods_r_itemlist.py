"""Provide a class for ODS item list import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import ITEMLIST_SUFFIX
from novxlib.novx_globals import ITEM_PREFIX
from novxlib.novx_globals import _
from novxlib.novx_globals import string_to_list
from novxlib.ods.ods_reader import OdsReader


class OdsRItemList(OdsReader):
    """ODS item list reader."""
    DESCRIPTION = _('Item list')
    SUFFIX = ITEMLIST_SUFFIX
    _columnTitles = ['ID', 'Name', 'Description', 'Aka', 'Tags']
    _idPrefix = ITEM_PREFIX

    def read(self):
        """Parse the ODS file located at filePath, fetching the item attributes contained.

        Extends the superclass method.
        """
        super().read()
        for itId in self.novel.items:

            #--- name
            try:
                title = self._columns['Name'][itId]
            except:
                pass
            else:
                self.novel.items[itId].title = title.rstrip()

            #--- desc
            try:
                desc = self._columns['Description'][itId]
            except:
                pass
            else:
                self.novel.items[itId].desc = desc.rstrip()

            #--- aka
            try:
                desc = self._columns['Aka'][itId]
            except:
                pass
            else:
                self.novel.items[itId].aka = desc.rstrip()

            #--- tags
            try:
                tags = self._columns['Tags'][itId]
            except:
                pass
            else:
                if tags:
                    self.novel.items[itId].tags = string_to_list(tags, divider=self._DIVIDER)

