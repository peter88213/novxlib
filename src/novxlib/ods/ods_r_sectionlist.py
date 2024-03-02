"""Provide a class for ODS section list import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import re

from novxlib.model.section import Section
from novxlib.novx_globals import SECTIONLIST_SUFFIX
from novxlib.novx_globals import SECTION_PREFIX
from novxlib.novx_globals import _
from novxlib.novx_globals import string_to_list
from novxlib.ods.ods_reader import OdsReader


class OdsRSectionList(OdsReader):
    """ODS section list reader. """
    DESCRIPTION = _('Section list')
    SUFFIX = SECTIONLIST_SUFFIX
    _rowTitles = ['Section link', 'Section title', 'Section description', 'Tags', 'Section notes', 'A/R',
                 'Goal', 'Conflict', 'Outcome', 'Section', 'Words total',
                 'Word count', 'Characters', 'Locations', 'Items']

    def read(self):
        """Parse the file and get the instance variables.
        
        Parse the ODS file located at filePath, fetching the Section attributes contained.
        Extends the superclass method.
        """
        super().read()
        for cells in self._rows:
            i = 0
            if SECTION_PREFIX in cells[i]:
                scId = re.search(f'({SECTION_PREFIX}[0-9]+)', cells[0]).group(1)
                if not scId in self.novel.sections:
                    self.novel.sections[scId] = Section()
                i += 1
                self.novel.sections[scId].title = cells[i].rstrip()
                i += 1
                self.novel.sections[scId].desc = cells[i].rstrip()
                i += 1
                if cells[i] or self.novel.sections[scId].date:
                    self.novel.sections[scId].date = cells[i]
                i += 1
                if cells[i] or self.novel.sections[scId].time:
                    self.novel.sections[scId].time = cells[i]
                i += 1
                if cells[i] or self.novel.sections[scId].tags:
                    self.novel.sections[scId].tags = string_to_list(cells[i], divider=self._DIVIDER)
                i += 1
                if cells[i] or self.novel.sections[scId].notes:
                    self.novel.sections[scId].notes = cells[i].rstrip()
                i += 1
                try:
                    self.novel.sections[scId].scPacing = Section.PACING.index(cells[i])
                except ValueError:
                    pass
                    # Section pacing type remains None and will be ignored when
                    # writing back.
                i += 1
                if cells[i] or self.novel.sections[scId].goal:
                    self.novel.sections[scId].goal = cells[i].rstrip()
                i += 1
                if cells[i] or self.novel.sections[scId].conflict:
                    self.novel.sections[scId].conflict = cells[i].rstrip()
                i += 1
                if cells[i] or self.novel.sections[scId].outcome:
                    self.novel.sections[scId].outcome = cells[i].rstrip()
                i += 1
                # Don't write back sectionCount
                i += 1
                # Don't write back wordCount
                i += 1
                # Don't write back section words total
                i += 1
                # Can't write back character IDs, because self.characters is None.
                i += 1
                # Can't write back location IDs, because self.locations is None.
                i += 1
                # Can't write back item IDs, because self.items is None.
