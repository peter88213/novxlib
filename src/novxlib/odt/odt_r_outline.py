"""Provide a class for ODT outline import.

Conventions:
An outline has at least one third level heading.

-   Heading 1 -- New chapter title (beginning a new section).
-   Heading 2 -- New chapter title.
-   Heading 3 -- New section title.
-   All other text is considered to be chapter/section description.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from xml.sax.saxutils import unescape
import re

from novxlib.model.chapter import Chapter
from novxlib.model.section import Section
from novxlib.novx_globals import CHAPTER_PREFIX
from novxlib.novx_globals import CH_ROOT
from novxlib.novx_globals import SECTION_PREFIX
from novxlib.novx_globals import _
from novxlib.odt.odt_reader import OdtReader


class OdtROutline(OdtReader):
    """ODT outline file reader.

    Import an outline without chapter and section tags.
    """
    DESCRIPTION = _('Novel outline')
    SUFFIX = ''

    def __init__(self, filePath, **kwargs):
        """Initialize local instance variables for parsing.

        Positional arguments:
            filePath: str -- path to the file represented by the Novel instance.
            
        The ODT parser works like a state machine. 
        Chapter and section count must be saved between the transitions.         
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self._chCount = 0
        self._scCount = 0

    def handle_data(self, data):
        """Collect data within section sections.

        Positional arguments:
            data: str -- text to be stored. 
        
        Overrides the superclass method.
        """
        self._lines.append(data)

    def handle_endtag(self, tag):
        """Recognize the paragraph's end.
        
        Positional arguments:
            tag: str -- name of the tag converted to lower case.

        Overrides the superclass method.
        """
        text = ''.join(self._lines)
        if tag == 'p':
            self._lines = [f'{text.strip()}\n']
            if self._scId is not None:
                self.novel.sections[self._scId].desc = text
                return

            if self._chId is not None:
                self.novel.chapters[self._chId].desc = text
            return

        if tag in ('h1', 'h2'):
            self.novel.chapters[self._chId].title = unescape(re.sub('<.*?>', '', text).strip())
            self._lines = []
            return

        if tag == 'h3':
            self.novel.sections[self._scId].title = unescape(re.sub('<.*?>', '', text).strip())
            self._lines = []
            return

        if tag == 'title':
            self.novel.title = text.strip()

    def handle_starttag(self, tag, attrs):
        """Recognize the paragraph's beginning.
        
        Positional arguments:
            tag: str -- name of the tag converted to lower case.
            attrs -- list of (name, value) pairs containing the attributes found inside the tag’s <> brackets.
        
        Overrides the superclass method.
        """
        if tag in ('h1', 'h2'):
            self._scId = None
            self._lines = []
            self._chCount += 1
            self._chId = f'{CHAPTER_PREFIX}{self._chCount}'
            self.novel.chapters[self._chId] = Chapter(chType=0)
            self.novel.tree.append(CH_ROOT, self._chId)
            if tag == 'h1':
                self.novel.chapters[self._chId].chLevel = 1
            else:
                self.novel.chapters[self._chId].chLevel = 2
            return

        if tag == 'h3':
            self._lines = []
            self._scCount += 1
            self._scId = f'{SECTION_PREFIX}{self._scCount}'
            self.novel.sections[self._scId] = Section(
                scType=0,
                scene=0,
                status=1,
            )
            self.novel.tree.append(self._chId, self._scId)
            self.novel.sections[self._scId].sectionContent = ''
            return

        if tag == 'div':
            self._scId = None
            self._chId = None
            return

        if tag == 'meta':
            if attrs[0][1] == 'author':
                self.novel.authorName = attrs[1][1]
                return

            if attrs[0][1] == 'description':
                self.novel.desc = attrs[1][1]
            return

        if tag == 'title':
            self._lines = []
            return

        if tag == 'body':
            for attr in attrs:
                if attr[0] == 'language':
                    if attr[1]:
                        self.novel.languageCode = attr[1]
                if attr[0] == 'country':
                    if attr[1]:
                        self.novel.countryCode = attr[1]
            return

        if tag == 's':
            self._lines.append(' ')
