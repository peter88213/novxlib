"""Provide a class for ODS plot grid import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import re
from datetime import date, time

from novxlib.model.section import Section
from novxlib.novx_globals import GRID_SUFFIX, AC_ROOT
from novxlib.novx_globals import SECTION_PREFIX
from novxlib.novx_globals import _
from novxlib.novx_globals import string_to_list
from novxlib.ods.ods_reader import OdsReader


class OdsRGrid(OdsReader):
    """ODS section list reader. """
    DESCRIPTION = _('Plot grid')
    SUFFIX = GRID_SUFFIX
    _columnTitles = [
        'Link',
        'Section',
        'Date',
        'Time',
        'Day',
        'Title',
        'Description',
        'Viewpoint',
        'Tags',
        'A/R',
        'Goal',
        'Conflict',
        'Outcome',
        'Notes',
        ]
    _idPrefix = SECTION_PREFIX

    def read(self):
        """Parse the ODS file located at filePath, fetching the Section attributes contained.
        
        Extends the superclass method.
        """
        arcs = self.novel.tree.get_children(AC_ROOT)
        for acId in arcs:
            self._columnTitles.append(acId)
        super().read()
        for scId in self.novel.sections:

            #--- arc notes
            for acId in arcs:
                try:
                    arcNote = self._columns[acId][scId]
                except:
                    pass
                else:
                    plotNotes = self.novel.sections[scId].plotNotes
                    if not plotNotes:
                        plotNotes = {}
                    plotNotes[acId] = arcNote.strip()
                    self.novel.sections[scId].plotNotes = plotNotes
                    if plotNotes[acId] and not acId in self.novel.sections[scId].scArcs:
                        scArcs = self.novel.sections[scId].scArcs
                        scArcs.append(acId)
                        self.novel.sections[scId].scArcs = scArcs
                        acSections = self.novel.arcs[acId].sections
                        acSections.append(scId)
                        self.novel.arcs[acId].sections = acSections

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
                self.novel.sections[scId].time = scTime

            #--- day
            try:
                day = self._columns['Day'][scId]
                int(day)
            except:
                pass
            else:
                self.novel.sections[scId].day = day.strip()

            #--- title
            try:
                title = self._columns['Title'][scId]
            except:
                pass
            else:
                self.novel.sections[scId].title = title.strip()

            #--- desc
            try:
                desc = self._columns['Description'][scId]
            except:
                pass
            else:
                self.novel.sections[scId].desc = desc.strip()

            #--- viewpoint
            try:
                viewpoint = self._columns['Viewpoint'][scId]
            except:
                pass
            else:
                viewpoint = viewpoint.strip()

                # Get the vp character ID.
                vpId = None
                for crId in self.novel.characters:
                    if self.novel.characters[crId].title == viewpoint:
                        vpId = crId
                        break
                if vpId is not None:
                    scCharacters = self.novel.sections[scId].characters
                    if scCharacters is None:
                        scCharacters = []

                    # Put the vp charcter ID at the first position.
                    try:
                        scCharacters.remove(vpId)
                    except:
                        pass
                    scCharacters.insert(0, vpId)
                    self.novel.sections[scId].characters = scCharacters

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
                self.novel.sections[scId].goal = goal.strip()

            #--- conflict
            try:
                conflict = self._columns['Conflict'][scId]
            except:
                pass
            else:
                self.novel.sections[scId].conflict = conflict.strip()

            #--- outcome
            try:
                outcome = self._columns['Outcome'][scId]
            except:
                pass
            else:
                self.novel.sections[scId].outcome = outcome.strip()

            #--- notes
            try:
                notes = self._columns['Notes'][scId]
            except:
                pass
            else:
                self.novel.sections[scId].notes = notes.strip()

