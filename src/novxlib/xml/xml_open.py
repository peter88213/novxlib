"""Provide a helper module for xml file operation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import Error
from novxlib.novx_globals import _
from novxlib.novx_globals import norm_path
import xml.etree.ElementTree as ET


def get_xml_root(filePath):
    try:
        xmlTree = ET.parse(filePath)
    except Exception as ex:
        raise Error(f'{_("Cannot process file")}: "{norm_path(filePath)}" - {str(ex)}')

    return xmlTree.getroot()
