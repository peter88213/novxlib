"""Provide a class for parsing novx section content, converting it to shortcode.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from xml import sax


class NovxToShortcode(sax.ContentHandler):
    """A parser to convert novx markup to yw7-compatible shortcode markup."""
    NOTE_TYPES = {
        'footnote':'@fn',
        'endnote':'@en',
    }

    def __init__(self):
        super().__init__()
        self.textList = None
        self._paragraph = None
        self._span = None
        self._comment = None

    def feed(self, xmlString):
        """Feed a string file to the parser.
        
        Positional arguments:
            filePath: str -- novx document path.        
        """
        self.textList = []
        if xmlString:
            self._comment = False
            self._paragraph = False
            self._span = []
            sax.parseString(xmlString, self)

    def characters(self, content):
        """Receive notification of character data.
        
        Overrides the xml.sax.ContentHandler method             
        """
        if self._paragraph:
            self.textList.append(content)

    def endElement(self, name):
        """Signals the end of an element in non-namespace mode.
        
        Overrides the xml.sax.ContentHandler method     
        """
        if name == 'p':
            while self._span:
                self.textList.append(self._span.pop())
            if self._comment:
                self.textList.append(' ')
            else:
                self.textList.append('\n')
            self._paragraph = False
            return

        if name == 'em':
            self.textList.append('[/i]')
            return

        if name == 'strong':
            self.textList.append('[/b]')
            return

        if name == 'span':
            if self._span:
                self.textList.append(self._span.pop())
            return

        if name in ('comment', 'note'):
            self._comment = False
            self.textList.append('*/')
            return

        if name in ('creator', 'date', 'note-citation'):
            self._paragraph = True

    def startElement(self, name, attrs):
        """Signals the start of an element in non-namespace mode.
        
        Overrides the xml.sax.ContentHandler method             
        """
        xmlAttributes = {}
        for attribute in attrs.items():
            attrKey, attrValue = attribute
            xmlAttributes[attrKey] = attrValue
        locale = xmlAttributes.get('xml:lang', None)

        if name == 'p':
            self._paragraph = True
            if xmlAttributes.get('style', None) == 'quotations':
                self.textList.append('> ')
            return

        if name == 'em':
            self.textList.append('[i]')
            return

        if name == 'strong':
            self.textList.append('[b]')
            return

        if name == 'span':
            if locale is None:
                return

            self._span.append(f'[/lang={locale}]')
            self.textList.append(f'[lang={locale}]')
            return

        if name in ('comment', 'note'):
            self._comment = True
            self.textList.append('/*')

            if name == 'note':
                noteClass = xmlAttributes.get('class', 'footnote')
                self.textList.append(f"{self.NOTE_TYPES.get(noteClass, '@fn')} ")
            return

        if name in ('creator', 'date', 'note-citation'):
            self._paragraph = False

