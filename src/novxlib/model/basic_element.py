"""Provide a base class for novelibre element representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import xml.etree.ElementTree as ET


class BasicElement:
    """Basic data model element representation.

    Public instance variables:
        on_element_change -- Points to a callback routine for element changes
        
    The on_element_change method is called when the value of any property changes.
    This method can be overridden at runtime for each individual element instance.
    """

    def __init__(self,
            on_element_change=None,
            title=None,
            desc=None,
            links=None):
        """Set the initial values.

        If on_element_change is None, the do_nothing method will be assigned to it.
            
        General note:
        When merging files, only new elements that are not None will override 
        existing elements. This allows you to easily update a novelibre project 
        from a document that contains only a subset of the data model.
        Keep this in mind when setting the initial values.
        """
        if on_element_change is None:
            self.on_element_change = self.do_nothing
        else:
            self.on_element_change = on_element_change
        self._title = title
        self._desc = desc
        self._links = links

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, newVal):
        if self._title != newVal:
            self._title = newVal
            self.on_element_change()

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, newVal):
        if self._desc != newVal:
            self._desc = newVal
            self.on_element_change()

    @property
    def links(self):
        # dict: (Key:str -- relative path, value:str -- full path)
        try:
            return self._links.copy()
        except AttributeError:
            return None

    @links.setter
    def links(self, newVal):
        if self._links != newVal:
            self._links = newVal
            self.on_element_change()

    def do_nothing(self):
        """Standard callback routine for element changes."""
        pass

    def read_xml(self, xmlElement):
        self.title = self._get_element_text(xmlElement, 'Title')
        self.desc = self._xml_element_to_text(xmlElement.find('Desc'))
        self.links = self._get_link_dict(xmlElement)

    def write_xml(self, xmlElement):
        if self.title:
            ET.SubElement(xmlElement, 'Title').text = self.title
        if self.desc:
            xmlElement.append(self._text_to_xml_element('Desc', self.desc))
        if self.links:
            for path in self.links:
                xmlLink = ET.SubElement(xmlElement, 'Link')
                xmlLink.set('path', path)
                if self.links[path]:
                    xmlLink.set('fullPath', self.links[path])

    def _get_element_text(self, parent, tag, default=None):
        """Return the text field of an XML element.
        
        If the element doesn't exist, return default.
        """
        if parent.find(tag) is not None:
            return parent.find(tag).text
        else:
            return default

    def _text_to_xml_element(self, tag, text):
        """Return an ElementTree element named "tag" with paragraph subelements.
        
        Positional arguments:
        tag: str -- Name of the XML element to return.    
        text -- string to convert.
        """
        xmlElement = ET.Element(tag)
        for line in text.split('\n'):
            ET.SubElement(xmlElement, 'p').text = line
        return xmlElement

    def _xml_element_to_text(self, xmlElement):
        """Return plain text, converted from ElementTree paragraph subelements.
        
        Positional arguments:
            xmlElement -- ElementTree element.        
        
        Each <p> subelement of xmlElement creates a line. Formatting is discarded.
        """
        lines = []
        if xmlElement:
            for paragraph in xmlElement.iterfind('p'):
                lines.append(''.join(t for t in paragraph.itertext()))
        return '\n'.join(lines)

