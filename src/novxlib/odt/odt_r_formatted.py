"""Provide a base class for ODT documents containing text that is formatted in novelibre.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.splitter import Splitter
from novxlib.odt.odt_reader import OdtReader


class OdtRFormatted(OdtReader):
    """ODT file reader.
    
    Provide methods and data for processing chapters with formatted text.
    """

    def read(self):
        """Parse the file and get the instance variables.
        
        Extends the superclass method.
        """
        self.novel.languages = []
        super().read()

        # Split sections, if necessary.
        sectionSplitter = Splitter()
        self.sectionsSplit = sectionSplitter.split_sections(self.novel)

