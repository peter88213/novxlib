"""Provide a class for novelibre chapter representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element_notes import BasicElementNotes


class Chapter(BasicElementNotes):
    """novelibre chapter representation."""

    def __init__(self,
            chLevel=None,
            chType=None,
            noNumber=None,
            isTrash=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)
        self._chLevel = chLevel
        # 1 = part level
        # 2 = regular chapter level
        self._chType = chType
        # 0 = Normal
        # 1 = Unused
        self._noNumber = noNumber
        # True: Auto-number this chapter
        # False: Do not auto-number this chapter
        self._isTrash = isTrash
        # True: This chapter is the novelibre project's "trash bin"
        # False: This chapter is not a "trash bin"

    @property
    def chLevel(self):
        return self._chLevel

    @chLevel.setter
    def chLevel(self, newVal):
        if self._chLevel != newVal:
            self._chLevel = newVal
            self.on_element_change()

    @property
    def chType(self):
        return self._chType

    @chType.setter
    def chType(self, newVal):
        if self._chType != newVal:
            self._chType = newVal
            self.on_element_change()

    @property
    def noNumber(self):
        return self._noNumber

    @noNumber.setter
    def noNumber(self, newVal):
        if self._noNumber != newVal:
            self._noNumber = newVal
            self.on_element_change()

    @property
    def isTrash(self):
        return self._isTrash

    @isTrash.setter
    def isTrash(self, newVal):
        if self._isTrash != newVal:
            self._isTrash = newVal
            self.on_element_change()

    def from_xml(self, xmlElement):
        super().from_xml(xmlElement)
        typeStr = xmlElement.get('type', '0')
        if typeStr in ('0', '1'):
            self.chType = int(typeStr)
        else:
            self.chType = 1
        chLevel = xmlElement.get('level', None)
        if chLevel == '1':
            self.chLevel = 1
        else:
            self.chLevel = 2
        self.isTrash = xmlElement.get('isTrash', None) == '1'
        self.noNumber = xmlElement.get('noNumber', None) == '1'

    def to_xml(self, xmlElement):
        super().to_xml(xmlElement)
        if self.chType:
            xmlElement.set('type', str(self.chType))
        if self.chLevel == 1:
            xmlElement.set('level', '1')
        if self.isTrash:
            xmlElement.set('isTrash', '1')
        if self.noNumber:
            xmlElement.set('noNumber', '1')
