"""Provide a class for novelibre plot point representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element_notes import BasicElementNotes
import xml.etree.ElementTree as ET


class PlotPoint(BasicElementNotes):
    """Plot point representation."""

    def __init__(self,
            sectionAssoc=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)

        self._sectionAssoc = sectionAssoc
        # str -- ID of the associated section

    @property
    def sectionAssoc(self):
        return self._sectionAssoc

    @sectionAssoc.setter
    def sectionAssoc(self, newVal):
        if self._sectionAssoc != newVal:
            self._sectionAssoc = newVal
            self.on_element_change()

    def read_xml(self, xmlElement):
        super().read_xml(xmlElement)
        xmlSectionAssoc = xmlElement.find('Section')
        if xmlSectionAssoc is not None:
            self.sectionAssoc = xmlSectionAssoc.get('id', None)

    def write_xml(self, xmlElement):
        super().write_xml(xmlElement)
        if self.sectionAssoc:
            ET.SubElement(xmlElement, 'Section', attrib={'id': self.sectionAssoc})
