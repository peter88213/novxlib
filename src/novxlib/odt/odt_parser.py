"""Provide a class for parsing ODT documents.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from xml import sax
import zipfile

from novxlib.novx_globals import Error
from novxlib.novx_globals import _
from novxlib.novx_globals import norm_path
import xml.etree.ElementTree as ET


class OdtParser(sax.ContentHandler):
    """An ODT document parser, using the html.parser.HTMLParser API."""

    def __init__(self, client):
        super().__init__()

        self._emTags = ['Emphasis']
        # Collection of "emphasis" styles used in the ODT document.

        self._strongTags = ['Strong_20_Emphasis']
        # Collection of "strong emphasis" styles used in the ODT document.

        self._blockquoteTags = ['Quotations']
        # Collection of "blockquote" paragraph styles used in the ODT document.

        self._languageTags = {}
        # Collection of language tags used in the ODT document.

        self._headingTags = {}
        # Collection of heading style names used in the ODT document.

        self._heading = None
        # Transformed heading element.

        self._getData = False
        # If True, handle the characters.

        self._span = []
        # Stack of novx elements created from ODT spans.
        # Each entry is a list of novx element names created from one ODT span.
        # For skipped spans, the list entry is None.

        self._paraSpan = []
        # Stack of additionsl spans created from ODT paragraph attributes.
        # Each list entry is the novx element name of the additional span.
        # If no additional span was created, the list entry is None.

        self._style = None
        # ODT style being processed.

        self._client = client

    def feed_file(self, filePath):
        """Feed an ODT file to the parser.
        
        Positional arguments:
            filePath: str -- ODT document path.
        
        First unzip the ODT file located at self.filePath, 
        and get languageCode, countryCode, title, desc, and authorName,        
        Then call the sax parser for content.xml.
        """
        namespaces = dict(
            office='urn:oasis:names:tc:opendocument:xmlns:office:1.0',
            style='urn:oasis:names:tc:opendocument:xmlns:style:1.0',
            fo='urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
            dc='http://purl.org/dc/elements/1.1/',
            meta='urn:oasis:names:tc:opendocument:xmlns:meta:1.0'
            )

        try:
            with zipfile.ZipFile(filePath, 'r') as odfFile:
                content = odfFile.read('content.xml')
                styles = odfFile.read('styles.xml')
                try:
                    meta = odfFile.read('meta.xml')
                except KeyError:
                    # meta.xml may be missing in outlines created with e.g. FreeMind
                    meta = None
        except:
            raise Error(f'{_("Cannot read file")}: "{norm_path(filePath)}".')

        #--- Get language and country from 'styles.xml'.
        root = ET.fromstring(styles)
        styles = root.find('office:styles', namespaces)
        for defaultStyle in styles.iterfind('style:default-style', namespaces):
            if defaultStyle.get(f'{{{namespaces["style"]}}}family') == 'paragraph':
                textProperties = defaultStyle.find('style:text-properties', namespaces)
                lngCode = textProperties.get(f'{{{namespaces["fo"]}}}language')
                ctrCode = textProperties.get(f'{{{namespaces["fo"]}}}country')
                self._client.handle_starttag('body', [('language', lngCode), ('country', ctrCode)])
                break

        #--- Get title, description, and author from 'meta.xml'.
        if meta:
            root = ET.fromstring(meta)
            meta = root.find('office:meta', namespaces)
            title = meta.find('dc:title', namespaces)
            if title is not None:
                if title.text:
                    self._client.handle_starttag('title', [()])
                    self._client.handle_data(title.text)
                    self._client.handle_endtag('title')
            author = meta.find('meta:initial-creator', namespaces)
            if author is not None:
                if author.text:
                    self._client.handle_starttag('meta', [('', 'author'), ('', author.text)])
            desc = meta.find('dc:description', namespaces)
            if desc is not None:
                if desc.text:
                    self._client.handle_starttag('meta', [('', 'description'), ('', desc.text)])

        #--- Parse 'content.xml'.
        sax.parseString(content, self)

    def characters(self, content):
        """Receive notification of character data.
        
        Overrides the xml.sax.ContentHandler method             
        """
        if self._getData:
            self._client.handle_data(sax.saxutils.escape(content))

    def endElement(self, name):
        """Signals the end of an element in non-namespace mode.
        
        Overrides the xml.sax.ContentHandler method     
        """
        if name in ('text:p', 'text:h'):
            try:
                span = self._paraSpan.pop()
                if span is not None:
                    self._client.handle_endtag(span)
            except:
                pass
            self._getData = False
            if self._heading:
                self._client.handle_endtag(self._heading)
                self._heading = None
            else:
                self._client.handle_endtag('p')
        elif name == 'text:span':
            try:
                spans = self._span.pop()
                for span in reversed(spans):
                    if span is not None:
                        self._client.handle_endtag(span)
            except:
                pass
        elif name == 'text:section':
            self._client.handle_endtag('div')
        elif name == 'office:annotation':
            self._client.handle_endtag('comment')
            self._getData = True
        elif name == 'dc:creator':
            self._client.handle_endtag('creator')
            self._getData = False
        elif name == 'dc:date':
            self._client.handle_endtag('date')
            self._getData = False
        elif name == 'text:note':
            self._client.handle_endtag('note')
            self._getData = True
        elif name == 'text:note-citation':
            self._client.handle_endtag('note-citation')
            self._getData = False
        elif name == 'text:h':
            self._client.handle_endtag(self._heading)
            self._heading = None
        elif name == 'text:list-item':
            self._client.handle_endtag('li')
        elif name == 'text:list':
            self._client.handle_endtag('ul')
        elif name == 'style:style':
            self._style = None

    def startElement(self, name, attrs):
        """Signals the start of an element in non-namespace mode.
        
        Overrides the xml.sax.ContentHandler method             
        """
        xmlAttributes = {}
        for attribute in attrs.items():
            attrKey, attrValue = attribute
            xmlAttributes[attrKey] = attrValue
        style = xmlAttributes.get('text:style-name', '')
        if name in ('text:p', 'text:h'):
            self._getData = True
            param = []
            if style in self._languageTags:
                param.append(('lang', self._languageTags[style]))
            if style in self._blockquoteTags:
                param.append(('style', 'quotations'))
                self._client.handle_starttag('p', param)
            elif style.startswith('Heading'):
                self._heading = f'h{style[-1]}'
                self._client.handle_starttag(self._heading, [()])
            elif style in self._headingTags:
                self._heading = self._headingTags[style]
                self._client.handle_starttag(self._heading, [()])
            else:
                if not param:
                    param = [()]
                self._client.handle_starttag('p', param)
            if style in self._strongTags:
                # Priority for "strong emphasis"
                self._paraSpan.append('strong')
                self._client.handle_starttag('strong', [()])
            elif style in self._emTags:
                self._paraSpan.append('em')
                self._client.handle_starttag('em', [()])
            else:
                self._paraSpan.append(None)
        elif name == 'text:span':
            spans = []
            if style in self._emTags:
                spans.append('em')
                self._client.handle_starttag('em', [()])
            elif style in self._strongTags:
                spans.append('strong')
                self._client.handle_starttag('strong', [()])
            if style in self._languageTags:
                spans.append('lang')
                self._client.handle_starttag('lang', [
                    ('lang', self._languageTags[style])
                    ])
            if not spans:
                spans.append(None)
            self._span.append(spans)
        elif name == 'text:section':
            self._client.handle_starttag('div', [
                ('id', xmlAttributes['text:name'])
                ])
        elif name == 'office:annotation':
            self._client.handle_starttag('comment', [()])
            self._getData = False
        elif name == 'dc:date':
            self._client.handle_starttag('date', [()])
            self._getData = True
        elif name == 'dc:creator':
            self._client.handle_starttag('creator', [()])
            self._getData = True
        elif name == 'text:note':
            self._client.handle_starttag('note', [
                ('id', xmlAttributes.get('text:id', '')),
                ('class', xmlAttributes.get('text:note-class', ''))
                ])
            self._getData = False
        elif name == 'text:note-citation':
            self._client.handle_starttag('note-citation', [()])
            self._getData = True
        elif name == 'text:h':
            try:
                self._heading = f'h{xmlAttributes["text:outline-level"]}'
            except:
                self._heading = f'h{style[-1]}'
            self._client.handle_starttag(self._heading, [()])
        elif name == 'text:list-item':
            self._client.handle_starttag('li', [()])
        elif name == 'text:list':
            self._client.handle_starttag('ul', [()])
        elif name == 'style:style':
            self._style = xmlAttributes.get('style:name', None)
            styleName = xmlAttributes.get('style:parent-style-name', '')
            if styleName.startswith('Heading'):
                self._headingTags[self._style] = f'h{styleName[-1]}'
            elif styleName == 'Quotations':
                self._blockquoteTags.append(self._style)
        elif name == 'style:text-properties':
            if xmlAttributes.get('fo:font-style', None) == 'italic':
                self._emTags.append(self._style)
            if xmlAttributes.get('fo:font-weight', None) == 'bold':
                self._strongTags.append(self._style)
            if xmlAttributes.get('fo:language', False):
                lngCode = xmlAttributes['fo:language']
                ctrCode = xmlAttributes['fo:country']
                if ctrCode != 'none':
                    locale = f'{lngCode}-{ctrCode}'
                else:
                    locale = lngCode
                self._languageTags[self._style] = locale
        elif name == 'text:s':
            self._client.handle_starttag('s', [()])

