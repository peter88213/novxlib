"""Provide a class for novx file import and export.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from datetime import date
from datetime import time
import os

from novxlib.file.file import File
from novxlib.model.plot_line import PlotLine
from novxlib.model.basic_element import BasicElement
from novxlib.model.chapter import Chapter
from novxlib.model.character import Character
from novxlib.model.section import Section
from novxlib.model.plot_point import PlotPoint
from novxlib.model.world_element import WorldElement
from novxlib.novx_globals import PL_ROOT
from novxlib.novx_globals import CH_ROOT
from novxlib.novx_globals import CR_ROOT
from novxlib.novx_globals import Error
from novxlib.novx_globals import IT_ROOT
from novxlib.novx_globals import LC_ROOT
from novxlib.novx_globals import PN_ROOT
from novxlib.novx_globals import _
from novxlib.novx_globals import list_to_string
from novxlib.novx_globals import norm_path
from novxlib.novx_globals import string_to_list
from novxlib.xml.etree_tools import *
from novxlib.xml.xml_indent import indent
import xml.etree.ElementTree as ET


class NovxFile(File):
    """novx file representation.

    Public instance variables:
        tree -- xml element tree of the novelibre project
        wcLog: dict[str, list[str, str]] -- Daily word count logs.
        wcLogUpdate: dict[str, list[str, str]] -- Word counts missing in the log.
    
    """
    DESCRIPTION = _('novelibre project')
    EXTENSION = '.novx'

    MAJOR_VERSION = 1
    MINOR_VERSION = 1
    # DTD version.

    XML_HEADER = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE novx SYSTEM "novx_{MAJOR_VERSION}_{MINOR_VERSION}.dtd">
<?xml-stylesheet href="novx.css" type="text/css"?>
'''

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            filePath: str -- path to the novx file.
            
        Optional arguments:
            kwargs -- keyword arguments (not used here).            
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self.on_element_change = None
        self.xmlTree = None
        self.wcLog = {}
        # key: str -- date (iso formatted)
        # value: list -- [word count: str, with unused: str]
        self.wcLogUpdate = {}

    def adjust_section_types(self):
        """Make sure that nodes with "Unused" parents inherit the type."""
        partType = 0
        for chId in self.novel.tree.get_children(CH_ROOT):
            if self.novel.chapters[chId].chLevel == 1:
                partType = self.novel.chapters[chId].chType
            elif partType != 0 and not self.novel.chapters[chId].isTrash:
                self.novel.chapters[chId].chType = partType
            for scId in self.novel.tree.get_children(chId):
                if self.novel.sections[scId].scType < self.novel.chapters[chId].chType:
                    self.novel.sections[scId].scType = self.novel.chapters[chId].chType

    def count_words(self):
        """Return a tuple of word count totals.
        
        count: int -- Total words of "normal" type sections.
        totalCount: int -- Total words of "normal" and "unused" sections.
        """
        count = 0
        totalCount = 0
        for chId in self.novel.tree.get_children(CH_ROOT):
            if not self.novel.chapters[chId].isTrash:
                for scId in self.novel.tree.get_children(chId):
                    if self.novel.sections[scId].scType < 2:
                        totalCount += self.novel.sections[scId].wordCount
                        if self.novel.sections[scId].scType == 0:
                            count += self.novel.sections[scId].wordCount
        return count, totalCount

    def read(self):
        """Parse the novelibre xml file and get the instance variables.
        
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """
        self.xmlTree = ET.parse(self.filePath)
        xmlRoot = self.xmlTree.getroot()
        try:
            majorVersionStr, minorVersionStr = xmlRoot.attrib['version'].split('.')
            majorVersion = int(majorVersionStr)
            minorVersion = int(minorVersionStr)
        except:
            raise Error(f'{_("No valid version found in file")}: "{norm_path(self.filePath)}".')

        if majorVersion > self.MAJOR_VERSION:
            raise Error(_('The project "{}" was created with a newer novelibre version.').format(norm_path(self.filePath)))

        elif majorVersion < self.MAJOR_VERSION:
            raise Error(_('The project "{}" was created with an outdated novelibre version.').format(norm_path(self.filePath)))

        elif minorVersion > self.MINOR_VERSION:
            raise Error(_('The project "{}" was created with a newer novelibre version.').format(norm_path(self.filePath)))

        try:
            locale = xmlRoot.attrib['{http://www.w3.org/XML/1998/namespace}lang']
            self.novel.languageCode, self.novel.countryCode = locale.split('-')
        except:
            pass
        self.novel.tree.reset()
        self._read_project(xmlRoot)
        self._read_locations(xmlRoot)
        self._read_items(xmlRoot)
        self._read_characters(xmlRoot)
        self._read_chapters(xmlRoot)
        self._read_plot_lines(xmlRoot)
        self._read_project_notes(xmlRoot)
        self.adjust_section_types()

        #--- Read the word count log.
        xmlWclog = xmlRoot.find('PROGRESS')
        if xmlWclog is not None:
            for xmlWc in xmlWclog.iterfind('WC'):
                wcDate = xmlWc.find('Date').text
                wcCount = xmlWc.find('Count').text
                wcTotalCount = xmlWc.find('WithUnused').text
                if wcDate and wcCount and wcTotalCount:
                    self.wcLog[wcDate] = [wcCount, wcTotalCount]

    def write(self):
        """Write instance variables to the novx xml file.
        
        Update the word count log, write the file, and update the timestamp.
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """
        if self.novel.saveWordCount:
            # Add today's word count and word count on reading, if not logged.
            newCountInt, newTotalCountInt = self.count_words()
            newCount = str(newCountInt)
            newTotalCount = str(newTotalCountInt)
            today = date.today().isoformat()
            self.wcLogUpdate[today] = [newCount, newTotalCount]
            for wcDate in self.wcLogUpdate:
                self.wcLog[wcDate] = self.wcLogUpdate[wcDate]
        self.wcLogUpdate = {}
        self.adjust_section_types()
        self.novel.get_languages()
        attrib = {'version':f'{self.MAJOR_VERSION}.{self.MINOR_VERSION}',
                'xml:lang':f'{self.novel.languageCode}-{self.novel.countryCode}',
                }
        xmlRoot = ET.Element('novx', attrib=attrib)
        self._build_element_tree(xmlRoot)
        indent(xmlRoot)
        self.xmlTree = ET.ElementTree(xmlRoot)
        self._write_element_tree(self)
        self._postprocess_xml_file(self.filePath)

    def _build_plot_line_branch(self, xmlPlotLines, prjPlotLine, plId):
        xmlPlotLine = ET.SubElement(xmlPlotLines, 'ARC', attrib={'id':plId})
        if prjPlotLine.title:
            ET.SubElement(xmlPlotLine, 'Title').text = prjPlotLine.title
        if prjPlotLine.shortName:
            ET.SubElement(xmlPlotLine, 'ShortName').text = prjPlotLine.shortName
        if prjPlotLine.desc:
            xmlPlotLine.append(text_to_xml_element('Desc', prjPlotLine.desc))

        #--- References
        if prjPlotLine.sections:
            attrib = {'ids':' '.join(prjPlotLine.sections)}
            ET.SubElement(xmlPlotLine, 'Sections', attrib=attrib)

        #--- Plot points.
        for ppId in self.novel.tree.get_children(plId):
            xmlPlotPoint = ET.SubElement(xmlPlotLine, 'POINT', attrib={'id':ppId})
            self._build_plot_point_branch(xmlPlotPoint, self.novel.plotPoints[ppId])

        return xmlPlotLine

    def _build_plot_point_branch(self, xmlPlotPoint, prjPlotPoint):
        if prjPlotPoint.title:
            ET.SubElement(xmlPlotPoint, 'Title').text = prjPlotPoint.title
        if prjPlotPoint.desc:
            xmlPlotPoint.append(text_to_xml_element('Desc', prjPlotPoint.desc))
        if prjPlotPoint.notes:
            xmlPlotPoint.append(text_to_xml_element('Notes', prjPlotPoint.notes))

        #--- References.
        if prjPlotPoint.sectionAssoc:
            ET.SubElement(xmlPlotPoint, 'Section', attrib={'id': prjPlotPoint.sectionAssoc})

    def _build_chapter_branch(self, xmlChapters, prjChp, chId):
        xmlChapter = ET.SubElement(xmlChapters, 'CHAPTER', attrib={'id':chId})
        if prjChp.chType:
            xmlChapter.set('type', str(prjChp.chType))
        if prjChp.chLevel == 1:
            xmlChapter.set('level', '1')
        if prjChp.isTrash:
            xmlChapter.set('isTrash', '1')
        if prjChp.noNumber:
            xmlChapter.set('noNumber', '1')
        if prjChp.title:
            ET.SubElement(xmlChapter, 'Title').text = prjChp.title
        if prjChp.desc:
            xmlChapter.append(text_to_xml_element('Desc', prjChp.desc))
        for scId in self.novel.tree.get_children(chId):
            xmlSection = ET.SubElement(xmlChapter, 'SECTION', attrib={'id':scId})
            self._build_section_branch(xmlSection, self.novel.sections[scId])
        return xmlChapter

    def _build_character_branch(self, xmlCrt, prjCrt):
        if prjCrt.isMajor:
            xmlCrt.set('major', '1')
        if prjCrt.title:
            ET.SubElement(xmlCrt, 'Title').text = prjCrt.title
        if prjCrt.fullName:
            ET.SubElement(xmlCrt, 'FullName').text = prjCrt.fullName
        if prjCrt.aka:
            ET.SubElement(xmlCrt, 'Aka').text = prjCrt.aka
        if prjCrt.desc:
            xmlCrt.append(text_to_xml_element('Desc', prjCrt.desc))
        if prjCrt.bio:
            xmlCrt.append(text_to_xml_element('Bio', prjCrt.bio))
        if prjCrt.goals:
            xmlCrt.append(text_to_xml_element('Goals', prjCrt.goals))
        if prjCrt.notes:
            xmlCrt.append(text_to_xml_element('Notes', prjCrt.notes))
        tagStr = list_to_string(prjCrt.tags)
        if tagStr:
            ET.SubElement(xmlCrt, 'Tags').text = tagStr
        if prjCrt.links:
            for path in prjCrt.links:
                xmlLink = ET.SubElement(xmlCrt, 'Link')
                xmlLink.set('path', path)
        if prjCrt.birthDate:
            ET.SubElement(xmlCrt, 'BirthDate').text = prjCrt.birthDate
        if prjCrt.deathDate:
            ET.SubElement(xmlCrt, 'DeathDate').text = prjCrt.deathDate

    def _build_element_tree(self, root):
        #--- Process project attributes.

        xmlProject = ET.SubElement(root, 'PROJECT')
        self._build_project_branch(xmlProject)

        #--- Process chapters and sections.
        xmlChapters = ET.SubElement(root, 'CHAPTERS')
        for chId in self.novel.tree.get_children(CH_ROOT):
            self._build_chapter_branch(xmlChapters, self.novel.chapters[chId], chId)

        #--- Process characters.
        xmlCharacters = ET.SubElement(root, 'CHARACTERS')
        for crId in self.novel.tree.get_children(CR_ROOT):
            xmlCrt = ET.SubElement(xmlCharacters, 'CHARACTER', attrib={'id':crId})
            self._build_character_branch(xmlCrt, self.novel.characters[crId])

        #--- Process locations.
        xmlLocations = ET.SubElement(root, 'LOCATIONS')
        for lcId in self.novel.tree.get_children(LC_ROOT):
            xmlLoc = ET.SubElement(xmlLocations, 'LOCATION', attrib={'id':lcId})
            self._build_location_branch(xmlLoc, self.novel.locations[lcId])

        #--- Process items.
        xmlItems = ET.SubElement(root, 'ITEMS')
        for itId in self.novel.tree.get_children(IT_ROOT):
            xmlItm = ET.SubElement(xmlItems, 'ITEM', attrib={'id':itId})
            self._build_item_branch(xmlItm, self.novel.items[itId])

        #--- Process plot lines and plot points.
        xmlPlotLines = ET.SubElement(root, 'ARCS')
        for plId in self.novel.tree.get_children(PL_ROOT):
            self._build_plot_line_branch(xmlPlotLines, self.novel.plotLines[plId], plId)

        #--- Process project notes.
        xmlProjectNotes = ET.SubElement(root, 'PROJECTNOTES')
        for pnId in self.novel.tree.get_children(PN_ROOT):
            xmlProjectNote = ET.SubElement(xmlProjectNotes, 'PROJECTNOTE', attrib={'id':pnId})
            self._build_project_notes_branch(xmlProjectNote, self.novel.projectNotes[pnId])

        #--- Build the word count log.
        if self.wcLog:
            xmlWcLog = ET.SubElement(root, 'PROGRESS')
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
                ET.SubElement(xmlWc, 'WithUnused').text = self.wcLog[wc][1]

    def _build_item_branch(self, xmlItm, prjItm):
        if prjItm.title:
            ET.SubElement(xmlItm, 'Title').text = prjItm.title
        if prjItm.aka:
            ET.SubElement(xmlItm, 'Aka').text = prjItm.aka
        if prjItm.desc:
            xmlItm.append(text_to_xml_element('Desc', prjItm.desc))
        tagStr = list_to_string(prjItm.tags)
        if tagStr:
            ET.SubElement(xmlItm, 'Tags').text = tagStr
        if prjItm.links:
            for path in prjItm.links:
                xmlLink = ET.SubElement(xmlItm, 'Link')
                xmlLink.set('path', path)

    def _build_location_branch(self, xmlLoc, prjLoc):
        if prjLoc.title:
            ET.SubElement(xmlLoc, 'Title').text = prjLoc.title
        if prjLoc.aka:
            ET.SubElement(xmlLoc, 'Aka').text = prjLoc.aka
        if prjLoc.desc:
            xmlLoc.append(text_to_xml_element('Desc', prjLoc.desc))
        tagStr = list_to_string(prjLoc.tags)
        if tagStr:
            ET.SubElement(xmlLoc, 'Tags').text = tagStr
        if prjLoc.links:
            for path in prjLoc.links:
                xmlLink = ET.SubElement(xmlLoc, 'Link')
                xmlLink.set('path', path)

    def _build_project_branch(self, xmlProject):
        if self.novel.renumberChapters:
            xmlProject.set('renumberChapters', '1')
        if self.novel.renumberParts:
            xmlProject.set('renumberParts', '1')
        if self.novel.renumberWithinParts:
            xmlProject.set('renumberWithinParts', '1')
        if self.novel.romanChapterNumbers:
            xmlProject.set('romanChapterNumbers', '1')
        if self.novel.romanPartNumbers:
            xmlProject.set('romanPartNumbers', '1')
        if self.novel.saveWordCount:
            xmlProject.set('saveWordCount', '1')
        if self.novel.workPhase is not None:
            xmlProject.set('workPhase', str(self.novel.workPhase))

        if self.novel.title:
            ET.SubElement(xmlProject, 'Title').text = self.novel.title
        if self.novel.authorName:
            ET.SubElement(xmlProject, 'Author').text = self.novel.authorName
        if self.novel.desc:
            xmlProject.append(text_to_xml_element('Desc', self.novel.desc))
        if self.novel.chapterHeadingPrefix:
            ET.SubElement(xmlProject, 'ChapterHeadingPrefix').text = self.novel.chapterHeadingPrefix
        if self.novel.chapterHeadingSuffix:
            ET.SubElement(xmlProject, 'ChapterHeadingSuffix').text = self.novel.chapterHeadingSuffix
        if self.novel.partHeadingPrefix:
            ET.SubElement(xmlProject, 'PartHeadingPrefix').text = self.novel.partHeadingPrefix
        if self.novel.partHeadingSuffix:
            ET.SubElement(xmlProject, 'PartHeadingSuffix').text = self.novel.partHeadingSuffix
        if self.novel.customGoal:
            ET.SubElement(xmlProject, 'CustomGoal').text = self.novel.customGoal
        if self.novel.customConflict:
            ET.SubElement(xmlProject, 'CustomConflict').text = self.novel.customConflict
        if self.novel.customOutcome:
            ET.SubElement(xmlProject, 'CustomOutcome').text = self.novel.customOutcome
        if self.novel.customChrBio:
            ET.SubElement(xmlProject, 'CustomChrBio').text = self.novel.customChrBio
        if self.novel.customChrGoals:
            ET.SubElement(xmlProject, 'CustomChrGoals').text = self.novel.customChrGoals
        if self.novel.wordCountStart:
            ET.SubElement(xmlProject, 'WordCountStart').text = str(self.novel.wordCountStart)
        if self.novel.wordTarget:
            ET.SubElement(xmlProject, 'WordTarget').text = str(self.novel.wordTarget)
        if self.novel.referenceDate:
            ET.SubElement(xmlProject, 'ReferenceDate').text = self.novel.referenceDate

    def _build_project_notes_branch(self, xmlProjectNote, projectNote):
        if projectNote.title:
            ET.SubElement(xmlProjectNote, 'Title').text = projectNote.title
        if projectNote.desc:
            xmlProjectNote.append(text_to_xml_element('Desc', projectNote.desc))

    def _build_section_branch(self, xmlSection, prjScn):
        if prjScn.scType:
            xmlSection.set('type', str(prjScn.scType))
        if prjScn.status > 1:
            xmlSection.set('status', str(prjScn.status))
        if prjScn.scPacing > 0:
            xmlSection.set('pacing', str(prjScn.scPacing))
        if prjScn.appendToPrev:
            xmlSection.set('append', '1')
        if prjScn.title:
            ET.SubElement(xmlSection, 'Title').text = prjScn.title
        if prjScn.desc:
            xmlSection.append(text_to_xml_element('Desc', prjScn.desc))
        if prjScn.goal:
            xmlSection.append(text_to_xml_element('Goal', prjScn.goal))
        if prjScn.conflict:
            xmlSection.append(text_to_xml_element('Conflict', prjScn.conflict))
        if prjScn.outcome:
            xmlSection.append(text_to_xml_element('Outcome', prjScn.outcome))
        if prjScn.plotNotes:
            xmlPlotNotes = ET.SubElement(xmlSection, 'PlotNotes')
            for plId in prjScn.plotNotes:
                if plId in prjScn.scPlotLines:
                    xmlPlotNote = text_to_xml_element('PlotlineNotes', prjScn.plotNotes[plId])
                    xmlPlotNote.set('id', plId)
                    xmlPlotNotes.append(xmlPlotNote)
        if prjScn.notes:
            xmlSection.append(text_to_xml_element('Notes', prjScn.notes))
        tagStr = list_to_string(prjScn.tags)
        if tagStr:
            ET.SubElement(xmlSection, 'Tags').text = tagStr

        #--- Date/Day and Time.
        if prjScn.date:
            ET.SubElement(xmlSection, 'Date').text = prjScn.date
        elif prjScn.day:
            ET.SubElement(xmlSection, 'Day').text = prjScn.day
        if prjScn.time:
            ET.SubElement(xmlSection, 'Time').text = prjScn.time

        #--- Duration.
        if prjScn.lastsDays and prjScn.lastsDays != '0':
            ET.SubElement(xmlSection, 'LastsDays').text = prjScn.lastsDays
        if prjScn.lastsHours and prjScn.lastsHours != '0':
            ET.SubElement(xmlSection, 'LastsHours').text = prjScn.lastsHours
        if prjScn.lastsMinutes and prjScn.lastsMinutes != '0':
            ET.SubElement(xmlSection, 'LastsMinutes').text = prjScn.lastsMinutes

        #--- References.
        if prjScn.characters:
            attrib = {'ids':' '.join(prjScn.characters)}
            ET.SubElement(xmlSection, 'Characters', attrib=attrib)
        if prjScn.locations:
            attrib = {'ids':' '.join(prjScn.locations)}
            ET.SubElement(xmlSection, 'Locations', attrib=attrib)
        if prjScn.items:
            attrib = {'ids':' '.join(prjScn.items)}
            ET.SubElement(xmlSection, 'Items', attrib=attrib)

        #--- Content.
        sectionContent = prjScn.sectionContent
        if sectionContent:
            if not sectionContent in ('<p></p>', '<p />'):
                xmlSection.append(ET.fromstring(f'<Content>{sectionContent}</Content>'))

    def _get_link_dict(self, parent):
        """Return a dictionary of links.
        
        If the element doesn't exist, return an empty dictionary.
        """
        links = {}
        for xmlLink in parent.iterfind('Link'):
            path = xmlLink.attrib.get('path', None)
            if path:
                links[path] = None
        return links

    def _postprocess_xml_file(self, filePath):
        """Postprocess an xml file created by ElementTree.
        
        Positional argument:
            filePath: str -- path to xml file.
        
        Read the xml file, put a header on top and fix double-escaped text. 
        Overwrite the .novx xml file.
        Raise the "Error" exception in case of error. 
        
        Note: The path is given as an argument rather than using self.filePath. 
        So this routine can be used for novelibre-generated xml files other than .novx as well. 
        """
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        # text = unescape(text)
        # this is because section content PCDATA is "double escaped"
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(f'{self.XML_HEADER}{text}')
        except:
            raise Error(f'{_("Cannot write file")}: "{norm_path(filePath)}".')

    def _read_plot_lines(self, root):
        """Read plotlines from the xml element tree."""
        try:
            for xmlPlotLine in root.find('ARCS'):
                plId = xmlPlotLine.attrib['id']
                self.novel.plotLines[plId] = PlotLine(on_element_change=self.on_element_change)
                self.novel.plotLines[plId].title = get_element_text(xmlPlotLine, 'Title')
                self.novel.plotLines[plId].desc = xml_element_to_text(xmlPlotLine.find('Desc'))
                self.novel.plotLines[plId].shortName = get_element_text(xmlPlotLine, 'ShortName')
                self.novel.tree.append(PL_ROOT, plId)
                for xmlPlotPoint in xmlPlotLine.iterfind('POINT'):
                    ppId = xmlPlotPoint.attrib['id']
                    self._read_plot_point(xmlPlotPoint, ppId, plId)
                    self.novel.tree.append(plId, ppId)

                #--- References
                acSections = []
                xmlSections = xmlPlotLine.find('Sections')
                if xmlSections is not None:
                    scIds = xmlSections.get('ids', None)
                    for scId in string_to_list(scIds, divider=' '):
                        if scId and scId in self.novel.sections:
                            acSections.append(scId)
                            self.novel.sections[scId].scPlotLines.append(plId)
                self.novel.plotLines[plId].sections = acSections
        except TypeError:
            pass

    def _read_plot_point(self, xmlPoint, ppId, plId):
        """Read a plot point from the xml element tree."""
        self.novel.plotPoints[ppId] = PlotPoint(on_element_change=self.on_element_change)
        self.novel.plotPoints[ppId].title = get_element_text(xmlPoint, 'Title')
        self.novel.plotPoints[ppId].desc = xml_element_to_text(xmlPoint.find('Desc'))
        self.novel.plotPoints[ppId].notes = xml_element_to_text(xmlPoint.find('Notes'))
        xmlSectionAssoc = xmlPoint.find('Section')
        if xmlSectionAssoc is not None:
            scId = xmlSectionAssoc.get('id', None)
            self.novel.plotPoints[ppId].sectionAssoc = scId
            self.novel.sections[scId].scPlotPoints[ppId] = plId

    def _read_chapters(self, root, partType=0):
        """Read data at chapter level from the xml element tree."""
        try:
            for xmlChapter in root.find('CHAPTERS'):
                chId = xmlChapter.attrib['id']
                self.novel.chapters[chId] = Chapter(on_element_change=self.on_element_change)
                typeStr = xmlChapter.get('type', '0')
                if typeStr in ('0', '1'):
                    self.novel.chapters[chId].chType = int(typeStr)
                else:
                    self.novel.chapters[chId].chType = 1
                chLevel = xmlChapter.get('level', None)
                if chLevel == '1':
                    self.novel.chapters[chId].chLevel = 1
                else:
                    self.novel.chapters[chId].chLevel = 2
                self.novel.chapters[chId].isTrash = xmlChapter.get('isTrash', None) == '1'
                self.novel.chapters[chId].noNumber = xmlChapter.get('noNumber', None) == '1'
                self.novel.chapters[chId].title = get_element_text(xmlChapter, 'Title')
                self.novel.chapters[chId].desc = xml_element_to_text(xmlChapter.find('Desc'))
                self.novel.tree.append(CH_ROOT, chId)
                if xmlChapter.find('SECTION'):
                    for xmlSection in xmlChapter.iterfind('SECTION'):
                        scId = xmlSection.attrib['id']
                        self._read_section(xmlSection, scId)
                        if self.novel.sections[scId].scType < self.novel.chapters[chId].chType:
                            self.novel.sections[scId].scType = self.novel.chapters[chId].chType
                        self.novel.tree.append(chId, scId)
        except TypeError:
            pass

    def _read_characters(self, root):
        """Read characters from the xml element tree."""
        try:
            for xmlCharacter in root.find('CHARACTERS'):
                crId = xmlCharacter.attrib['id']
                self.novel.characters[crId] = Character(on_element_change=self.on_element_change)
                self.novel.characters[crId].isMajor = xmlCharacter.get('major', None) == '1'
                self.novel.characters[crId].title = get_element_text(xmlCharacter, 'Title')
                self.novel.characters[crId].links = self._get_link_dict(xmlCharacter)
                self.novel.characters[crId].desc = xml_element_to_text(xmlCharacter.find('Desc'))
                self.novel.characters[crId].aka = get_element_text(xmlCharacter, 'Aka')
                tags = string_to_list(get_element_text(xmlCharacter, 'Tags'))
                self.novel.characters[crId].tags = self._strip_spaces(tags)
                self.novel.characters[crId].notes = xml_element_to_text(xmlCharacter.find('Notes'))
                self.novel.characters[crId].bio = xml_element_to_text(xmlCharacter.find('Bio'))
                self.novel.characters[crId].goals = xml_element_to_text(xmlCharacter.find('Goals'))
                self.novel.characters[crId].fullName = get_element_text(xmlCharacter, 'FullName')
                self.novel.characters[crId].birthDate = get_element_text(xmlCharacter, 'BirthDate')
                self.novel.characters[crId].deathDate = get_element_text(xmlCharacter, 'DeathDate')
                self.novel.tree.append(CR_ROOT, crId)
        except TypeError:
            pass

    def _read_items(self, root):
        """Read items from the xml element tree."""
        try:
            for xmlItem in root.find('ITEMS'):
                itId = xmlItem.attrib['id']
                self.novel.items[itId] = WorldElement(on_element_change=self.on_element_change)
                self.novel.items[itId].title = get_element_text(xmlItem, 'Title')
                self.novel.items[itId].desc = xml_element_to_text(xmlItem.find('Desc'))
                self.novel.items[itId].aka = get_element_text(xmlItem, 'Aka')
                tags = string_to_list(get_element_text(xmlItem, 'Tags'))
                self.novel.items[itId].tags = self._strip_spaces(tags)
                self.novel.items[itId].links = self._get_link_dict(xmlItem)
                self.novel.tree.append(IT_ROOT, itId)
        except TypeError:
            pass

    def _read_locations(self, root):
        """Read locations from the xml element tree."""
        try:
            for xmlLocation in root.find('LOCATIONS'):
                lcId = xmlLocation.attrib['id']
                self.novel.locations[lcId] = WorldElement(on_element_change=self.on_element_change)
                self.novel.locations[lcId].title = get_element_text(xmlLocation, 'Title')
                self.novel.locations[lcId].links = self._get_link_dict(xmlLocation)
                self.novel.locations[lcId].desc = xml_element_to_text(xmlLocation.find('Desc'))
                self.novel.locations[lcId].aka = get_element_text(xmlLocation, 'Aka')
                tags = string_to_list(get_element_text(xmlLocation, 'Tags'))
                self.novel.locations[lcId].tags = self._strip_spaces(tags)
                self.novel.tree.append(LC_ROOT, lcId)
        except TypeError:
            pass

    def _read_project(self, root):
        """Read data at project level from the xml element tree."""
        xmlProject = root.find('PROJECT')
        self.novel.renumberChapters = xmlProject.get('renumberChapters', None) == '1'
        self.novel.renumberParts = xmlProject.get('renumberParts', None) == '1'
        self.novel.renumberWithinParts = xmlProject.get('renumberWithinParts', None) == '1'
        self.novel.romanChapterNumbers = xmlProject.get('romanChapterNumbers', None) == '1'
        self.novel.romanPartNumbers = xmlProject.get('romanPartNumbers', None) == '1'
        self.novel.saveWordCount = xmlProject.get('saveWordCount', None) == '1'
        workPhase = xmlProject.get('workPhase', None)
        if workPhase in ('1', '2', '3', '4', '5'):
            self.novel.workPhase = int(workPhase)
        else:
            self.novel.workPhase = None
        self.novel.title = get_element_text(xmlProject, 'Title')
        self.novel.authorName = get_element_text(xmlProject, 'Author')
        self.novel.desc = xml_element_to_text(xmlProject.find('Desc'))
        self.novel.chapterHeadingPrefix = get_element_text(xmlProject, 'ChapterHeadingPrefix')
        self.novel.chapterHeadingSuffix = get_element_text(xmlProject, 'ChapterHeadingSuffix')
        self.novel.partHeadingPrefix = get_element_text(xmlProject, 'PartHeadingPrefix')
        self.novel.partHeadingSuffix = get_element_text(xmlProject, 'PartHeadingSuffix')
        self.novel.customGoal = get_element_text(xmlProject, 'CustomGoal')
        self.novel.customConflict = get_element_text(xmlProject, 'CustomConflict')
        self.novel.customOutcome = get_element_text(xmlProject, 'CustomOutcome')
        self.novel.customChrBio = get_element_text(xmlProject, 'CustomChrBio')
        self.novel.customChrGoals = get_element_text(xmlProject, 'CustomChrGoals')
        if xmlProject.find('WordCountStart') is not None:
            self.novel.wordCountStart = int(xmlProject.find('WordCountStart').text)
        if xmlProject.find('WordTarget') is not None:
            self.novel.wordTarget = int(xmlProject.find('WordTarget').text)
        self.novel.referenceDate = get_element_text(xmlProject, 'ReferenceDate')

    def _read_project_notes(self, root):
        """Read project notes from the xml element tree."""
        try:
            for xmlProjectNote in root.find('PROJECTNOTES'):
                pnId = xmlProjectNote.attrib['id']
                self.novel.projectNotes[pnId] = BasicElement()
                self.novel.projectNotes[pnId].title = get_element_text(xmlProjectNote, 'Title')
                self.novel.projectNotes[pnId].desc = xml_element_to_text(xmlProjectNote.find('Desc'))
                self.novel.tree.append(PN_ROOT, pnId)
        except TypeError:
            pass

    def _read_section(self, xmlSection, scId):
        """Read data at section level from the xml element tree."""
        self.novel.sections[scId] = Section(on_element_change=self.on_element_change)
        typeStr = xmlSection.get('type', '0')
        if typeStr in ('0', '1', '2', '3'):
            self.novel.sections[scId].scType = int(typeStr)
        else:
            self.novel.sections[scId].scType = 1
        status = xmlSection.get('status', None)
        if status in ('2', '3', '4', '5'):
            self.novel.sections[scId].status = int(status)
        else:
            self.novel.sections[scId].status = 1
        scPacing = xmlSection.get('pacing', 0)
        if scPacing in ('1', '2'):
            self.novel.sections[scId].scPacing = int(scPacing)
        else:
            self.novel.sections[scId].scPacing = 0
        self.novel.sections[scId].appendToPrev = xmlSection.get('append', None) == '1'
        self.novel.sections[scId].title = get_element_text(xmlSection, 'Title')
        self.novel.sections[scId].desc = xml_element_to_text(xmlSection.find('Desc'))

        #--- Read content.
        if xmlSection.find('Content'):
            xmlStr = ET.tostring(xmlSection.find('Content'),
                                 encoding='utf-8',
                                 short_empty_elements=False
                                 ).decode('utf-8')
            xmlStr = xmlStr.replace('<Content>', '').replace('</Content>', '')

            # Remove indentiation, if any.
            lines = xmlStr.split('\n')
            newlines = []
            for line in lines:
                newlines.append(line.strip())
            xmlStr = ''.join(newlines)
            if xmlStr:
                self.novel.sections[scId].sectionContent = xmlStr
            else:
                self.novel.sections[scId].sectionContent = '<p></p>'
        else:
            self.novel.sections[scId].sectionContent = '<p></p>'

        #--- Read notes
        self.novel.sections[scId].notes = xml_element_to_text(xmlSection.find('Notes'))

        #--- Read tags
        tags = string_to_list(get_element_text(xmlSection, 'Tags'))
        self.novel.sections[scId].tags = self._strip_spaces(tags)

        #--- Read date/time.
        if xmlSection.find('Date') is not None:
            dateStr = xmlSection.find('Date').text
            try:
                date.fromisoformat(dateStr)
            except:
                self.novel.sections[scId].date = None
            else:
                self.novel.sections[scId].date = dateStr
        elif xmlSection.find('Day') is not None:
            dayStr = xmlSection.find('Day').text
            try:
                int(dayStr)
            except ValueError:
                self.novel.sections[scId].day = None
            else:
                self.novel.sections[scId].day = dayStr

        if xmlSection.find('Time') is not None:
            timeStr = xmlSection.find('Time').text
            try:
                time.fromisoformat(timeStr)
            except:
                self.novel.sections[scId].time = None
            else:
                self.novel.sections[scId].time = timeStr

        #--- Section duration.
        self.novel.sections[scId].lastsDays = get_element_text(xmlSection, 'LastsDays')
        self.novel.sections[scId].lastsHours = get_element_text(xmlSection, 'LastsHours')
        self.novel.sections[scId].lastsMinutes = get_element_text(xmlSection, 'LastsMinutes')

        #--- Goal/Conflict/outcome.
        self.novel.sections[scId].goal = xml_element_to_text(xmlSection.find('Goal'))
        self.novel.sections[scId].conflict = xml_element_to_text(xmlSection.find('Conflict'))
        self.novel.sections[scId].outcome = xml_element_to_text(xmlSection.find('Outcome'))

        #--- Plot notes.
        xmlPlotNotes = xmlSection.find('PlotNotes')
        if xmlPlotNotes is not None:
            plotNotes = {}
            for xmlPlotLineNote in xmlPlotNotes.iterfind('PlotlineNotes'):
                plId = xmlPlotLineNote.get('id', None)
                plotNotes[plId] = xml_element_to_text(xmlPlotLineNote)
            self.novel.sections[scId].plotNotes = plotNotes

        #--- References
        scCharacters = []
        xmlCharacters = xmlSection.find('Characters')
        if xmlCharacters is not None:
            crIds = xmlCharacters.get('ids', None)
            for crId in string_to_list(crIds, divider=' '):
                if crId and crId in self.novel.characters:
                    scCharacters.append(crId)
        self.novel.sections[scId].characters = scCharacters

        scLocations = []
        xmlLocations = xmlSection.find('Locations')
        if xmlLocations is not None:
            lcIds = xmlLocations.get('ids', None)
            for lcId in string_to_list(lcIds, divider=' '):
                if lcId and lcId in self.novel.locations:
                    scLocations.append(lcId)
        self.novel.sections[scId].locations = scLocations

        scItems = []
        xmlItems = xmlSection.find('Items')
        if xmlItems is not None:
            itIds = xmlItems.get('ids', None)
            for itId in string_to_list(itIds, divider=' '):
                if itId and itId in self.novel.items:
                    scItems.append(itId)
        self.novel.sections[scId].items = scItems

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

    def _write_element_tree(self, xmlProject):
        """Write back the xml element tree to a .novx xml file located at filePath.
        
        Raise the "Error" exception in case of error. 
        """
        backedUp = False
        if os.path.isfile(xmlProject.filePath):
            try:
                os.replace(xmlProject.filePath, f'{xmlProject.filePath}.bak')
            except:
                raise Error(f'{_("Cannot overwrite file")}: "{norm_path(xmlProject.filePath)}".')
            else:
                backedUp = True
        try:
            xmlProject.xmlTree.write(xmlProject.filePath, xml_declaration=False, encoding='utf-8')
        except Error:
            if backedUp:
                os.replace(f'{xmlProject.filePath}.bak', xmlProject.filePath)
            raise Error(f'{_("Cannot write file")}: "{norm_path(xmlProject.filePath)}".')

