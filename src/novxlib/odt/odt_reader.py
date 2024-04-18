"""Provide an abstract ODT file reader class.

Other ODT file readers inherit from this class.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from abc import ABC

from novxlib.novx_globals import CHAPTER_PREFIX
from novxlib.novx_globals import Error
from novxlib.novx_globals import PLOT_LINE_PREFIX
from novxlib.novx_globals import PLOT_POINT_PREFIX
from novxlib.novx_globals import SECTION_PREFIX
from novxlib.novx_globals import _
from novxlib.novx_globals import norm_path
from novxlib.odf.odf_reader import OdfReader
from novxlib.odt.odt_parser import OdtParser


class OdtReader(OdfReader, ABC):
    """Abstract ODT file reader class.
    
      HTMLParser-like API used by the XML parser:
        handle comment(data) -- Process inline comments within section content.
        handle_data -- Stub for a data handler to be implemented in a subclass.
        handle_endtag -- Stub for an end tag handler to be implemented in a subclass.
        handle_starttag(tag, attrs) -- Identify sections and chapters.
    """
    EXTENSION = '.odt'

    def __init__(self, filePath, **kwargs):
        """Initialize the ODT parser and local instance variables for parsing.
        
        Positional arguments:
            filePath: str -- path to the file represented by the File instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            

        The ODT parser works like a state machine. 
        Section ID, chapter ID and processed lines must be saved between the transitions.         
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._lines = []
        self._scId = None
        self._chId = None
        self._plId = None
        self._ppId = None
        self._skip_data = False

    def handle_data(self, data):
        """Stub for a data handler to be implemented in a subclass.

        Positional arguments:
            data: str -- text to be stored. 
        """
        pass

    def handle_endtag(self, tag):
        """Stub for an end tag handler to be implemented in a subclass.
        
        Positional arguments:
            tag: str -- name of the tag converted to lower case.
        """
        pass

    def handle_starttag(self, tag, attrs):
        """Identify sections and chapters.
        
        Positional arguments:
            tag: str -- name of the tag.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        This method is applicable to ODT files that are divided into chapters and/or sections. 
        For differently structured ODT files  do override this method in a subclass.
        """
        if tag == 'div':
            if attrs[0][0] == 'id':
                if attrs[0][1].startswith(SECTION_PREFIX):
                    self._scId = attrs[0][1]
                elif attrs[0][1].startswith(CHAPTER_PREFIX):
                    self._chId = attrs[0][1]
                elif attrs[0][1].startswith(PLOT_LINE_PREFIX):
                    self._plId = attrs[0][1]
                elif attrs[0][1].startswith(PLOT_POINT_PREFIX):
                    self._ppId = attrs[0][1]
        elif tag == 's':
            self._lines.append(' ')

    def read(self):
        parser = OdtParser(self)
        try:
            parser.feed_file(self.filePath)
        except:
            raise Error(f'{_("Cannot parse File")}: {norm_path(self.filePath)}')

