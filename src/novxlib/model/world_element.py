"""Provide a generic class for novelibre story world element representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element_tags import BasicElementTags
import xml.etree.ElementTree as ET


class WorldElement(BasicElementTags):
    """Story world element representation (may be location or item)."""

    def __init__(self,
            aka=None,
            **kwargs):
        """Extends the superclass constructor"""
        super().__init__(**kwargs)
        self._aka = aka

    @property
    def aka(self):
        return self._aka

    @aka.setter
    def aka(self, newVal):
        if self._aka != newVal:
            self._aka = newVal
            self.on_element_change()

    def read_xml(self, xmlElement):
        super().read_xml(xmlElement)
        self.aka = self._get_element_text(xmlElement, 'Aka')

    def write_xml(self, xmlElement):
        super().write_xml(xmlElement)
        if self.aka:
            ET.SubElement(xmlElement, 'Aka').text = self.aka

