"""Provide a class for noveltree XML data files.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import os

from novxlib.novx.novx_file import NovxFile
from novxlib.novx_globals import DATA_SUFFIX
from novxlib.novx_globals import Error
from novxlib.novx_globals import _
from novxlib.novx_globals import norm_path
import xml.etree.ElementTree as ET


class DataWriter(NovxFile):
    """noveltree XML data files representation.
       
    noveltree can import or export characters, locations and items as separate
    xml files. This class represents a set of three xml files generated from
    a noveltree project.
    """
    DESCRIPTION = _('noveltree XML data files')
    EXTENSION = '.xml'
    SUFFIX = DATA_SUFFIX

    XML_HEADER = '''<?xml version="1.0" encoding="utf-8"?>
'''

    def _postprocess_xml_file(self, filePath):
        '''Postprocess three xml files created by ElementTree.
        
        Positional argument:
            filePath: str -- path to .novx xml file.
            
        Generate the xml file paths from the .novx path. 
        Read, postprocess and write the characters, locations, and items xml files.        
        Extends the superclass method.
        '''
        path, __ = os.path.splitext(filePath)
        characterPath = f'{path}_Characters.xml'
        super()._postprocess_xml_file(characterPath)
        locationPath = f'{path}_Locations.xml'
        super()._postprocess_xml_file(locationPath)
        itemPath = f'{path}_Items.xml'
        super()._postprocess_xml_file(itemPath)

    def _write_element_tree(self, xmlProject):
        """Save the characters/locations/items subtrees as separate xml files
        
        Positional argument:
            xmlProject -- NovxFile instance.
            
        Extract the characters/locations/items xml subtrees from a noveltree project.
        Generate the xml file paths from the .novx path and write each subtree to an xml file.
        Raise the "Error" exception in case of error. 
        """
        path, __ = os.path.splitext(xmlProject.filePath)
        characterPath = f'{path}_Characters.xml'
        characterSubtree = xmlProject.xmlTree.find('CHARACTERS')
        characterTree = ET.ElementTree(characterSubtree)
        try:
            characterTree.write(characterPath, xml_declaration=False, encoding='utf-8')
        except(PermissionError):
            raise Error(f'{_("File is write protected")}: "{norm_path(characterPath)}".')

        locationPath = f'{path}_Locations.xml'
        locationSubtree = xmlProject.xmlTree.find('LOCATIONS')
        locationTree = ET.ElementTree(locationSubtree)
        try:
            locationTree.write(locationPath, xml_declaration=False, encoding='utf-8')
        except(PermissionError):
            raise Error(f'{_("File is write protected")}: "{norm_path(locationPath)}".')

        itemPath = f'{path}_Items.xml'
        itemSubtree = xmlProject.xmlTree.find('ITEMS')
        itemTree = ET.ElementTree(itemSubtree)
        try:
            itemTree.write(itemPath, xml_declaration=False, encoding='utf-8')
        except(PermissionError):
            raise Error(f'{_("File is write protected")}: "{norm_path(itemPath)}".')

