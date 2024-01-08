"""Helper module for xml ElementTree processing.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import xml.etree.ElementTree as ET

__all__ = [
    'get_element_text',
    'text_to_xml_element',
    'xml_element_to_text',
    ]


def get_element_text(parent, tag, default=None):
    """Return the text field of an XML element.
    
    If the element doesn't exist, return default.
    """
    if parent.find(tag) is not None:
        return parent.find(tag).text
    else:
        return default


def text_to_xml_element(tag, text):
    """Return an ElementTree element named "tag" with paragraph subelements.
    
    Positional arguments:
    tag: str -- Name of the XML element to return.    
    text -- string to convert.
    """
    xmlElement = ET.Element(tag)
    for line in text.split('\n'):
        ET.SubElement(xmlElement, 'p').text = line
    return xmlElement


def xml_element_to_text(xmlElement):
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

