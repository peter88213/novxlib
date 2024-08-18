"""Provide a helper module for xml file operation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import Error
from novxlib.novx_globals import norm_path
from novxlib.xml.xml_filter import strip_illegal_characters
import xml.etree.ElementTree as ET


def get_xml_root(filePath):
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            xmlText = f.read()
    except Exception as ex:
        raise Error(f'{_("Cannot read file")}: "{norm_path(filePath)}" - {str(ex)}')

    try:
        xmlText = strip_illegal_characters(xmlText)
        return ET.fromstring(xmlText)

    except Exception as ex:
        raise Error(f'{_("Cannot process file")}: "{norm_path(filePath)}" - {str(ex)}')
