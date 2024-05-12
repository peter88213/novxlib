"""Provide a class for novx file import and export.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from datetime import date
from datetime import time
import os

from novxlib.file.file import File
from novxlib.model.basic_element import BasicElement
from novxlib.model.chapter import Chapter
from novxlib.model.character import Character
from novxlib.model.plot_line import PlotLine
from novxlib.model.plot_point import PlotPoint
from novxlib.model.section import Section
from novxlib.model.world_element import WorldElement
from novxlib.novx_globals import CH_ROOT
from novxlib.novx_globals import CR_ROOT
from novxlib.novx_globals import Error
from novxlib.novx_globals import IT_ROOT
from novxlib.novx_globals import LC_ROOT
from novxlib.novx_globals import PL_ROOT
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
    MINOR_VERSION = 3
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

        # Read the word count log.
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
        self._build_project(xmlRoot)
        self._build_chapters_and_sections(xmlRoot)
        self._build_characters(xmlRoot)
        self._build_locations(xmlRoot)
        self._build_items(xmlRoot)
        self._build_plot_lines_and_points(xmlRoot)
        self._build_project_notes(xmlRoot)
        self._build_word_count_log(xmlRoot)

        indent(xmlRoot)
        # CAUTION: make sure not to indent inline elements within paragraphs

        self.xmlTree = ET.ElementTree(xmlRoot)
        self._write_element_tree(self)
        self._postprocess_xml_file(self.filePath)

    def _build_chapter_branch(self, xmlChapters, prjChp, chId):
        xmlChapter = ET.SubElement(xmlChapters, 'CHAPTER', attrib={'id':chId})

        #--- Attributes.
        if prjChp.chType:
            xmlChapter.set('type', str(prjChp.chType))
        if prjChp.chLevel == 1:
            xmlChapter.set('level', '1')
        if prjChp.isTrash:
            xmlChapter.set('isTrash', '1')
        if prjChp.noNumber:
            xmlChapter.set('noNumber', '1')

        #--- Inherited properties.
        self._set_base_data(xmlChapter, prjChp)
        self._set_notes(xmlChapter, prjChp)

        #--- Section branch.
        for scId in self.novel.tree.get_children(chId):
            xmlSection = ET.SubElement(xmlChapter, 'SECTION', attrib={'id':scId})
            self._build_section_branch(xmlSection, self.novel.sections[scId])

    def _build_project(self, root):
        xmlProject = ET.SubElement(root, 'PROJECT')
        self._build_project_branch(xmlProject)

    def _build_chapters_and_sections(self, root):
        xmlChapters = ET.SubElement(root, 'CHAPTERS')
        for chId in self.novel.tree.get_children(CH_ROOT):
            self._build_chapter_branch(xmlChapters, self.novel.chapters[chId], chId)

    def _build_characters(self, root):
        xmlCharacters = ET.SubElement(root, 'CHARACTERS')
        for crId in self.novel.tree.get_children(CR_ROOT):
            self.novel.characters[crId].write_xml(ET.SubElement(xmlCharacters, 'CHARACTER', attrib={'id':crId}))

    def _build_locations(self, root):
        xmlLocations = ET.SubElement(root, 'LOCATIONS')
        for lcId in self.novel.tree.get_children(LC_ROOT):
            self.novel.locations[lcId].write_xml(ET.SubElement(xmlLocations, 'LOCATION', attrib={'id':lcId}))

    def _build_items(self, root):
        xmlItems = ET.SubElement(root, 'ITEMS')
        for itId in self.novel.tree.get_children(IT_ROOT):
            self.novel.items[itId].write_xml(ET.SubElement(xmlItems, 'ITEM', attrib={'id':itId}))

    def _build_plot_lines_and_points(self, root):
        xmlPlotLines = ET.SubElement(root, 'ARCS')
        for plId in self.novel.tree.get_children(PL_ROOT):
            xmlPlotLine = ET.SubElement(xmlPlotLines, 'ARC', attrib={'id':plId})
            self.novel.plotLines[plId].write_xml(xmlPlotLine)
            for ppId in self.novel.tree.get_children(plId):
                xmlPlotPoint = ET.SubElement(xmlPlotLine, 'POINT', attrib={'id':ppId})
                self.novel.plotPoints[ppId].write_xml(xmlPlotPoint)

    def _build_project_notes(self, root):
        xmlProjectNotes = ET.SubElement(root, 'PROJECTNOTES')
        for pnId in self.novel.tree.get_children(PN_ROOT):
            self.novel.projectNotes[pnId].write_xml(ET.SubElement(xmlProjectNotes, 'PROJECTNOTE', attrib={'id':pnId}))

    def _build_project_branch(self, xmlProject):

        #--- Attributes.
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

        #--- Inherited properties.
        self._set_base_data(xmlProject, self.novel)

        #--- Author.
        if self.novel.authorName:
            ET.SubElement(xmlProject, 'Author').text = self.novel.authorName

        #--- Chapter heading prefix/suffix.
        if self.novel.chapterHeadingPrefix:
            ET.SubElement(xmlProject, 'ChapterHeadingPrefix').text = self.novel.chapterHeadingPrefix
        if self.novel.chapterHeadingSuffix:
            ET.SubElement(xmlProject, 'ChapterHeadingSuffix').text = self.novel.chapterHeadingSuffix

        #--- Part heading prefix/suffix.
        if self.novel.partHeadingPrefix:
            ET.SubElement(xmlProject, 'PartHeadingPrefix').text = self.novel.partHeadingPrefix
        if self.novel.partHeadingSuffix:
            ET.SubElement(xmlProject, 'PartHeadingSuffix').text = self.novel.partHeadingSuffix

        #--- Custom Goal/Conflict/Outcome.
        if self.novel.customGoal:
            ET.SubElement(xmlProject, 'CustomGoal').text = self.novel.customGoal
        if self.novel.customConflict:
            ET.SubElement(xmlProject, 'CustomConflict').text = self.novel.customConflict
        if self.novel.customOutcome:
            ET.SubElement(xmlProject, 'CustomOutcome').text = self.novel.customOutcome

        #--- Custom Character Bio/Goals.
        if self.novel.customChrBio:
            ET.SubElement(xmlProject, 'CustomChrBio').text = self.novel.customChrBio
        if self.novel.customChrGoals:
            ET.SubElement(xmlProject, 'CustomChrGoals').text = self.novel.customChrGoals

        #--- Word count start/Word target.
        if self.novel.wordCountStart:
            ET.SubElement(xmlProject, 'WordCountStart').text = str(self.novel.wordCountStart)
        if self.novel.wordTarget:
            ET.SubElement(xmlProject, 'WordTarget').text = str(self.novel.wordTarget)

        #--- Reference date.
        if self.novel.referenceDate:
            ET.SubElement(xmlProject, 'ReferenceDate').text = self.novel.referenceDate

    def _build_section_branch(self, xmlSection, prjScn):

        #--- Attributes.
        if prjScn.scType:
            xmlSection.set('type', str(prjScn.scType))
        if prjScn.status > 1:
            xmlSection.set('status', str(prjScn.status))
        if prjScn.scPacing > 0:
            xmlSection.set('pacing', str(prjScn.scPacing))
        if prjScn.appendToPrev:
            xmlSection.set('append', '1')

        #--- Inherited properties.
        self._set_base_data(xmlSection, prjScn)
        self._set_notes(xmlSection, prjScn)
        self._set_tags(xmlSection, prjScn)

        #--- Goal/Conflict/Outcome.
        if prjScn.goal:
            xmlSection.append(text_to_xml_element('Goal', prjScn.goal))
        if prjScn.conflict:
            xmlSection.append(text_to_xml_element('Conflict', prjScn.conflict))
        if prjScn.outcome:
            xmlSection.append(text_to_xml_element('Outcome', prjScn.outcome))

        #--- Plot notes.
        if prjScn.plotNotes:
            xmlPlotNotes = ET.SubElement(xmlSection, 'PlotNotes')
            for plId in prjScn.plotNotes:
                if plId in prjScn.scPlotLines:
                    xmlPlotNote = text_to_xml_element('PlotlineNotes', prjScn.plotNotes[plId])
                    xmlPlotNote.set('id', plId)
                    xmlPlotNotes.append(xmlPlotNote)

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

        #--- Characters references.
        if prjScn.characters:
            attrib = {'ids':' '.join(prjScn.characters)}
            ET.SubElement(xmlSection, 'Characters', attrib=attrib)

        #--- Locations references.
        if prjScn.locations:
            attrib = {'ids':' '.join(prjScn.locations)}
            ET.SubElement(xmlSection, 'Locations', attrib=attrib)

        #--- Items references.
        if prjScn.items:
            attrib = {'ids':' '.join(prjScn.items)}
            ET.SubElement(xmlSection, 'Items', attrib=attrib)

        #--- Content.
        sectionContent = prjScn.sectionContent
        if sectionContent:
            if not sectionContent in ('<p></p>', '<p />'):
                xmlSection.append(ET.fromstring(f'<Content>{sectionContent}</Content>'))

    def _build_word_count_log(self, root):
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

    def _get_base_data(self, xmlElement, prjElement):
        prjElement.title = get_element_text(xmlElement, 'Title')
        prjElement.desc = xml_element_to_text(xmlElement.find('Desc'))
        prjElement.links = self._get_link_dict(xmlElement)

    def _get_link_dict(self, parent):
        """Return a dictionary of links.
        
        If the element doesn't exist, return an empty dictionary.
        """
        links = {}
        for xmlLink in parent.iterfind('Link'):
            path = xmlLink.attrib.get('path', None)
            fullPath = xmlLink.attrib.get('fullPath', None)
            if path:
                links[path] = fullPath
        return links

    def _get_notes(self, xmlElement, prjElement):
        prjElement.notes = xml_element_to_text(xmlElement.find('Notes'))

    def _get_tags(self, xmlElement, prjElement):
        tags = string_to_list(get_element_text(xmlElement, 'Tags'))
        prjElement.tags = self._strip_spaces(tags)

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

    def _read_chapters(self, root):
        """Read data at chapter level from the xml element tree."""
        try:
            for xmlChapter in root.find('CHAPTERS'):

                #--- Attributes.
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

                #--- Inherited properties.
                self._get_base_data(xmlChapter, self.novel.chapters[chId])
                self._get_notes(xmlChapter, self.novel.chapters[chId])

                #--- Section branch.
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
                self.novel.characters[crId].read_xml(xmlCharacter)
                self.novel.tree.append(CR_ROOT, crId)
        except TypeError:
            pass

    def _read_items(self, root):
        """Read items from the xml element tree."""
        try:
            for xmlItem in root.find('ITEMS'):
                itId = xmlItem.attrib['id']
                self.novel.items[itId] = WorldElement(on_element_change=self.on_element_change)
                self.novel.items[itId].read_xml(xmlItem)
                self.novel.tree.append(IT_ROOT, itId)
        except TypeError:
            pass

    def _read_locations(self, root):
        """Read locations from the xml element tree."""
        try:
            for xmlLocation in root.find('LOCATIONS'):
                lcId = xmlLocation.attrib['id']
                self.novel.locations[lcId] = WorldElement(on_element_change=self.on_element_change)
                self.novel.locations[lcId].read_xml(xmlLocation)
                self.novel.tree.append(LC_ROOT, lcId)
        except TypeError:
            pass

    def _read_plot_lines(self, root):
        """Read plotlines from the xml element tree."""
        try:
            for xmlPlotLine in root.find('ARCS'):
                plId = xmlPlotLine.attrib['id']
                self.novel.plotLines[plId] = PlotLine(on_element_change=self.on_element_change)
                self.novel.plotLines[plId].read_xml(xmlPlotLine)

                # Verify sections and create backlinks.
                plSections = []
                for scId in self.novel.plotLines[plId].sections:
                    if scId in self.novel.sections:
                        self.novel.sections[scId].scPlotLines.append(plId)
                        plSections.append(scId)
                self.novel.plotLines[plId].sections = plSections

                # Plot points.
                self.novel.tree.append(PL_ROOT, plId)
                for xmlPlotPoint in xmlPlotLine.iterfind('POINT'):
                    ppId = xmlPlotPoint.attrib['id']
                    self._read_plot_point(xmlPlotPoint, ppId, plId)
                    self.novel.tree.append(plId, ppId)

        except TypeError:
            pass

    def _read_plot_point(self, xmlPlotPoint, ppId, plId):
        """Read a plot point from the xml element tree."""
        self.novel.plotPoints[ppId] = PlotPoint(on_element_change=self.on_element_change)
        self.novel.plotPoints[ppId].read_xml(xmlPlotPoint)

        # Verify section and create backlink.
        scId = self.novel.plotPoints[ppId].sectionAssoc
        if scId in self.novel.sections:
            self.novel.sections[scId].scPlotPoints[ppId] = plId
        else:
            self.novel.plotPoints[ppId].sectionAssoc = None

    def _read_project(self, root):
        """Read data at project level from the xml element tree."""
        xmlProject = root.find('PROJECT')

        #--- Attributes.
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

        #--- Inherited properties.
        self._get_base_data(xmlProject, self.novel)

        #--- Author.
        self.novel.authorName = get_element_text(xmlProject, 'Author')

        #--- Chapter heading prefix/suffix.
        self.novel.chapterHeadingPrefix = get_element_text(xmlProject, 'ChapterHeadingPrefix')
        self.novel.chapterHeadingSuffix = get_element_text(xmlProject, 'ChapterHeadingSuffix')

        #--- Part heading prefix/suffix.
        self.novel.partHeadingPrefix = get_element_text(xmlProject, 'PartHeadingPrefix')
        self.novel.partHeadingSuffix = get_element_text(xmlProject, 'PartHeadingSuffix')

        #--- Custom Goal/Conflict/Outcome.
        self.novel.customGoal = get_element_text(xmlProject, 'CustomGoal')
        self.novel.customConflict = get_element_text(xmlProject, 'CustomConflict')
        self.novel.customOutcome = get_element_text(xmlProject, 'CustomOutcome')

        #--- Custom Character Bio/Goals.
        self.novel.customChrBio = get_element_text(xmlProject, 'CustomChrBio')
        self.novel.customChrGoals = get_element_text(xmlProject, 'CustomChrGoals')

        #--- Word count start/Word target.
        if xmlProject.find('WordCountStart') is not None:
            self.novel.wordCountStart = int(xmlProject.find('WordCountStart').text)
        if xmlProject.find('WordTarget') is not None:
            self.novel.wordTarget = int(xmlProject.find('WordTarget').text)

        #--- Reference date.
        self.novel.referenceDate = get_element_text(xmlProject, 'ReferenceDate')

    def _read_project_notes(self, root):
        """Read project notes from the xml element tree."""
        try:
            for xmlProjectNote in root.find('PROJECTNOTES'):
                pnId = xmlProjectNote.attrib['id']
                self.novel.projectNotes[pnId] = BasicElement()
                self.novel.projectNotes[pnId].read_xml(xmlProjectNote)
                self.novel.tree.append(PN_ROOT, pnId)
        except TypeError:
            pass

    def _read_section(self, xmlSection, scId):
        """Read data at section level from the xml element tree."""
        self.novel.sections[scId] = Section(on_element_change=self.on_element_change)

        #--- Attributes.
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

        #--- Inherited properties.
        self._get_base_data(xmlSection, self.novel.sections[scId])
        self._get_notes(xmlSection, self.novel.sections[scId])
        self._get_tags(xmlSection, self.novel.sections[scId])

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

        #--- Date/Day and Time.
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

        #--- Duration.
        self.novel.sections[scId].lastsDays = get_element_text(xmlSection, 'LastsDays')
        self.novel.sections[scId].lastsHours = get_element_text(xmlSection, 'LastsHours')
        self.novel.sections[scId].lastsMinutes = get_element_text(xmlSection, 'LastsMinutes')

        #--- Characters references.
        scCharacters = []
        xmlCharacters = xmlSection.find('Characters')
        if xmlCharacters is not None:
            crIds = xmlCharacters.get('ids', None)
            for crId in string_to_list(crIds, divider=' '):
                if crId and crId in self.novel.characters:
                    scCharacters.append(crId)
        self.novel.sections[scId].characters = scCharacters

        #--- Locations references.
        scLocations = []
        xmlLocations = xmlSection.find('Locations')
        if xmlLocations is not None:
            lcIds = xmlLocations.get('ids', None)
            for lcId in string_to_list(lcIds, divider=' '):
                if lcId and lcId in self.novel.locations:
                    scLocations.append(lcId)
        self.novel.sections[scId].locations = scLocations

        #--- Items references.
        scItems = []
        xmlItems = xmlSection.find('Items')
        if xmlItems is not None:
            itIds = xmlItems.get('ids', None)
            for itId in string_to_list(itIds, divider=' '):
                if itId and itId in self.novel.items:
                    scItems.append(itId)
        self.novel.sections[scId].items = scItems

        #--- Content.
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

    def _set_aka(self, xmlElement, prjElement):
        if prjElement.aka:
            ET.SubElement(xmlElement, 'Aka').text = prjElement.aka

    def _set_base_data(self, xmlElement, prjElement):
        if prjElement.title:
            ET.SubElement(xmlElement, 'Title').text = prjElement.title
        if prjElement.desc:
            xmlElement.append(text_to_xml_element('Desc', prjElement.desc))
        if prjElement.links:
            for path in prjElement.links:
                xmlLink = ET.SubElement(xmlElement, 'Link')
                xmlLink.set('path', path)
                if prjElement.links[path]:
                    xmlLink.set('fullPath', prjElement.links[path])

    def _set_notes(self, xmlElement, prjElement):
        if prjElement.notes:
            xmlElement.append(text_to_xml_element('Notes', prjElement.notes))

    def _set_tags(self, xmlElement, prjElement):
        tagStr = list_to_string(prjElement.tags)
        if tagStr:
            ET.SubElement(xmlElement, 'Tags').text = tagStr

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
        
        If a novx file already exists, rename it for backup.
        If writing the file fails, restore the backup copy, if any.
        
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

