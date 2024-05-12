"""Provide a class for novx file import and export.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from datetime import date
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
from novxlib.novx_globals import norm_path
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
        self._read_chapters_and_sections(xmlRoot)
        self._read_plot_lines_and_points(xmlRoot)
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

    def _build_project(self, root):
        xmlProject = ET.SubElement(root, 'PROJECT')
        self._build_project_branch(xmlProject)

    def _build_chapters_and_sections(self, root):
        xmlChapters = ET.SubElement(root, 'CHAPTERS')
        for chId in self.novel.tree.get_children(CH_ROOT):
            xmlChapter = ET.SubElement(xmlChapters, 'CHAPTER', attrib={'id':chId})
            self.novel.chapters[chId].write_xml(xmlChapter)
            for scId in self.novel.tree.get_children(chId):
                self.novel.sections[scId].write_xml(ET.SubElement(xmlChapter, 'SECTION', attrib={'id':scId}))

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
                self.novel.plotPoints[ppId].write_xml(ET.SubElement(xmlPlotLine, 'POINT', attrib={'id':ppId}))

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

    def _read_chapters_and_sections(self, root):
        """Read data at chapter level from the xml element tree."""
        try:
            for xmlChapter in root.find('CHAPTERS'):
                chId = xmlChapter.attrib['id']
                self.novel.chapters[chId] = Chapter(on_element_change=self.on_element_change)
                self.novel.chapters[chId].read_xml(xmlChapter)
                self.novel.tree.append(CH_ROOT, chId)

                # Sections.
                for xmlSection in xmlChapter.iterfind('SECTION'):
                    scId = xmlSection.attrib['id']
                    self._read_section(xmlSection, scId)
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

    def _read_plot_lines_and_points(self, root):
        """Read plotlines from the xml element tree."""
        try:
            for xmlPlotLine in root.find('ARCS'):
                plId = xmlPlotLine.attrib['id']
                self.novel.plotLines[plId] = PlotLine(on_element_change=self.on_element_change)
                self.novel.plotLines[plId].read_xml(xmlPlotLine)
                self.novel.tree.append(PL_ROOT, plId)

                # Verify sections and create backlinks.
                plSections = []
                for scId in self.novel.plotLines[plId].sections:
                    if scId in self.novel.sections:
                        self.novel.sections[scId].scPlotLines.append(plId)
                        plSections.append(scId)
                self.novel.plotLines[plId].sections = plSections

                # Plot points.
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
        self.novel.sections[scId].read_xml(xmlSection)

        # Verify characters.
        scCharacters = []
        for crId in self.novel.sections[scId].characters:
            if crId in self.novel.characters:
                scCharacters.append(crId)
        self.novel.sections[scId].characters = scCharacters

        # Verify locations.
        scLocations = []
        for lcId in self.novel.sections[scId].locations:
            if lcId in self.novel.locations:
                scLocations.append(lcId)
        self.novel.sections[scId].locations = scLocations

        # Verify items.
        scItems = []
        for itId in self.novel.sections[scId].items:
            if itId in self.novel.items:
                scItems.append(itId)
        self.novel.sections[scId].items = scItems

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

