"""Provide a class for a novelibre element with notes and tags.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element_notes import BasicElementNotes
from novxlib.novx_globals import list_to_string
from novxlib.novx_globals import string_to_list
import xml.etree.ElementTree as ET


class BasicElementTags(BasicElementNotes):
    """Basic element with notes and tags."""

    def __init__(self,
            tags=None,
            **kwargs):
        """Extends the superclass constructor"""
        super().__init__(**kwargs)
        self._tags = tags

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, newVal):
        # str: semicolon-separated tags
        if self._tags != newVal:
            self._tags = newVal
            self.on_element_change()

    def read_xml(self, xmlElement):
        super().read_xml(xmlElement)
        tags = string_to_list(self._get_element_text(xmlElement, 'Tags'))
        strippedTags = []
        for tag in tags:
            strippedTags.append(tag.strip())
        self.tags = strippedTags

    def write_xml(self, xmlElement):
        super().write_xml(xmlElement)
        tagStr = list_to_string(self.tags)
        if tagStr:
            ET.SubElement(xmlElement, 'Tags').text = tagStr

