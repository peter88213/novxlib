"""Provide a generic class for template-based file export.

All file representations with template-based write methods inherit from this class.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import os
from string import Template

from novxlib.file.file import File
from novxlib.file.filter import Filter
from novxlib.model.character import Character
from novxlib.model.section import Section
from novxlib.novx_globals import AC_ROOT
from novxlib.novx_globals import CHARACTERS_SUFFIX
from novxlib.novx_globals import CH_ROOT
from novxlib.novx_globals import CR_ROOT
from novxlib.novx_globals import Error
from novxlib.novx_globals import ITEMS_SUFFIX
from novxlib.novx_globals import IT_ROOT
from novxlib.novx_globals import LC_ROOT
from novxlib.novx_globals import LOCATIONS_SUFFIX
from novxlib.novx_globals import MANUSCRIPT_SUFFIX
from novxlib.novx_globals import PN_ROOT
from novxlib.novx_globals import SECTIONS_SUFFIX
from novxlib.novx_globals import _
from novxlib.novx_globals import list_to_string
from novxlib.novx_globals import norm_path


class FileExport(File):
    """Abstract novelibre project file exporter representation.
    
    This class is generic and contains no conversion algorithm and no templates.
    """
    SUFFIX = ''
    _fileHeader = ''
    _partTemplate = ''
    _chapterTemplate = ''
    _unusedChapterTemplate = ''
    _sectionTemplate = ''
    _firstSectionTemplate = ''
    _unusedSectionTemplate = ''
    _stage1Template = ''
    _stage2Template = ''
    _sectionDivider = ''
    _chapterEndTemplate = ''
    _unusedChapterEndTemplate = ''
    _characterSectionHeading = ''
    _characterTemplate = ''
    _locationSectionHeading = ''
    _locationTemplate = ''
    _itemSectionHeading = ''
    _itemTemplate = ''
    _fileFooter = ''
    _projectNoteTemplate = ''
    _arcTemplate = ''

    _DIVIDER = ', '

    def __init__(self, filePath, **kwargs):
        """Initialize filter strategy class instances.
        
        Positional arguments:
            filePath: str -- path to the file represented by the File instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            

        Extends the superclass constructor.
        """
        super().__init__(filePath, **kwargs)
        self._sectionFilter = Filter()
        self._chapterFilter = Filter()
        self._characterFilter = Filter()
        self._locationFilter = Filter()
        self._itemFilter = Filter()
        self._arcFilter = Filter()
        self._turningPointFilter = Filter()

    def write(self):
        """Write instance variables to the export file.
        
        Create a template-based output file. 
        Return a message in case of success.
        Raise the "Error" exception in case of error. 
        """
        text = self._get_text()
        backedUp = False
        if os.path.isfile(self.filePath):
            try:
                os.replace(self.filePath, f'{self.filePath}.bak')
            except:
                raise Error(f'{_("Cannot overwrite file")}: "{norm_path(self.filePath)}".')
            else:
                backedUp = True
        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            if backedUp:
                os.replace(f'{self.filePath}.bak', self.filePath)
            raise Error(f'{_("Cannot write file")}: "{norm_path(self.filePath)}".')

    def _get_fileHeaderMapping(self):
        """Return a mapping dictionary for the project section.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        projectTemplateMapping = dict(
            Title=self._convert_from_novx(self.novel.title, quick=True),
            Desc=self._convert_from_novx(self.novel.desc),
            AuthorName=self._convert_from_novx(self.novel.authorName, quick=True),
            Language=self.novel.languageCode,
            Country=self.novel.countryCode,
        )
        return projectTemplateMapping

    def _convert_from_novx(self, text, quick=False, append=False, xml=False):
        """Return text, converted from novelibre markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick: bool -- if True, apply a conversion mode for one-liners without formatting.        
        """
        if text is None:
            text = ''
        return(text)

    def _get_arcMapping(self, acId):
        """Return a mapping dictionary for a arc section.
        
        Positional arguments:
            acId: str -- arc ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        arcMapping = dict(
            ID=acId,
            Title=self._convert_from_novx(self.novel.arcs[acId].title, quick=True),
            Desc=self._convert_from_novx(self.novel.arcs[acId].desc),
            ProjectName=self._convert_from_novx(self.projectName, quick=True),
            ProjectPath=self.projectPath,
            Language=self.novel.languageCode,
            Country=self.novel.countryCode,
        )
        return arcMapping

    def _get_arcs(self):
        """Process the arcs. 
        
        Iterate through the sorted arc list and apply the template, 
        substituting placeholders according to the arc mapping dictionary.
        Skip arcs not accepted by the arc filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        for acId in self.novel.tree.get_children(AC_ROOT):
            if self._arcFilter.accept(self, acId):
                if self._arcTemplate:
                    template = Template(self._arcTemplate)
                    lines.append(template.safe_substitute(self._get_arcMapping(acId)))
        return lines

    def _get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section.
        
        Positional arguments:
            chId: str -- chapter ID.
            chapterNumber: int -- chapter number.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if chapterNumber == 0:
            chapterNumber = ''

        chapterMapping = dict(
            ID=chId,
            ChapterNumber=chapterNumber,
            Title=self._convert_from_novx(self.novel.chapters[chId].title, quick=True),
            Desc=self._convert_from_novx(self.novel.chapters[chId].desc),
            ProjectName=self._convert_from_novx(self.projectName, quick=True),
            ProjectPath=self.projectPath,
            Language=self.novel.languageCode,
            Country=self.novel.countryCode,
            ManuscriptSuffix=MANUSCRIPT_SUFFIX,
        )
        return chapterMapping

    def _get_chapters(self):
        """Process the chapters and nested sections.
        
        Iterate through the sorted chapter list and apply the templates, 
        substituting placeholders according to the chapter mapping dictionary.
        For each chapter call the processing of its included sections.
        Skip chapters not accepted by the chapter filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        chapterNumber = 0
        sectionNumber = 0
        wordsTotal = 0
        for chId in self.novel.tree.get_children(CH_ROOT):
            dispNumber = 0
            if not self._chapterFilter.accept(self, chId):
                continue

            # The order counts; be aware that "Todo" and "Notes" chapters are
            # always unused.
            # Has the chapter only sections not to be exported?
            template = None
            if self.novel.chapters[chId].chType == 1:
                # Chapter is "unused" type.
                if self._unusedChapterTemplate:
                    template = Template(self._unusedChapterTemplate)
            elif self.novel.chapters[chId].chLevel == 1 and self._partTemplate:
                template = Template(self._partTemplate)
            else:
                template = Template(self._chapterTemplate)
                chapterNumber += 1
                dispNumber = chapterNumber
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))

            #--- Process sections.
            sectionLines, sectionNumber, wordsTotal = self._get_sections(chId, sectionNumber, wordsTotal)
            lines.extend(sectionLines)

            #--- Process chapter ending.
            template = None
            if self.novel.chapters[chId].chType == 1:
                if self._unusedChapterEndTemplate:
                    template = Template(self._unusedChapterEndTemplate)
            elif self._chapterEndTemplate:
                template = Template(self._chapterEndTemplate)
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))
        return lines

    def _get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section.
        
        Positional arguments:
            crId: str -- character ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.novel.characters[crId].tags is not None:
            tags = list_to_string(self.novel.characters[crId].tags, divider=self._DIVIDER)
        else:
            tags = ''
        if self.novel.characters[crId].isMajor:
            characterStatus = Character.MAJOR_MARKER
        else:
            characterStatus = Character.MINOR_MARKER

        characterMapping = dict(
            ID=crId,
            Title=self._convert_from_novx(self.novel.characters[crId].title, quick=True),
            Desc=self._convert_from_novx(self.novel.characters[crId].desc),
            Tags=self._convert_from_novx(tags),
            AKA=self._convert_from_novx(self.novel.characters[crId].aka, quick=True),
            Notes=self._convert_from_novx(self.novel.characters[crId].notes),
            Bio=self._convert_from_novx(self.novel.characters[crId].bio),
            Goals=self._convert_from_novx(self.novel.characters[crId].goals),
            FullName=self._convert_from_novx(self.novel.characters[crId].fullName, quick=True),
            Status=characterStatus,
            ProjectName=self._convert_from_novx(self.projectName, quick=True),
            ProjectPath=self.projectPath,
            CharactersSuffix=CHARACTERS_SUFFIX,
        )
        return characterMapping

    def _get_characters(self):
        """Process the characters.
        
        Iterate through the sorted character list and apply the template, 
        substituting placeholders according to the character mapping dictionary.
        Skip characters not accepted by the character filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._characterSectionHeading:
            lines = [self._characterSectionHeading]
        else:
            lines = []
        template = Template(self._characterTemplate)
        for crId in self.novel.tree.get_children(CR_ROOT):
            if self._characterFilter.accept(self, crId):
                lines.append(template.safe_substitute(self._get_characterMapping(crId)))
        return lines

    def _get_fileHeader(self):
        """Process the file header.
        
        Apply the file header template, substituting placeholders 
        according to the file header mapping dictionary.
        Return a list of strings.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        template = Template(self._fileHeader)
        lines.append(template.safe_substitute(self._get_fileHeaderMapping()))
        return lines

    def _get_itemMapping(self, itId):
        """Return a mapping dictionary for an item section.
        
        Positional arguments:
            itId: str -- item ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.novel.items[itId].tags is not None:
            tags = list_to_string(self.novel.items[itId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        itemMapping = dict(
            ID=itId,
            Title=self._convert_from_novx(self.novel.items[itId].title, quick=True),
            Desc=self._convert_from_novx(self.novel.items[itId].desc),
            Tags=self._convert_from_novx(tags, quick=True),
            AKA=self._convert_from_novx(self.novel.items[itId].aka, quick=True),
            ProjectName=self._convert_from_novx(self.projectName, quick=True),
            ProjectPath=self.projectPath,
            ItemsSuffix=ITEMS_SUFFIX,
        )
        return itemMapping

    def _get_items(self):
        """Process the items. 
        
        Iterate through the sorted item list and apply the template, 
        substituting placeholders according to the item mapping dictionary.
        Skip items not accepted by the item filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._itemSectionHeading:
            lines = [self._itemSectionHeading]
        else:
            lines = []
        template = Template(self._itemTemplate)
        for itId in self.novel.tree.get_children(IT_ROOT):
            if self._itemFilter.accept(self, itId):
                lines.append(template.safe_substitute(self._get_itemMapping(itId)))
        return lines

    def _get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section.
        
        Positional arguments:
            lcId: str -- location ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.novel.locations[lcId].tags is not None:
            tags = list_to_string(self.novel.locations[lcId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        locationMapping = dict(
            ID=lcId,
            Title=self._convert_from_novx(self.novel.locations[lcId].title, quick=True),
            Desc=self._convert_from_novx(self.novel.locations[lcId].desc),
            Tags=self._convert_from_novx(tags, quick=True),
            AKA=self._convert_from_novx(self.novel.locations[lcId].aka, quick=True),
            ProjectName=self._convert_from_novx(self.projectName, quick=True),
            ProjectPath=self.projectPath,
            LocationsSuffix=LOCATIONS_SUFFIX,
        )
        return locationMapping

    def _get_locations(self):
        """Process the locations.
        
        Iterate through the sorted location list and apply the template, 
        substituting placeholders according to the location mapping dictionary.
        Skip locations not accepted by the location filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._locationSectionHeading:
            lines = [self._locationSectionHeading]
        else:
            lines = []
        template = Template(self._locationTemplate)
        for lcId in self.novel.tree.get_children(LC_ROOT):
            if self._locationFilter.accept(self, lcId):
                lines.append(template.safe_substitute(self._get_locationMapping(lcId)))
        return lines

    def _get_sectionMapping(self, scId, sectionNumber, wordsTotal):
        """Return a mapping dictionary for a section section.
        
        Positional arguments:
            scId: str -- section ID.
            sectionNumber: int -- section number to be displayed.
            wordsTotal: int -- accumulated wordcount.
        
        This is a template method that can be extended or overridden by subclasses.
        """

        #--- Create a comma separated tag list.
        if sectionNumber == 0:
            sectionNumber = ''
        if self.novel.sections[scId].tags is not None:
            tags = list_to_string(self.novel.sections[scId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        #--- Create a comma separated character list.
        try:
            # Note: Due to a bug, novelibre sections might hold invalid
            # viepoint characters
            sChList = []
            for crId in self.novel.sections[scId].characters:
                sChList.append(self.novel.characters[crId].title)
            sectionChars = list_to_string(sChList, divider=self._DIVIDER)
            viewpointChar = sChList[0]
        except:
            sectionChars = ''
            viewpointChar = ''

        #--- Create a comma separated location list.
        if self.novel.sections[scId].locations is not None:
            sLcList = []
            for lcId in self.novel.sections[scId].locations:
                sLcList.append(self.novel.locations[lcId].title)
            sectionLocs = list_to_string(sLcList, divider=self._DIVIDER)
        else:
            sectionLocs = ''

        #--- Create a comma separated item list.
        if self.novel.sections[scId].items is not None:
            sItList = []
            for itId in self.novel.sections[scId].items:
                sItList.append(self.novel.items[itId].title)
            sectionItems = list_to_string(sItList, divider=self._DIVIDER)
        else:
            sectionItems = ''

        #--- Create A/R marker string.

        #--- Date or day.
        if self.novel.sections[scId].date is not None and self.novel.sections[scId].date != Section.NULL_DATE:
            scDay = ''
            scDate = self.novel.sections[scId].date
            cmbDate = self.novel.sections[scId].date
        else:
            scDate = ''
            if self.novel.sections[scId].day is not None:
                scDay = self.novel.sections[scId].day
                cmbDate = f'Day {self.novel.sections[scId].day}'
            else:
                scDay = ''
                cmbDate = ''

        #--- Time.
        if self.novel.sections[scId].time is not None:
            scTime = self.novel.sections[scId].time.rsplit(':', 1)[0]
            # remove seconds
        else:
            scTime = ''

        #--- Create a combined duration information.
        if self.novel.sections[scId].lastsDays is not None and self.novel.sections[scId].lastsDays != '0':
            lastsDays = self.novel.sections[scId].lastsDays
            days = f'{self.novel.sections[scId].lastsDays}d '
        else:
            lastsDays = ''
            days = ''
        if self.novel.sections[scId].lastsHours is not None and self.novel.sections[scId].lastsHours != '0':
            lastsHours = self.novel.sections[scId].lastsHours
            hours = f'{self.novel.sections[scId].lastsHours}h '
        else:
            lastsHours = ''
            hours = ''
        if self.novel.sections[scId].lastsMinutes is not None and self.novel.sections[scId].lastsMinutes != '0':
            lastsMinutes = self.novel.sections[scId].lastsMinutes
            minutes = f'{self.novel.sections[scId].lastsMinutes}min'
        else:
            lastsMinutes = ''
            minutes = ''
        duration = f'{days}{hours}{minutes}'

        sectionMapping = dict(
            ID=scId,
            SectionNumber=sectionNumber,
            Title=self._convert_from_novx(self.novel.sections[scId].title, quick=True),
            Desc=self._convert_from_novx(self.novel.sections[scId].desc, append=self.novel.sections[scId].appendToPrev),
            WordCount=str(self.novel.sections[scId].wordCount),
            WordsTotal=wordsTotal,
            Status=int(self.novel.sections[scId].status),
            SectionContent=self._convert_from_novx(self.novel.sections[scId].sectionContent, append=self.novel.sections[scId].appendToPrev, xml=True),
            Date=scDate,
            Time=scTime,
            Day=scDay,
            ScDate=cmbDate,
            LastsDays=lastsDays,
            LastsHours=lastsHours,
            LastsMinutes=lastsMinutes,
            Duration=duration,
            ReactionSection=Section.PACING[self.novel.sections[scId].scPacing],
            Goal=self._convert_from_novx(self.novel.sections[scId].goal),
            Conflict=self._convert_from_novx(self.novel.sections[scId].conflict),
            Outcome=self._convert_from_novx(self.novel.sections[scId].outcome),
            Tags=self._convert_from_novx(tags, quick=True),
            Characters=sectionChars,
            Viewpoint=viewpointChar,
            Locations=sectionLocs,
            Items=sectionItems,
            Notes=self._convert_from_novx(self.novel.sections[scId].notes),
            ProjectName=self._convert_from_novx(self.projectName, quick=True),
            ProjectPath=self.projectPath,
            Language=self.novel.languageCode,
            Country=self.novel.countryCode,
            ManuscriptSuffix=MANUSCRIPT_SUFFIX,
            SectionsSuffix=SECTIONS_SUFFIX,
        )
        return sectionMapping

    def _get_sections(self, chId, sectionNumber, wordsTotal):
        """Process the sections.
        
        Positional arguments:
            chId: str -- chapter ID.
            sectionNumber: int -- number of previously processed sections.
            wordsTotal: int -- accumulated wordcount of the previous sections.
        
        Iterate through a sorted section list and apply the templates, 
        substituting placeholders according to the section mapping dictionary.
        Skip sections not accepted by the section filter.
        
        Return a tuple:
            lines: list of strings -- the lines of the processed section.
            sectionNumber: int -- number of all processed sections.
            wordsTotal: int -- accumulated wordcount of all processed sections.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        firstSectionInChapter = True
        for scId in self.novel.tree.get_children(chId):
            template = None
            dispNumber = 0
            if not self._sectionFilter.accept(self, scId):
                continue

            sectionContent = self.novel.sections[scId].sectionContent
            if sectionContent is None:
                sectionContent = ''

            if self.novel.sections[scId].scType == 2:
                if self._stage1Template:
                    template = Template(self._stage1Template)
                else:
                    continue

            elif self.novel.sections[scId].scType == 3:
                if self._stage2Template:
                    template = Template(self._stage2Template)
                else:
                    continue

            elif self.novel.sections[scId].scType == 1 or self.novel.chapters[chId].chType == 1:
                if self._unusedSectionTemplate:
                    template = Template(self._unusedSectionTemplate)
                else:
                    continue

            else:
                sectionNumber += 1
                dispNumber = sectionNumber
                wordsTotal += self.novel.sections[scId].wordCount
                template = Template(self._sectionTemplate)
                if firstSectionInChapter and self._firstSectionTemplate:
                    template = Template(self._firstSectionTemplate)
            if not (firstSectionInChapter or self.novel.sections[scId].appendToPrev):
                lines.append(self._sectionDivider)
            if template is not None:
                lines.append(template.safe_substitute(self._get_sectionMapping(scId, dispNumber, wordsTotal)))
            firstSectionInChapter = False
        return lines, sectionNumber, wordsTotal

    def _get_prjNoteMapping(self, pnId):
        """Return a mapping dictionary for a project note.
        
        Positional arguments:
            pnId: str -- project note ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        noteMapping = dict(
            ID=pnId,
            Title=self._convert_from_novx(self.novel.projectNotes[pnId].title, quick=True),
            Desc=self._convert_from_novx(self.novel.projectNotes[pnId].desc, quick=True),
            ProjectName=self._convert_from_novx(self.projectName, quick=True),
            ProjectPath=self.projectPath,
        )
        return noteMapping

    def _get_projectNotes(self):
        """Process the project notes. 
        
        Iterate through the sorted project note list and apply the template, 
        substituting placeholders according to the item mapping dictionary.
        Skip items not accepted by the item filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        template = Template(self._projectNoteTemplate)
        for pnId in self.novel.tree.get_children(PN_ROOT):
            map = self._get_prjNoteMapping(pnId)
            lines.append(template.safe_substitute(map))
        return lines

    def _get_text(self):
        """Call all processing methods.
        
        Return a string to be written to the output file.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = self._get_fileHeader()
        lines.extend(self._get_chapters())
        lines.extend(self._get_characters())
        lines.extend(self._get_locations())
        lines.extend(self._get_items())
        lines.extend(self._get_arcs())
        lines.extend(self._get_projectNotes())
        lines.append(self._fileFooter)
        return ''.join(lines)

