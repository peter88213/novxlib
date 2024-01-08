"""Provide a class for yWriter 7 file import and export.

yWriter file importers and exporters inherit from this class.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from datetime import datetime
from html import unescape
import os
import re

from novxlib.file.file import File
from novxlib.model.arc import Arc
from novxlib.model.basic_element import BasicElement
from novxlib.model.chapter import Chapter
from novxlib.model.character import Character
from novxlib.model.id_generator import create_id
from novxlib.model.section import Section
from novxlib.model.turning_point import TurningPoint
from novxlib.model.world_element import WorldElement
from novxlib.novx_globals import AC_ROOT
from novxlib.novx_globals import ARC_POINT_PREFIX
from novxlib.novx_globals import ARC_PREFIX
from novxlib.novx_globals import CHAPTER_PREFIX
from novxlib.novx_globals import CHARACTER_PREFIX
from novxlib.novx_globals import CH_ROOT
from novxlib.novx_globals import CR_ROOT
from novxlib.novx_globals import Error
from novxlib.novx_globals import ITEM_PREFIX
from novxlib.novx_globals import IT_ROOT
from novxlib.novx_globals import LC_ROOT
from novxlib.novx_globals import LOCATION_PREFIX
from novxlib.novx_globals import PN_ROOT
from novxlib.novx_globals import PRJ_NOTE_PREFIX
from novxlib.novx_globals import SECTION_PREFIX
from novxlib.novx_globals import _
from novxlib.novx_globals import list_to_string
from novxlib.novx_globals import norm_path
from novxlib.novx_globals import string_to_list
from novxlib.xml.xml_indent import indent
from novxlib.yw.novx_to_yw7 import NovxToYw7
import xml.etree.ElementTree as ET


class Yw7File(File):
    """yWriter 7 project file representation."""
    DESCRIPTION = _('yWriter 7 project')
    EXTENSION = '.yw7'

    PRJ_KWVAR_YW7 = [
        'Field_WorkPhase',
        'Field_RenumberChapters',
        'Field_RenumberParts',
        'Field_RenumberWithinParts',
        'Field_RomanChapterNumbers',
        'Field_RomanPartNumbers',
        'Field_ChapterHeadingPrefix',
        'Field_ChapterHeadingSuffix',
        'Field_PartHeadingPrefix',
        'Field_PartHeadingSuffix',
        'Field_CustomGoal',
        'Field_CustomConflict',
        'Field_CustomOutcome',
        'Field_CustomChrBio',
        'Field_CustomChrGoals',
        'Field_SaveWordCount',
        'Field_LanguageCode',
        'Field_CountryCode',
        ]
    # list of the names of the project keyword variables

    CHP_KWVAR_YW7 = [
        'Field_NoNumber',
        'Field_ArcDefinition',
        'Field_Arc_Definition',
        ]
    # list of the names of the chapter keyword variables

    SCN_KWVAR_YW7 = [
        'Field_SceneArcs',
        'Field_SceneAssoc',
        'Field_CustomAR',
        'Field_SceneMode',
        ]
    # list of the names of the scene keyword variables

    CRT_KWVAR_YW7 = [
        'Field_Link',
        'Field_BirthDate',
        'Field_DeathDate',
        ]
    # list of the names of the character keyword variables

    LOC_KWVAR_YW7 = [
        'Field_Link',
        ]
    # list of the names of the location keyword variables

    ITM_KWVAR_YW7 = [
        'Field_Link',
        ]
    # list of the names of the item keyword variables

    _CDATA_TAGS = [
        'Title',
        'AuthorName',
        'Bio',
        'Desc',
        'FieldTitle1',
        'FieldTitle2',
        'FieldTitle3',
        'FieldTitle4',
        'LaTeXHeaderFile',
        'Tags',
        'AKA',
        'ImageFile',
        'FullName',
        'Goals',
        'Notes',
        'RTFFile',
        'SceneContent',
        'Outcome',
        'Goal',
        'Conflict'
        'Field_ChapterHeadingPrefix',
        'Field_ChapterHeadingSuffix',
        'Field_PartHeadingPrefix',
        'Field_PartHeadingSuffix',
        'Field_CustomGoal',
        'Field_CustomConflict',
        'Field_CustomOutcome',
        'Field_CustomChrBio',
        'Field_CustomChrGoals',
        'Field_ArcDefinition',
        'Field_SceneArcs',
        'Field_CustomAR',
        ]
    # Names of xml elements containing CDATA.
    # ElementTree.write omits CDATA tags, so they have to be inserted afterwards.

    STAGE_MARKER = 'stage'

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            filePath: str -- path to the yw7 file.
            
        Optional arguments:
            kwargs -- keyword arguments (not used here).            
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self.tree = None
        # xml element tree of the yWriter project
        self.wcLog = {}
        self._ywApIds = None

    def is_locked(self):
        """Check whether the yw7 file is locked by yWriter.
        
        Return True if a .lock file placed by yWriter exists.
        Otherwise, return False. 
        """
        return os.path.isfile(f'{self.filePath}.lock')

    def read(self):
        """Parse the yWriter xml file and get the instance variables.
        
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """
        if self.is_locked():
            raise Error(f'{_("yWriter seems to be open. Please close first")}.')

        self._noteCounter = 0
        self._noteNumber = 0
        self.tree = ET.parse(self.filePath)
        self._ywApIds = []
        self.wcLog = {}
        root = self.tree.getroot()
        self._read_project(root)
        self._read_locations(root)
        self._read_items(root)
        self._read_characters(root)
        self._read_projectvars(root)
        self._read_chapters(root)
        self._read_scenes(root)
        self._read_projectnotes(root)

        #--- Read the word count log.
        xmlWclog = root.find('WCLog')
        if xmlWclog is not None:
            for xmlWc in xmlWclog.iterfind('WC'):
                wcDate = xmlWc.find('Date').text
                wcCount = xmlWc.find('Count').text
                wcTotalCount = xmlWc.find('TotalCount').text
                self.wcLog[wcDate] = [wcCount, wcTotalCount]

        #--- Initialize empty scene character/location/item lists.
        # This helps deleting orphaned XML list items when saving the file.
        # Also fix missing scene status as a tribute to defensive programming.
        for scId in self.novel.sections:
            if self.novel.sections[scId].characters is None:
                self.novel.sections[scId].characters = []
            if self.novel.sections[scId].locations is None:
                self.novel.sections[scId].locations = []
            if self.novel.sections[scId].items is None:
                self.novel.sections[scId].items = []
            if self.novel.sections[scId].status is None:
                self.novel.sections[scId].status = 1

        #--- If no reasonable looking locale is set, set the system locale.
        self.novel.check_locale()

    def write(self):
        """Write instance variables to the yWriter xml file.
        
        Open the yWriter xml file located at filePath and replace the instance variables 
        not being None. Create new XML elements if necessary.
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """
        if self.is_locked():
            raise Error(f'{_("yWriter seems to be open. Please close first")}.')

        self._novxParser = NovxToYw7()
        self._noteCounter = 0
        self._noteNumber = 0
        if self.novel.languages is None:
            self.novel.get_languages()
        self._build_element_tree()
        self._write_element_tree(self)
        self._postprocess_xml_file(self.filePath)

    def _build_element_tree(self):
        """Modify the yWriter project attributes of an existing xml element tree."""

        def isTrue(value):
            if value:
                return '1'

        def set_element(parent, tag, text, index):
            if text is not None:
                subelement = ET.Element(tag)
                parent.insert(index, subelement)
                subelement.text = text
                index += 1
            return index

        def build_scene_subtree(xmlScene, prjScn, turningPoint=False):
            i = 1
            i = set_element(xmlScene, 'Title', prjScn.title, i)
            if prjScn.desc is not None:
                ET.SubElement(xmlScene, 'Desc').text = prjScn.desc

            if not turningPoint:
                scTags = prjScn.tags
                # copy of the scene's property

            #--- Write scene type.
            #
            # This is how yWriter 7.1.3.0 writes the scene type:
            #
            # Type   |<Unused>|Field_SceneType>|scType
            # -------+--------+----------------+------
            # Normal | N/A    | N/A            | 0
            # Notes  | -1     | 1              | 1
            # Todo   | -1     | 2              | 2
            # Unused | -1     | 0              | 3

            scTypeEncoding = (
                (False, None),
                (True, '1'),
                (True, '2'),
                (True, '0'),
                )
            if turningPoint:
                scType = 2
            elif prjScn.scType in (0, None):
                scType = 0
            elif prjScn.scType > 1:
                scType = 2
                if not scTags:
                    scTags = [self.STAGE_MARKER]
                elif not self.STAGE_MARKER in scTags:
                    scTags.append(self.STAGE_MARKER)
            else:
                scType = 3
            yUnused, ySceneType = scTypeEncoding[scType]
            if yUnused:
                ET.SubElement(xmlScene, 'Unused').text = '-1'
            if ySceneType is not None:
                ET.SubElement(xmlSceneFields[scId], 'Field_SceneType').text = ySceneType
            if turningPoint:
                ET.SubElement(xmlScene, 'Status').text = '1'
            elif prjScn.status is not None:
                ET.SubElement(xmlScene, 'Status').text = str(prjScn.status)

            if turningPoint:
                ET.SubElement(xmlScene, 'SceneContent')
                return

            self._novxParser.feed(f'<Content>{prjScn.sectionContent}</Content>')
            ET.SubElement(xmlScene, 'SceneContent').text = ''.join(self._novxParser.textList)
            if prjScn.notes:
                ET.SubElement(xmlScene, 'Notes').text = prjScn.notes
            if scTags:
                ET.SubElement(xmlScene, 'Tags').text = list_to_string(scTags)
            if prjScn.appendToPrev:
                ET.SubElement(xmlScene, 'AppendToPrev').text = '-1'

            #--- Write scene start.
            if (prjScn.date) and (prjScn.time):
                separator = ' '
                dateTime = f'{prjScn.date}{separator}{prjScn.time}'
                ET.SubElement(xmlScene, 'SpecificDateTime').text = dateTime
                ET.SubElement(xmlScene, 'SpecificDateMode').text = '-1'
            elif (prjScn.day) or (prjScn.time):
                if prjScn.day:
                    ET.SubElement(xmlScene, 'Day').text = prjScn.day
                if prjScn.time:
                    hours, minutes, __ = prjScn.time.split(':')
                    ET.SubElement(xmlScene, 'Hour').text = hours
                    ET.SubElement(xmlScene, 'Minute').text = minutes

            #--- Write scene duration.
            if prjScn.lastsDays:
                ET.SubElement(xmlScene, 'LastsDays').text = prjScn.lastsDays
            if prjScn.lastsHours:
                ET.SubElement(xmlScene, 'LastsHours').text = prjScn.lastsHours
            if prjScn.lastsMinutes:
                ET.SubElement(xmlScene, 'LastsMinutes').text = prjScn.lastsMinutes

            # Plot related information
            if prjScn.scPacing == 1:
                ET.SubElement(xmlScene, 'ReactionScene').text = '-1'
            if prjScn.goal:
                ET.SubElement(xmlScene, 'Goal').text = prjScn.goal
            if prjScn.conflict:
                ET.SubElement(xmlScene, 'Conflict').text = prjScn.conflict
            if prjScn.outcome:
                ET.SubElement(xmlScene, 'Outcome').text = prjScn.outcome

            #--- Characters/locations/items
            if prjScn.characters:
                xmlCharacters = ET.SubElement(xmlScene, 'Characters')
                for crId in prjScn.characters:
                    ET.SubElement(xmlCharacters, 'CharID').text = crId[2:]
            if prjScn.locations:
                xmlLocations = ET.SubElement(xmlScene, 'Locations')
                for lcId in prjScn.locations:
                    ET.SubElement(xmlLocations, 'LocID').text = lcId[2:]
            if prjScn.items:
                xmlItems = ET.SubElement(xmlScene, 'Items')
                for itId in prjScn.items:
                    ET.SubElement(xmlItems, 'ItemID').text = itId[2:]

        def build_chapter_subtree(xmlChapter, prjChp, acId=None, chType=None):
            # This is how yWriter 7.1.3.0 writes the chapter type:
            #
            # Type   |<Unused>|<Type>|<ChapterType>|chType
            #--------+--------+------+-------------+------
            # Normal | N/A    | 0    | 0           | 0
            # Notes  | -1     | 1    | 1           | 1
            # Todo   | -1     | 1    | 2           | 2
            # Unused | -1     | 1    | 0           | 3

            chTypeEncoding = (
                (False, '0', '0'),
                (True, '1', '1'),
                (True, '1', '2'),
                (True, '1', '0'),
                )
            if chType is None:
                if acId is not None:
                    chType = 2
                elif prjChp.chType in (0, None):
                    chType = 0
                else:
                    chType = 3
            yUnused, yType, yChapterType = chTypeEncoding[chType]

            i = 1
            i = set_element(xmlChapter, 'Title', prjChp.title, i)
            i = set_element(xmlChapter, 'Desc', prjChp.desc, i)

            if yUnused:
                elem = ET.Element('Unused')
                elem.text = '-1'
                xmlChapter.insert(i, elem)
                i += 1

            #--- Write chapter fields.
            xmlChapterFields = ET.SubElement(xmlChapter, 'Fields')
            i += 1
            if acId is None and prjChp.isTrash:
                ET.SubElement(xmlChapterFields, 'Field_IsTrash').text = '1'

            #--- Write chapter custom fields.
            if acId is None:
                fields = { 'Field_NoNumber': isTrue(prjChp.noNumber)}
            else:
                fields = {'Field_ArcDefinition': self.novel.arcs[acId].shortName}
            for field in fields:
                if fields[field]:
                    ET.SubElement(xmlChapterFields, field).text = fields[field]
            if acId is None and prjChp.chLevel == 1:
                ET.SubElement(xmlChapter, 'SectionStart').text = '-1'
                i += 1
            i = set_element(xmlChapter, 'Type', yType, i)
            i = set_element(xmlChapter, 'ChapterType', yChapterType, i)

        def build_location_subtree(xmlLoc, prjLoc):
            if prjLoc.title:
                ET.SubElement(xmlLoc, 'Title').text = prjLoc.title
            # if prjLoc.image:
            #    ET.SubElement(xmlLoc, 'ImageFile').text = prjLoc.image
            if prjLoc.desc:
                ET.SubElement(xmlLoc, 'Desc').text = prjLoc.desc
            if prjLoc.aka:
                ET.SubElement(xmlLoc, 'AKA').text = prjLoc.aka
            if prjLoc.tags:
                ET.SubElement(xmlLoc, 'Tags').text = list_to_string(prjLoc.tags)

        def add_projectvariable(title, desc, tags):
            # Note:
            # prjVars, xmlProjectvars are caller's variables
            pvId = create_id(prjVars)
            prjVars.append(pvId)
            # side effect
            xmlProjectvar = ET.SubElement(xmlProjectvars, 'PROJECTVAR')
            ET.SubElement(xmlProjectvar, 'ID').text = pvId
            ET.SubElement(xmlProjectvar, 'Title').text = title
            ET.SubElement(xmlProjectvar, 'Desc').text = desc
            ET.SubElement(xmlProjectvar, 'Tags').text = tags

        def build_item_subtree(xmlItm, prjItm):
            if prjItm.title:
                ET.SubElement(xmlItm, 'Title').text = prjItm.title
            # if prjItm.image:
            #     ET.SubElement(xmlItm, 'ImageFile').text = prjItm.image
            if prjItm.desc:
                ET.SubElement(xmlItm, 'Desc').text = prjItm.desc
            if prjItm.aka:
                ET.SubElement(xmlItm, 'AKA').text = prjItm.aka
            if prjItm.tags:
                ET.SubElement(xmlItm, 'Tags').text = list_to_string(prjItm.tags)

        def build_character_subtree(xmlCrt, prjCrt):
            if prjCrt.title:
                ET.SubElement(xmlCrt, 'Title').text = prjCrt.title
            if prjCrt.desc:
                ET.SubElement(xmlCrt, 'Desc').text = prjCrt.desc
            # if prjCrt.image:
            #    ET.SubElement(xmlCrt, 'ImageFile').text = prjCrt.image
            if prjCrt.notes:
                ET.SubElement(xmlCrt, 'Notes').text = prjCrt.notes
            if prjCrt.aka:
                ET.SubElement(xmlCrt, 'AKA').text = prjCrt.aka
            if prjCrt.tags:
                ET.SubElement(xmlCrt, 'Tags').text = list_to_string(prjCrt.tags)
            if prjCrt.bio:
                ET.SubElement(xmlCrt, 'Bio').text = prjCrt.bio
            if prjCrt.goals:
                ET.SubElement(xmlCrt, 'Goals').text = prjCrt.goals
            if prjCrt.fullName:
                ET.SubElement(xmlCrt, 'FullName').text = prjCrt.fullName
            if prjCrt.isMajor:
                ET.SubElement(xmlCrt, 'Major').text = '-1'
            fields = {
                'Field_BirthDate': prjCrt.birthDate,
                'Field_DeathDate': prjCrt.deathDate,
                }
            xmlCrtFields = None
            for field in fields:
                if fields[field]:
                    if xmlCrtFields is None:
                        xmlCrtFields = ET.SubElement(xmlCrt, 'Fields')
                    ET.SubElement(xmlCrtFields, field).text = fields[field]

        def build_project_subtree(xmlProject):
            ET.SubElement(xmlProject, 'Ver').text = '7'
            if self.novel.title:
                ET.SubElement(xmlProject, 'Title').text = self.novel.title
            if self.novel.desc:
                ET.SubElement(xmlProject, 'Desc').text = self.novel.desc
            if self.novel.authorName:
                ET.SubElement(xmlProject, 'AuthorName').text = self.novel.authorName
            if self.novel.wordCountStart is not None:
                ET.SubElement(xmlProject, 'WordCountStart').text = str(self.novel.wordCountStart)
            if self.novel.wordTarget is not None:
                ET.SubElement(xmlProject, 'WordTarget').text = str(self.novel.wordTarget)

            # Write project custom fields.
            workPhase = self.novel.workPhase
            if workPhase is not None:
                workPhase = str(workPhase)
            fields = {
                'Field_WorkPhase': workPhase,
                'Field_RenumberChapters': isTrue(self.novel.renumberChapters),
                'Field_RenumberParts': isTrue(self.novel.renumberParts),
                'Field_RenumberWithinParts': isTrue(self.novel.renumberWithinParts),
                'Field_RomanChapterNumbers': isTrue(self.novel.romanChapterNumbers),
                'Field_RomanPartNumbers': isTrue(self.novel.romanPartNumbers),
                'Field_ChapterHeadingPrefix': self.novel.chapterHeadingPrefix,
                'Field_ChapterHeadingSuffix': self.novel.chapterHeadingSuffix,
                'Field_PartHeadingPrefix': self.novel.partHeadingPrefix,
                'Field_PartHeadingSuffix': self.novel.partHeadingSuffix,
                'Field_CustomGoal': self.novel.customGoal,
                'Field_CustomConflict': self.novel.customConflict,
                'Field_CustomOutcome': self.novel.customOutcome,
                'Field_CustomChrBio': self.novel.customChrBio,
                'Field_CustomChrGoals': self.novel.customChrGoals,
                'Field_SaveWordCount': isTrue(self.novel.saveWordCount),
                'Field_ReferenceDate': self.novel.referenceDate,
                }
            xmlProjectFields = ET.SubElement(xmlProject, 'Fields')
            for field in fields:
                if fields[field]:
                    ET.SubElement(xmlProjectFields, field).text = fields[field]

        def build_prjNote_subtree(xmlProjectnote, projectNote):
            if projectNote.title is not None:
                ET.SubElement(xmlProjectnote, 'Title').text = projectNote.title

            if projectNote.desc is not None:
                ET.SubElement(xmlProjectnote, 'Desc').text = projectNote.desc

        #--- Build a new tree.
        root = ET.Element('YWRITER7')
        xmlProject = ET.SubElement(root, 'PROJECT')
        xmlLocations = ET.SubElement(root, 'LOCATIONS')
        xmlItems = ET.SubElement(root, 'ITEMS')
        xmlCharacters = ET.SubElement(root, 'CHARACTERS')
        xmlProjectvars = ET.SubElement(root, 'PROJECTVARS')
        xmlScenes = ET.SubElement(root, 'SCENES')
        xmlChapters = ET.SubElement(root, 'CHAPTERS')

        #--- Process project.
        build_project_subtree(xmlProject)

        #--- Process locations.
        for lcId in self.novel.tree.get_children(LC_ROOT):
            xmlLoc = ET.SubElement(xmlLocations, 'LOCATION')
            ET.SubElement(xmlLoc, 'ID').text = lcId[2:]
            build_location_subtree(xmlLoc, self.novel.locations[lcId])

        #--- Process items.
        for itId in self.novel.tree.get_children(IT_ROOT):
            xmlItm = ET.SubElement(xmlItems, 'ITEM')
            ET.SubElement(xmlItm, 'ID').text = itId[2:]
            build_item_subtree(xmlItm, self.novel.items[itId])

        #--- Process characters.
        for crId in self.novel.tree.get_children(CR_ROOT):
            xmlCrt = ET.SubElement(xmlCharacters, 'CHARACTER')
            ET.SubElement(xmlCrt, 'ID').text = crId[2:]
            build_character_subtree(xmlCrt, self.novel.characters[crId])

        #--- Process project variables.
        if self.novel.languages or self.novel.languageCode or self.novel.countryCode:
            self.novel.check_locale()
            prjVars = []

            # Define project variables for the locale.
            add_projectvariable('Language',
                                self.novel.languageCode,
                                '0')

            add_projectvariable('Country',
                                self.novel.countryCode,
                                '0')

            # Define project variables for the language code tags.
            for langCode in self.novel.languages:
                add_projectvariable(f'lang={langCode}',
                                    f'<HTM <SPAN LANG="{langCode}"> /HTM>',
                                    '0')
                add_projectvariable(f'/lang={langCode}',
                                    f'<HTM </SPAN> /HTM>',
                                    '0')
                # adding new IDs to the prjVars list

        #--- Process scenes.
        xmlSceneFields = {}
        scIds = list(self.novel.sections)
        for scId in scIds:
            xmlScene = ET.SubElement(xmlScenes, 'SCENE')
            ET.SubElement(xmlScene, 'ID').text = scId[2:]
            xmlSceneFields[scId] = ET.SubElement(xmlScene, 'Fields')
            build_scene_subtree(xmlScene, self.novel.sections[scId])

        #--- Process turning points.
        newScIds = {}
        # new scene IDs by turning point ID
        for tpId in self.novel.turningPoints:
            scId = create_id(scIds, prefix=SECTION_PREFIX)
            scIds.append(scId)
            newScIds[tpId] = scId
            xmlScene = ET.SubElement(xmlScenes, 'SCENE')
            ET.SubElement(xmlScene, 'ID').text = scId[2:]
            xmlSceneFields[scId] = ET.SubElement(xmlScene, 'Fields')
            build_scene_subtree(xmlScene, self.novel.turningPoints[tpId], turningPoint=True)

        #--- Process chapters.
        chIds = list(self.novel.tree.get_children(CH_ROOT))
        for chId in chIds:
            xmlChapter = ET.SubElement(xmlChapters, 'CHAPTER')
            ET.SubElement(xmlChapter, 'ID').text = chId[2:]
            build_chapter_subtree(xmlChapter, self.novel.chapters[chId])
            srtScenes = self.novel.tree.get_children(chId)
            if srtScenes:
                xmlScnList = ET.SubElement(xmlChapter, 'Scenes')
                for scId in self.novel.tree.get_children(chId):
                    ET.SubElement(xmlScnList, 'ScID').text = scId[2:]

        #--- Process arcs.
        chId = create_id(chIds, prefix=CHAPTER_PREFIX)
        chIds.append(chId)
        xmlChapter = ET.SubElement(xmlChapters, 'CHAPTER')
        ET.SubElement(xmlChapter, 'ID').text = chId[2:]
        arcPart = Chapter(title=_('Arcs'), chLevel=1)
        build_chapter_subtree(xmlChapter, arcPart, chType=2)
        for acId in self.novel.tree.get_children(AC_ROOT):
            chId = create_id(chIds, prefix=CHAPTER_PREFIX)
            chIds.append(chId)
            xmlChapter = ET.SubElement(xmlChapters, 'CHAPTER')
            ET.SubElement(xmlChapter, 'ID').text = chId[2:]
            build_chapter_subtree(xmlChapter, self.novel.arcs[acId], acId=acId)
            srtScenes = self.novel.tree.get_children(acId)
            if srtScenes:
                xmlScnList = ET.SubElement(xmlChapter, 'Scenes')
                for tpId in srtScenes:
                    ET.SubElement(xmlScnList, 'ScID').text = newScIds[tpId][2:]

        #--- Process project notes.
        if self.novel.tree.get_children(PN_ROOT):
            xmlProjectnotes = ET.SubElement(root, 'PROJECTNOTES')
            for pnId in self.novel.tree.get_children(PN_ROOT):
                xmlProjectnote = ET.SubElement(xmlProjectnotes, 'PROJECTNOTE')
                ET.SubElement(xmlProjectnote, 'ID').text = pnId[2:]
                build_prjNote_subtree(xmlProjectnote, self.novel.projectNotes[pnId])

        #--- Add arc/scene references.
        sectionArcs = {}
        sectionAssoc = {}
        for scId in scIds:
            sectionArcs[scId] = []
            sectionAssoc[scId] = []
        for acId in self.novel.arcs:
            for scId in self.novel.arcs[acId].sections:
                sectionArcs[scId].append(self.novel.arcs[acId].shortName)
            for tpId in self.novel.tree.get_children(acId):
                sectionArcs[newScIds[tpId]].append(self.novel.arcs[acId].shortName)
        for tpId in self.novel.turningPoints:
            if self.novel.turningPoints[tpId].sectionAssoc:
                sectionAssoc[self.novel.turningPoints[tpId].sectionAssoc].append(newScIds[tpId][2:])
                sectionAssoc[newScIds[tpId]].append(self.novel.turningPoints[tpId].sectionAssoc[2:])
        for scId in scIds:
            fields = {
                'Field_SceneArcs': list_to_string(sectionArcs[scId]),
                'Field_SceneAssoc': list_to_string(sectionAssoc[scId]),
                }
            for field in fields:
                if fields[field]:
                    ET.SubElement(xmlSceneFields[scId], field).text = fields[field]

        #--- Build the word count log.
        if self.wcLog:
            xmlWcLog = ET.SubElement(root, 'WCLog')
            wcLastCount = None
            wcLastTotalCount = None
            for wc in self.wcLog:
                if self.novel.saveWordCount:
                    # Discard entries with unchanged word count.
                    if self.wcLog[wc][0] == wcLastCount and self.wcLog[wc][1] == wcLastTotalCount:
                        continue

                    wcLastCount = self.wcLog[wc][0]
                    wcLastTotalCount = self.wcLog[wc][1]
                xmlWc = ET.SubElement(xmlWcLog, 'WC')
                ET.SubElement(xmlWc, 'Date').text = wc
                ET.SubElement(xmlWc, 'Count').text = self.wcLog[wc][0]
                ET.SubElement(xmlWc, 'TotalCount').text = self.wcLog[wc][1]

        #--- Prepare the XML tree for saving.
        indent(root)
        self.tree = ET.ElementTree(root)

    def _convert_to_novx(self, text):

        def replace_note(match):
            noteType = match.group(1)
            self._noteCounter += 1
            self._noteNumber += 1
            noteLabel = f'{self._noteNumber}'
            if noteType.startswith('fn'):
                noteClass = 'footnote'
                if noteType.endswith('*'):
                    self._noteNumber -= 1
                    noteLabel = '*'
            elif noteType.startswith('en'):
                noteClass = 'endnote'
            return (f'<note id="ftn{self._noteCounter}" '
                    f'class="{noteClass}"><note-citation>{noteLabel}</note-citation>'
                    f'<p>{match.group(2)}</p></note>')

        def replace_comment(match):
            if self.novel.authorName:
                creator = self.novel.authorName
            else:
                creator = _('unknown')
            return (f'<comment><creator>{creator}</creator>'
                    f'<date>{datetime.today().replace(microsecond=0).isoformat()}</date>'
                    f'<p>{match.group(1)}</p></comment>')

        if not text:
            text = ''
        else:
            #--- Remove inline raw code from text.
            text = text.replace('<RTFBRK>', '')
            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)
            # remove highlighting, alignment, strikethrough, and underline tags
            for specialCode in ('HTM', 'TEX', 'RTF', 'epub', 'mobi', 'rtfimg'):
                text = re.sub(f'\<{specialCode} .+?\/{specialCode}\>', '', text)

            #--- Apply XML predefined entities.
            xmlReplacements = [
                ('&', '&amp;'),
                ('>', '&gt;'),
                ('<', '&lt;'),
                ("'", '&apos;'),
                ('"', '&quot;'),
                ('\n', '</p><p>'),
                ('[i]', '<em>'),
                ('[/i]', '</em>'),
                ('[b]', '<strong>'),
                ('[/b]', '</strong>'),
                ]
            tags = ['i', 'b']
            if self.novel.languages is None:
                self.novel.get_languages()
            for language in self.novel.languages:
                tags.append(f'lang={language}')
                xmlReplacements.append((f'[lang={language}]', f'<span xml:lang="{language}">'))
                xmlReplacements.append((f'[/lang={language}]', '</span>'))

            #--- Process markup reaching across linebreaks.
            newlines = []
            lines = text.split('\n')
            isOpen = {}
            opening = {}
            closing = {}
            for tag in tags:
                isOpen[tag] = False
                opening[tag] = f'[{tag}]'
                closing[tag] = f'[/{tag}]'
            for line in lines:
                for tag in tags:
                    if isOpen[tag]:
                        if line.startswith('&gt; '):
                            line = f"&gt; {opening[tag]}{line.lstrip('&gt; ')}"
                        else:
                            line = f'{opening[tag]}{line}'
                        isOpen[tag] = False
                    while line.count(opening[tag]) > line.count(closing[tag]):
                        line = f'{line}{closing[tag]}'
                        isOpen[tag] = True
                    while line.count(closing[tag]) > line.count(opening[tag]):
                        line = f'{opening[tag]}{line}'
                    line = line.replace(f'{opening[tag]}{closing[tag]}', '')
                newlines.append(line)
            text = '\n'.join(newlines).rstrip()

            #--- Apply odt formating.
            for nv, od in xmlReplacements:
                text = text.replace(nv, od)

            #--- Convert comments, footnotes, and endnotes.
            if text.find('/*') > 0:
                text = re.sub('\/\* *@([ef]n\**) (.*?)\*\/', replace_note, text)
                text = re.sub('\/\*(.*?)\*\/', replace_comment, text)

            text = f'<p>{text}</p>'
            text = re.sub('\<p\>\&gt\; (.*?)\<\/p\>', '<p style="quotations">\\1</p>', text)
        return text

    def _postprocess_xml_file(self, filePath):
        """Postprocess an xml file created by ElementTree.
        
        Positional argument:
            filePath: str -- path to xml file.
        
        Read the xml file, put a header on top, insert the missing CDATA tags,
        and replace xml entities by plain text (unescape). Overwrite the .yw7 xml file.
        Raise the "Error" exception in case of error. 
        
        Note: The path is given as an argument rather than using self.filePath. 
        So this routine can be used for yWriter-generated xml files other than .yw7 as well. 
        """
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = text.split('\n')
        newlines = ['<?xml version="1.0" encoding="utf-8"?>']
        for line in lines:
            for tag in self._CDATA_TAGS:
                line = re.sub(f'\<{tag}\>', f'<{tag}><![CDATA[', line)
                line = re.sub(f'\<\/{tag}\>', f']]></{tag}>', line)
            newlines.append(line)
        text = '\n'.join(newlines)
        text = text.replace('[CDATA[ \n', '[CDATA[')
        text = text.replace('\n]]', ']]')
        if not self.novel.chapters:
            text = text.replace('<CHAPTERS />', '<CHAPTERS></CHAPTERS>')
            # otherwise, yWriter fails to parse the file if there are no chapters.
        text = unescape(text)
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            raise Error(f'{_("Cannot write file")}: "{norm_path(filePath)}".')

    def _read_locations(self, root):
        """Read locations from the xml element tree."""
        self.novel.tree.delete_children(LC_ROOT)
        # This is necessary for re-reading.
        for xmlLocation in root.find('LOCATIONS'):
            lcId = f"{LOCATION_PREFIX}{xmlLocation.find('ID').text}"
            self.novel.tree.append(LC_ROOT, lcId)
            self.novel.locations[lcId] = WorldElement()

            if xmlLocation.find('Title') is not None:
                self.novel.locations[lcId].title = xmlLocation.find('Title').text

            # if xmlLocation.find('ImageFile') is not None:
            #    self.novel.locations[lcId].image = xmlLocation.find('ImageFile').text

            if xmlLocation.find('Desc') is not None:
                self.novel.locations[lcId].desc = xmlLocation.find('Desc').text

            if xmlLocation.find('AKA') is not None:
                self.novel.locations[lcId].aka = xmlLocation.find('AKA').text

            if xmlLocation.find('Tags') is not None:
                if xmlLocation.find('Tags').text is not None:
                    tags = string_to_list(xmlLocation.find('Tags').text)
                    self.novel.locations[lcId].tags = self._strip_spaces(tags)

    def _read_items(self, root):
        """Read items from the xml element tree."""
        self.novel.tree.delete_children(IT_ROOT)
        # This is necessary for re-reading.
        for xmlItem in root.find('ITEMS'):
            itId = f"{ITEM_PREFIX}{xmlItem.find('ID').text}"
            self.novel.tree.append(IT_ROOT, itId)
            self.novel.items[itId] = WorldElement()

            if xmlItem.find('Title') is not None:
                self.novel.items[itId].title = xmlItem.find('Title').text

            # if xmlItem.find('ImageFile') is not None:
            #    self.novel.items[itId].image = xmlItem.find('ImageFile').text

            if xmlItem.find('Desc') is not None:
                self.novel.items[itId].desc = xmlItem.find('Desc').text

            if xmlItem.find('AKA') is not None:
                self.novel.items[itId].aka = xmlItem.find('AKA').text

            if xmlItem.find('Tags') is not None:
                if xmlItem.find('Tags').text is not None:
                    tags = string_to_list(xmlItem.find('Tags').text)
                    self.novel.items[itId].tags = self._strip_spaces(tags)

    def _read_chapters(self, root):
        """Read attributes at chapter level from the xml element tree."""
        self.novel.tree.delete_children(CH_ROOT)
        self.novel.tree.delete_children(AC_ROOT)
        # This is necessary for re-reading.
        for xmlChapter in root.find('CHAPTERS'):
            prjChapter = Chapter()

            if xmlChapter.find('Title') is not None:
                prjChapter.title = xmlChapter.find('Title').text

            if xmlChapter.find('Desc') is not None:
                prjChapter.desc = xmlChapter.find('Desc').text

            if xmlChapter.find('SectionStart') is not None:
                prjChapter.chLevel = 1
            else:
                prjChapter.chLevel = 2

            # This is how yWriter 7.1.3.0 reads the chapter type:
            #
            # Type   |<Unused>|<Type>|<ChapterType>|chType
            # -------+--------+------+--------------------
            # Normal | N/A    | N/A  | N/A         | 0
            # Normal | N/A    | 0    | N/A         | 0
            # Notes  | x      | 1    | N/A         | 1
            # Unused | -1     | 0    | N/A         | 1
            # Normal | N/A    | x    | 0           | 0
            # Notes  | x      | x    | 1           | 1
            # Todo   | x      | x    | 2           | 1
            # Unused | -1     | x    | x           | 1

            prjChapter.chType = 0
            if xmlChapter.find('Unused') is not None:
                yUnused = True
            else:
                yUnused = False
            if xmlChapter.find('ChapterType') is not None:
                # The file may be created with yWriter version 7.0.7.2+
                yChapterType = xmlChapter.find('ChapterType').text
                if yChapterType == '2':
                    prjChapter.chType = 1
                elif yChapterType == '1':
                    prjChapter.chType = 1
                elif yUnused:
                    prjChapter.chType = 1
            else:
                # The file may be created with a yWriter version prior to 7.0.7.2
                if xmlChapter.find('Type') is not None:
                    yType = xmlChapter.find('Type').text
                    if yType == '1':
                        prjChapter.chType = 1
                    elif yUnused:
                        prjChapter.chType = 1

            #--- Read chapter fields.
            kwVarYw7 = {}
            for xmlChapterFields in xmlChapter.iterfind('Fields'):
                prjChapter.isTrash = False
                if xmlChapterFields.find('Field_IsTrash') is not None:
                    if xmlChapterFields.find('Field_IsTrash').text == '1':
                        prjChapter.isTrash = True

                #--- Read chapter custom fields.
                for fieldName in self.CHP_KWVAR_YW7:
                    xmlField = xmlChapterFields.find(fieldName)
                    if xmlField  is not None:
                        kwVarYw7[fieldName] = xmlField .text
            prjChapter.noNumber = kwVarYw7.get('Field_NoNumber', False)
            shortName = kwVarYw7.get('Field_ArcDefinition', '')

            # This is for projects written with noveltree v4.3:
            field = kwVarYw7.get('Field_Arc_Definition', None)
            if field is not None:
                shortName = field

            #--- Read chapter's scene list.
            scenes = []
            if xmlChapter.find('Scenes') is not None:
                for scn in xmlChapter.find('Scenes').iterfind('ScID'):
                    scId = scn.text
                    scenes.append(scId)

            if shortName:
                acId = f"{ARC_PREFIX}{xmlChapter.find('ID').text}"
                self.novel.arcs[acId] = Arc()
                self.novel.arcs[acId].title = prjChapter.title
                self.novel.arcs[acId].desc = prjChapter.desc
                self.novel.arcs[acId].shortName = shortName
                self.novel.tree.append(AC_ROOT, acId)
                for scId in scenes:
                    self.novel.tree.append(acId, f'{ARC_POINT_PREFIX}{scId}')
                    self._ywApIds.append(scId)
                    # this is necessary for turning yWriter scenes into noveltree turning points
            else:
                chId = f"{CHAPTER_PREFIX}{xmlChapter.find('ID').text}"
                self.novel.chapters[chId] = prjChapter
                self.novel.tree.append(CH_ROOT, chId)
                for scId in scenes:
                    self.novel.tree.append(chId, f'{SECTION_PREFIX}{scId}')

    def _read_characters(self, root):
        """Read characters from the xml element tree."""
        self.novel.tree.delete_children(CR_ROOT)
        # This is necessary for re-reading.
        for xmlCharacter in root.find('CHARACTERS'):
            crId = f"{CHARACTER_PREFIX}{xmlCharacter.find('ID').text}"
            self.novel.tree.append(CR_ROOT, crId)
            self.novel.characters[crId] = Character()

            if xmlCharacter.find('Title') is not None:
                self.novel.characters[crId].title = xmlCharacter.find('Title').text

            # if xmlCharacter.find('ImageFile') is not None:
            #    self.novel.characters[crId].image = xmlCharacter.find('ImageFile').text
            # TODO: read link

            if xmlCharacter.find('Desc') is not None:
                self.novel.characters[crId].desc = xmlCharacter.find('Desc').text

            if xmlCharacter.find('AKA') is not None:
                self.novel.characters[crId].aka = xmlCharacter.find('AKA').text

            if xmlCharacter.find('Tags') is not None:
                if xmlCharacter.find('Tags').text is not None:
                    tags = string_to_list(xmlCharacter.find('Tags').text)
                    self.novel.characters[crId].tags = self._strip_spaces(tags)

            if xmlCharacter.find('Notes') is not None:
                self.novel.characters[crId].notes = xmlCharacter.find('Notes').text

            if xmlCharacter.find('Bio') is not None:
                self.novel.characters[crId].bio = xmlCharacter.find('Bio').text

            if xmlCharacter.find('Goals') is not None:
                self.novel.characters[crId].goals = xmlCharacter.find('Goals').text

            if xmlCharacter.find('FullName') is not None:
                self.novel.characters[crId].fullName = xmlCharacter.find('FullName').text

            if xmlCharacter.find('Major') is not None:
                self.novel.characters[crId].isMajor = True
            else:
                self.novel.characters[crId].isMajor = False
                #--- Read scene custom fields.

            kwVarYw7 = {}
            xmlCharacterFields = xmlCharacter.find('Fields')
            if xmlCharacterFields is not None:
                for fieldName in self.CRT_KWVAR_YW7:
                    xmlField = xmlCharacterFields.find(fieldName)
                    if xmlField  is not None:
                        kwVarYw7[fieldName] = xmlField.text
            self.novel.characters[crId].birthDate = kwVarYw7.get('Field_BirthDate', '')
            self.novel.characters[crId].deathDate = kwVarYw7.get('Field_DeathDate', '')

    def _read_project(self, root):
        """Read attributes at project level from the xml element tree."""
        xmlProject = root.find('PROJECT')

        if xmlProject.find('Title') is not None:
            self.novel.title = xmlProject.find('Title').text

        if xmlProject.find('AuthorName') is not None:
            self.novel.authorName = xmlProject.find('AuthorName').text

        if xmlProject.find('Desc') is not None:
            self.novel.desc = xmlProject.find('Desc').text

        #--- Read word target data.
        if xmlProject.find('WordCountStart') is not None:
            try:
                self.novel.wordCountStart = int(xmlProject.find('WordCountStart').text)
            except:
                pass
        if xmlProject.find('WordTarget') is not None:
            try:
                self.novel.wordTarget = int(xmlProject.find('WordTarget').text)
            except:
                pass

        #--- Read project custom fields.
        kwVarYw7 = {}
        for xmlProjectFields in xmlProject.iterfind('Fields'):
            for fieldName in self.PRJ_KWVAR_YW7:
                xmlField = xmlProjectFields.find(fieldName)
                if xmlField  is not None:
                    kwVarYw7[fieldName] = xmlField .text
        self.novel.workPhase = kwVarYw7.get('Field_WorkPhase', None)
        self.novel.renumberChapters = kwVarYw7.get('Field_RenumberChapters', False)
        self.novel.renumberParts = kwVarYw7.get('Field_RenumberParts', False)
        self.novel.renumberWithinParts = kwVarYw7.get('Field_RenumberWithinParts', False)
        self.novel.romanChapterNumbers = kwVarYw7.get('Field_RomanChapterNumbers', False)
        self.novel.romanPartNumbers = kwVarYw7.get('Field_RomanPartNumbers', False)
        self.novel.chapterHeadingPrefix = kwVarYw7.get('Field_ChapterHeadingPrefix', '')
        self.novel.chapterHeadingSuffix = kwVarYw7.get('Field_ChapterHeadingSuffix', '')
        self.novel.partHeadingPrefix = kwVarYw7.get('Field_PartHeadingPrefix', '')
        self.novel.partHeadingSuffix = kwVarYw7.get('Field_PartHeadingSuffix', '')
        self.novel.customGoal = kwVarYw7.get('Field_CustomGoal', '')
        self.novel.customConflict = kwVarYw7.get('Field_CustomConflict', '')
        self.novel.customOutcome = kwVarYw7.get('Field_CustomOutcome', '')
        self.novel.customChrBio = kwVarYw7.get('Field_CustomChrBio', '')
        self.novel.customChrGoals = kwVarYw7.get('Field_CustomChrGoals', '')
        self.novel.saveWordCount = kwVarYw7.get('Field_SaveWordCount', False)

        # This is for projects written with novxlib v7.6 - v7.10:
        field = kwVarYw7.get('Field_LanguageCode', None)
        if field is not None:
            self.novel.languageCode = field
        field = kwVarYw7.get('Field_CountryCode', None)
        if field is not None:
            self.novel.countryCode = field

    def _read_projectnotes(self, root):
        """Read project notes from the xml element tree.
        
        If any, create "Notes" scenes in the "Project notes" chapter.
        """
        if root.find('PROJECTNOTES') is not None:
            for xmlProjectnote in root.find('PROJECTNOTES'):
                if xmlProjectnote.find('ID') is not None:
                    pnId = f"{PRJ_NOTE_PREFIX}{xmlProjectnote.find('ID').text}"
                    self.novel.tree.append(PN_ROOT, pnId)
                    self.novel.projectNotes[pnId] = BasicElement()
                    if xmlProjectnote.find('Title') is not None:
                        self.novel.projectNotes[pnId].title = xmlProjectnote.find('Title').text
                    if xmlProjectnote.find('Desc') is not None:
                        self.novel.projectNotes[pnId].desc = xmlProjectnote.find('Desc').text

    def _read_projectvars(self, root):
        """Read relevant project variables from the xml element tree."""
        try:
            for xmlProjectvar in root.find('PROJECTVARS'):
                if xmlProjectvar.find('Title') is not None:
                    title = xmlProjectvar.find('Title').text
                    if title == 'Language':
                        if xmlProjectvar.find('Desc') is not None:
                            self.novel.languageCode = xmlProjectvar.find('Desc').text

                    elif title == 'Country':
                        if xmlProjectvar.find('Desc') is not None:
                            self.novel.countryCode = xmlProjectvar.find('Desc').text

                    elif title.startswith('lang='):
                        try:
                            __, langCode = title.split('=')
                            if self.novel.languages is None:
                                self.novel.languages = []
                            self.novel.languages.append(langCode)
                        except:
                            pass
        except:
            pass

    def _read_scenes(self, root):
        """ Read attributes at scene level from the xml element tree."""
        for xmlScene in root.find('SCENES'):
            prjScn = Section()

            if xmlScene.find('Title') is not None:
                prjScn.title = xmlScene.find('Title').text

            if xmlScene.find('Desc') is not None:
                prjScn.desc = xmlScene.find('Desc').text

            if xmlScene.find('SceneContent') is not None:
                sceneContent = xmlScene.find('SceneContent').text
                if sceneContent is not None:
                    prjScn.sectionContent = self._convert_to_novx(sceneContent)

            #--- Read scene type.

            # This is how yWriter 7.1.3.0 reads the scene type:
            #
            # Type   |<Unused>|Field_SceneType>|scType
            #--------+--------+----------------+------
            # Notes  | x      | 1              | 1
            # Todo   | x      | 2              | 1
            # Unused | -1     | N/A            | 1
            # Unused | -1     | 0              | 1
            # Normal | N/A    | N/A            | 0
            # Normal | N/A    | 0              | 0

            prjScn.scType = 0
            kwVarYw7 = {}
            for xmlSceneFields in xmlScene.iterfind('Fields'):
                # Read scene type, if any.
                if xmlSceneFields.find('Field_SceneType') is not None:
                    if xmlSceneFields.find('Field_SceneType').text == '1':
                        prjScn.scType = 1
                    elif xmlSceneFields.find('Field_SceneType').text == '2':
                        prjScn.scType = 1

                #--- Read scene custom fields.
                for fieldName in self.SCN_KWVAR_YW7:
                    xmlField = xmlSceneFields.find(fieldName)
                    if xmlField  is not None:
                        kwVarYw7[fieldName] = xmlField.text

            ywScnArcs = string_to_list(kwVarYw7.get('Field_SceneArcs', ''))
            for shortName in ywScnArcs:
                for acId in self.novel.arcs:
                    if self.novel.arcs[acId].shortName == shortName:
                        if prjScn.scType == 0:
                            arcSections = self.novel.arcs[acId].sections
                            if not arcSections:
                                arcSections = [f"{SECTION_PREFIX}{xmlScene.find('ID').text}"]
                            else:
                                arcSections.append(f"{SECTION_PREFIX}{xmlScene.find('ID').text}")
                            self.novel.arcs[acId].sections = arcSections
                        break

            ywScnAssocs = string_to_list(kwVarYw7.get('Field_SceneAssoc', ''))
            prjScn.turningPoints = [f'{ARC_POINT_PREFIX}{turningPoint}' for turningPoint in ywScnAssocs]

            if kwVarYw7.get('Field_CustomAR', None) is not None:
                prjScn.scPacing = 2
            elif xmlScene.find('ReactionScene') is not None:
                prjScn.scPacing = 1
            else:
                prjScn.scPacing = 0

            # Unused.
            if xmlScene.find('Unused') is not None:
                if prjScn.scType == 0:
                    prjScn.scType = 1

            if xmlScene.find('Status') is not None:
                prjScn.status = int(xmlScene.find('Status').text)

            if xmlScene.find('Notes') is not None:
                prjScn.notes = xmlScene.find('Notes').text

            if xmlScene.find('Tags') is not None:
                if xmlScene.find('Tags').text is not None:
                    tags = string_to_list(xmlScene.find('Tags').text)
                    prjScn.tags = self._strip_spaces(tags)

            if xmlScene.find('AppendToPrev') is not None:
                prjScn.appendToPrev = True
            else:
                prjScn.appendToPrev = False

            #--- Scene start.
            if xmlScene.find('SpecificDateTime') is not None:
                dateTimeStr = xmlScene.find('SpecificDateTime').text

                # Check SpecificDateTime for ISO compliance.
                try:
                    dateTime = datetime.fromisoformat(dateTimeStr)
                except:
                    prjScn.date = ''
                    prjScn.time = ''
                else:
                    startDateTime = dateTime.isoformat().split('T')
                    prjScn.date = startDateTime[0]
                    prjScn.time = startDateTime[1]
            else:
                if xmlScene.find('Day') is not None:
                    day = xmlScene.find('Day').text

                    # Check if Day represents an integer.
                    try:
                        int(day)
                    except ValueError:
                        day = ''
                    prjScn.day = day

                hasUnspecificTime = False
                if xmlScene.find('Hour') is not None:
                    hour = xmlScene.find('Hour').text.zfill(2)
                    hasUnspecificTime = True
                else:
                    hour = '00'
                if xmlScene.find('Minute') is not None:
                    minute = xmlScene.find('Minute').text.zfill(2)
                    hasUnspecificTime = True
                else:
                    minute = '00'
                if hasUnspecificTime:
                    prjScn.time = f'{hour}:{minute}:00'

            #--- Scene duration.
            if xmlScene.find('LastsDays') is not None:
                prjScn.lastsDays = xmlScene.find('LastsDays').text

            if xmlScene.find('LastsHours') is not None:
                prjScn.lastsHours = xmlScene.find('LastsHours').text

            if xmlScene.find('LastsMinutes') is not None:
                prjScn.lastsMinutes = xmlScene.find('LastsMinutes').text

            if xmlScene.find('Goal') is not None:
                prjScn.goal = xmlScene.find('Goal').text

            if xmlScene.find('Conflict') is not None:
                prjScn.conflict = xmlScene.find('Conflict').text

            if xmlScene.find('Outcome') is not None:
                prjScn.outcome = xmlScene.find('Outcome').text

            # if xmlScene.find('ImageFile') is not None:
            #    prjScn.image = xmlScene.find('ImageFile').text

            #--- Characters associated with the scene.
            scCharacters = []
            if xmlScene.find('Characters') is not None:
                for character in xmlScene.find('Characters').iter('CharID'):
                    crId = f"{CHARACTER_PREFIX}{character.text}"
                    if crId in self.novel.tree.get_children(CR_ROOT):
                        scCharacters.append(crId)
            prjScn.characters = scCharacters

            #--- Locations associated with the scene.
            scLocations = []
            if xmlScene.find('Locations') is not None:
                for location in xmlScene.find('Locations').iter('LocID'):
                    lcId = f"{LOCATION_PREFIX}{location.text}"
                    if lcId in self.novel.tree.get_children(LC_ROOT):
                        scLocations.append(lcId)
            prjScn.locations = scLocations

            #--- Items associated with the scene.
            scItems = []
            if xmlScene.find('Items') is not None:
                for item in xmlScene.find('Items').iter('ItemID'):
                    itId = f"{ITEM_PREFIX}{item.text}"
                    if itId in self.novel.tree.get_children(IT_ROOT):
                        scItems.append(itId)
            prjScn.items = scItems

            ywScId = xmlScene.find('ID').text
            if ywScId in self._ywApIds:
                # it's a turning point
                ptId = f"{ARC_POINT_PREFIX}{ywScId}"
                self.novel.turningPoints[ptId] = TurningPoint(title=prjScn.title,
                                                      desc=prjScn.desc
                                                      )
                if ywScnAssocs:
                    self.novel.turningPoints[ptId].sectionAssoc = f'{SECTION_PREFIX}{ywScnAssocs[0]}'
            else:
                # it's a scene
                if prjScn.tags and self.STAGE_MARKER in prjScn.tags:
                    # no, it's a stage
                    prjScn.scType = 3
                    prjScn.tags = prjScn.tags.remove(self.STAGE_MARKER)
                scId = f"{SECTION_PREFIX}{ywScId}"
                self.novel.sections[scId] = prjScn

    def _strip_spaces(self, lines):
        """Local helper method.

        Positional argument:
            lines -- list of strings

        Return lines with leading and trailing spaces removed.
        """
        stripped = []
        for line in lines:
            stripped.append(line.strip())
        return stripped

    def _write_element_tree(self, ywProject):
        """Write back the xml element tree to a .yw7 xml file located at filePath.
        
        Raise the "Error" exception in case of error. 
        """
        backedUp = False
        if os.path.isfile(ywProject.filePath):
            try:
                os.replace(ywProject.filePath, f'{ywProject.filePath}.bak')
            except:
                raise Error(f'{_("Cannot overwrite file")}: "{norm_path(ywProject.filePath)}".')
            else:
                backedUp = True
        try:
            ywProject.tree.write(ywProject.filePath, xml_declaration=False, encoding='utf-8')
        except:
            if backedUp:
                os.replace(f'{ywProject.filePath}.bak', ywProject.filePath)
            raise Error(f'{_("Cannot write file")}: "{norm_path(ywProject.filePath)}".')

