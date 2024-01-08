"""Provide a class for parsing novx section content, converting it to ODT.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from xml import sax


class NovxToOdt(sax.ContentHandler):
    """A parser to convert novx markup to odt markup."""

    def __init__(self):
        super().__init__()
        self.odtLines = None
        self._languages = None
        self._indentParagraph = None
        self._note = None
        self._comment = None

    def feed(self, xmlString, languages, append):
        """Feed a string file to the parser.
        
        Positional arguments:
            xmlString: str -- content as XML string.
            languages: list[str] -- Ordered list of the document#s languages.
            append: boolean -- indent the first paragraph, if True.
            
        """
        self._languages = languages
        self._indentParagraph = append
        self._note = None
        self._comment = False
        self.odtLines = []
        if xmlString:
            sax.parseString(f'<content>{xmlString}</content>', self)

    def characters(self, content):
        """Receive notification of character data.
        
        Overrides the xml.sax.ContentHandler method             
        """
        content = sax.saxutils.escape(content)
        self.odtLines.append(content)
        self._indentParagraph = True

    def endElement(self, name):
        """Signals the end of an element in non-namespace mode.
        
        Overrides the xml.sax.ContentHandler method     
        """
        if name == 'p':
            self.odtLines.append('</text:p>')
        elif name in ('em', 'strong', 'span'):
            self.odtLines.append('</text:span>')
        elif name == 'li':
            self.odtLines.append('</text:list-item>')
        elif name == 'creator':
            self.odtLines.append('</dc:creator>')
        elif name == 'date':
            self.odtLines.append('</dc:date>')
        elif name == 'note-citation':
            self.odtLines.append('</text:note-citation><text:note-body>')
        elif name == 'ul':
            self._list = False
            self._indentParagraph = False
            self.odtLines.append('</text:list>')
        elif name == 'comment':
            self.odtLines.append('</office:annotation>')
            self._comment = False
        elif name == 'note':
            self._note = None
            self.odtLines.append('</text:note-body></text:note>')

    def startElement(self, name, attrs):
        """Signals the start of an element in non-namespace mode.
        
        Overrides the xml.sax.ContentHandler method             
        """
        xmlAttributes = {}
        for attribute in attrs.items():
            attrKey, attrValue = attribute
            xmlAttributes[attrKey] = attrValue
        if name == 'p':
            if xmlAttributes.get('style', None) == 'quotations':
                self.odtLines.append('<text:p text:style-name="Quotations">')
            elif self._note:
                self.odtLines.append(f'<text:p text:style-name="{self._note.title()}">')
            elif self._comment:
                self.odtLines.append('<text:p>')
            elif self._indentParagraph:
                self.odtLines.append('<text:p text:style-name="First_20_line_20_indent">')
            else:
                self.odtLines.append('<text:p text:style-name="Text_20_body">')
            self._indentParagraph = False
        elif name == 'em':
            self.odtLines.append('<text:span text:style-name="Emphasis">')
        elif name == 'strong':
            self.odtLines.append('<text:span text:style-name="Strong_20_Emphasis">')
        elif name == 'span':
            language = xmlAttributes.get('xml:lang', None)
            if language:
                i = self._languages.index(language) + 1
                self.odtLines.append(f'<text:span text:style-name="T{i}">')
        elif name == 'ul':
            self._list = True
            self.odtLines.append('<text:list>')
        elif name == 'comment':
            self._comment = True
            self.odtLines.append('<office:annotation>')
        elif name == 'note':
            self._note = xmlAttributes.get('class', 'footnote')
            self.odtLines.append(f'<text:note text:note-class="{self._note}">')
        elif name == 'creator':
            self.odtLines.append('<dc:creator>')
        elif name == 'date':
            self.odtLines.append('<dc:date>')
        elif name == 'note-citation':
            self.odtLines.append('<text:note-citation>')
        elif name == 'li':
            self.odtLines.append('<text:list-item>')
