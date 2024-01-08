"""Provide an XML item data file reader class.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx.novx_file import NovxFile
from novxlib.novx_globals import _
import xml.etree.ElementTree as ET


class ItemDataReader(NovxFile):
    """XML item data file reader."""
    DESCRIPTION = _('XML item data file')
    EXTENSION = '.xml'

    def read(self):
        """Parse the xml files and get the instance variables.
        
        Overrides the superclass method.
        """
        tree = ET.parse(self.filePath)
        root = ET.Element('ROOT')
        root.append(tree.getroot())
        self._read_items(root)

