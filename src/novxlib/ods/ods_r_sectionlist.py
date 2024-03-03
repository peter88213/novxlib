"""Provide a class for ODS section list import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import re
from datetime import date, time

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
    _columnTitles = [
        'Section link', 'Section title', 'Section description',
        'Date', 'Time', 'Tags', 'Section notes', 'A/R',
        'Goal', 'Conflict', 'Outcome', 'Section', 'Words total',
        'Word count', 'Characters', 'Locations', 'Items'
        ]
    _idPrefix = SECTION_PREFIX

    def read(self):
        """Parse the ODS file located at filePath, fetching the Section attributes contained.
        
        Extends the superclass method.
        """
        super().read()
        for scId in self.novel.sections:

            #--- title
            try:
                title = self._columns['Section title'][scId]
            except:
                pass
            else:
                self.novel.sections[scId].title = title.rstrip()

            #--- desc
            try:
                desc = self._columns['Section description'][scId]
            except:
                pass
            else:
                self.novel.sections[scId].desc = desc.rstrip()

            #--- notes
            try:
                notes = self._columns['Section notes'][scId]
            except:
                pass
            else:
                self.novel.sections[scId].notes = notes.rstrip()

            #--- date
            try:
                scDate = self._columns['Date'][scId]
                date.fromisoformat(scDate)
            except:
                pass
            else:
                self.novel.sections[scId].date = scDate

            #--- time
            try:
                scTime = self._columns['Time'][scId]
                time.fromisoformat(scTime)
            except:
                pass
            else:
                self.novel.sections[scId].datetime = scTime

            #--- tags
            try:
                tags = self._columns['Tags'][scId]
            except:
                pass
            else:
                if tags:
                    self.novel.sections[scId].tags = string_to_list(tags, divider=self._DIVIDER)

            #--- A/R/C
            try:
                ar = self._columns['A/R'][scId]
            except:
                pass
            else:
                if ar:
                    try:
                        self.novel.sections[scId].scPacing = Section.PACING.index(ar)
                    except ValueError:
                        pass

            #--- goal
            try:
                goal = self._columns['Goal'][scId]
            except:
                pass
            else:
                self.novel.sections[scId].goal = goal.rstrip()

            #--- conflict
            try:
                conflict = self._columns['Conflict'][scId]
            except:
                pass
            else:
                self.novel.sections[scId].conflict = conflict.rstrip()

            #--- outcome
            try:
                outcome = self._columns['Outcome'][scId]
            except:
                pass
            else:
                self.novel.sections[scId].outcome = outcome.rstrip()

