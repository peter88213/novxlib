"""Helper module for removing novxlib specific data.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import re

__all__ = ['reset_custom_variables']


def reset_custom_variables(prjFile):
    """Set custom keyword variables of a File instance to an empty string.
    
    Positional arguments:
        prjFile -- File instance to process.
    
    Thus the Yw7File.write() method will remove the associated custom fields
    from the .yw7 XML file. 
    Return True, if a keyword variable has changed (i.e information is lost).
    """
    hasChanged = False
    for field in prjFile.PRJ_KWVAR_YW7:
        if prjFile.novel.kwVar.get(field, None):
            prjFile.novel.kwVar[field] = ''
            hasChanged = True
    for chId in prjFile.novel.chapters:
        # Deliberatey not iterate srtChapters: make sure to get all chapters.
        for field in prjFile.CHP_KWVAR_YW7:
            if prjFile.novel.chapters[chId].kwVar.get(field, None):
                prjFile.novel.chapters[chId].kwVar[field] = ''
                hasChanged = True
    for scId in prjFile.novel.sections:
        for field in prjFile.SCN_KWVAR_YW7:
            if prjFile.novel.sections[scId].kwVar.get(field, None):
                prjFile.novel.sections[scId].kwVar[field] = ''
                hasChanged = True
    return hasChanged


def remove_language_tags(novel):
    """Remove language tags from the document.
    
    Positional arguments:
        novel -- Novel instance to process.    
    
    Remove the language tags from the section contents.
    Return True, if changes have been made to novel.
    """
    languageTag = re.compile('\[\/*?lang=.*?\]')
    hasChanged = False
    for scId in novel.sections:
        text = novel.sections[scId].sectionContent
        try:
            text = languageTag.sub('', text)
        except:
            pass
        else:
            if  novel.sections[scId].sectionContent != text:
                novel.sections[scId].sectionContent = text
                hasChanged = True
    return hasChanged

