"""Provide a class for ODT invisibly tagged plot line/plot point descriptions import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import PLOTLINES_SUFFIX
from novxlib.novx_globals import _
from novxlib.odt.odt_reader import OdtReader


class OdtRPlotlines(OdtReader):
    """ODT plot line descriptions file reader.

    Import a document with invisibly tagged plot line/plot point descriptions.
    """
    DESCRIPTION = _('Plot lines')
    SUFFIX = PLOTLINES_SUFFIX

    def handle_data(self, data):
        """Collect data within section sections.

        Positional arguments:
            data: str -- text to be stored. 
        
        Overrides the superclass method.
        """
        if self._plId is not None:
            self._lines.append(data)
        elif self._ppId is not None:
            self._lines.append(data)

    def handle_endtag(self, tag):
        """Recognize the end of the section section and save data.
        
        Positional arguments:
            tag: str -- name of the tag converted to lower case.

        Overrides the superclass method.
        """
        if self._plId is not None:
            if tag == 'div':
                text = ''.join(self._lines)
                self.novel.plotLines[self._plId].desc = text.rstrip()
                self._lines = []
                self._plId = None
            elif tag == 'p':
                self._lines.append('\n')
        elif self._ppId is not None:
            if tag == 'div':
                text = ''.join(self._lines)
                self.novel.plotPoints[self._ppId].desc = text.rstrip()
                self._lines = []
                self._ppId = None
            elif tag == 'p':
                self._lines.append('\n')

