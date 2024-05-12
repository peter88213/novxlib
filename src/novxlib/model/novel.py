"""Provide a class for a novel representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from datetime import date
import locale
import re
import xml.etree.ElementTree as ET

from novxlib.model.basic_element import BasicElement

LANGUAGE_TAG = re.compile('\<span xml\:lang=\"(.*?)\"\>')


class Novel(BasicElement):
    """Novel representation."""

    def __init__(self,
            authorName=None,
            wordTarget=None,
            wordCountStart=None,
            languageCode=None,
            countryCode=None,
            renumberChapters=None,
            renumberParts=None,
            renumberWithinParts=None,
            romanChapterNumbers=None,
            romanPartNumbers=None,
            saveWordCount=None,
            workPhase=None,
            chapterHeadingPrefix=None,
            chapterHeadingSuffix=None,
            partHeadingPrefix=None,
            partHeadingSuffix=None,
            customGoal=None,
            customConflict=None,
            customOutcome=None,
            customChrBio=None,
            customChrGoals=None,
            referenceDate=None,
            tree=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)
        self._authorName = authorName
        self._wordTarget = wordTarget
        self._wordCountStart = wordCountStart
        self._languageCode = languageCode
        # Language code acc. to ISO 639-1.
        self._countryCode = countryCode
        # Country code acc. to ISO 3166-2.
        self._renumberChapters = renumberChapters
        # True: Auto-number chapters
        # False: Do not auto-number chapters
        self._renumberParts = renumberParts
        # True: Auto-number parts
        # False: Do not auto-number parts
        self._renumberWithinParts = renumberWithinParts
        # True: When auto-numbering chapters, start with 1 at each part beginning
        # False: When auto-numbering chapters, ignore parts
        self._romanChapterNumbers = romanChapterNumbers
        # True: Use Roman chapter numbers when auto-numbering
        # False: Use Arabic chapter numbers when auto-numbering
        self._romanPartNumbers = romanPartNumbers
        # True: Use Roman part numbers when auto-numbering
        # False: Use Arabic part numbers when auto-numbering
        self._saveWordCount = saveWordCount
        # True: Save daily word count log
        # False: Do not save daily word count log
        self._workPhase = workPhase
        # 1 - Outline
        # 2 - Draft
        # 3 - 1st Edit
        # 4 - 2nd Edit
        # 5 - Done
        self._chapterHeadingPrefix = chapterHeadingPrefix
        self._chapterHeadingSuffix = chapterHeadingSuffix
        self._partHeadingPrefix = partHeadingPrefix
        self._partHeadingSuffix = partHeadingSuffix
        self._customGoal = customGoal
        self._customConflict = customConflict
        self._customOutcome = customOutcome
        self._customChrBio = customChrBio
        self._customChrGoals = customChrGoals

        self.chapters = {}
        # key = chapter ID, value = Chapter instance.
        self.sections = {}
        # key = section ID, value = Section instance.
        self.plotPoints = {}
        # key = section ID, value = PlotPoint instance.
        self.languages = None
        # List of non-document languages occurring as section markup.
        # Format: ll-CC, where ll is the language code, and CC is the country code.
        self.plotLines = {}
        # key = plot line ID, value = PlotLine instance.
        self.locations = {}
        # key = location ID, value = WorldElement instance.
        self.items = {}
        # key = item ID, value = WorldElement instance.
        self.characters = {}
        # key = character ID, value = Character instance.
        self.projectNotes = {}
        # key = note ID, value = note instance.
        try:
            self.referenceWeekDay = date.fromisoformat(referenceDate).weekday()
            self._referenceDate = referenceDate
            # yyyy-mm-dd
        except:
            self.referenceWeekDay = None
            self._referenceDate = None
        self.tree = tree

    @property
    def authorName(self):
        return self._authorName

    @authorName.setter
    def authorName(self, newVal):
        if self._authorName != newVal:
            self._authorName = newVal
            self.on_element_change()

    @property
    def wordTarget(self):
        return self._wordTarget

    @wordTarget.setter
    def wordTarget(self, newVal):
        if self._wordTarget != newVal:
            self._wordTarget = newVal
            self.on_element_change()

    @property
    def wordCountStart(self):
        return self._wordCountStart

    @wordCountStart.setter
    def wordCountStart(self, newVal):
        if self._wordCountStart != newVal:
            self._wordCountStart = newVal
            self.on_element_change()

    @property
    def languageCode(self):
        return self._languageCode

    @languageCode.setter
    def languageCode(self, newVal):
        if self._languageCode != newVal:
            self._languageCode = newVal
            self.on_element_change()

    @property
    def countryCode(self):
        return self._countryCode

    @countryCode.setter
    def countryCode(self, newVal):
        if self._countryCode != newVal:
            self._countryCode = newVal
            self.on_element_change()

    @property
    def renumberChapters(self):
        return self._renumberChapters

    @renumberChapters.setter
    def renumberChapters(self, newVal):
        if self._renumberChapters != newVal:
            self._renumberChapters = newVal
            self.on_element_change()

    @property
    def renumberParts(self):
        return self._renumberParts

    @renumberParts.setter
    def renumberParts(self, newVal):
        if self._renumberParts != newVal:
            self._renumberParts = newVal
            self.on_element_change()

    @property
    def renumberWithinParts(self):
        return self._renumberWithinParts

    @renumberWithinParts.setter
    def renumberWithinParts(self, newVal):
        if self._renumberWithinParts != newVal:
            self._renumberWithinParts = newVal
            self.on_element_change()

    @property
    def romanChapterNumbers(self):
        return self._romanChapterNumbers

    @romanChapterNumbers.setter
    def romanChapterNumbers(self, newVal):
        if self._romanChapterNumbers != newVal:
            self._romanChapterNumbers = newVal
            self.on_element_change()

    @property
    def romanPartNumbers(self):
        return self._romanPartNumbers

    @romanPartNumbers.setter
    def romanPartNumbers(self, newVal):
        if self._romanPartNumbers != newVal:
            self._romanPartNumbers = newVal
            self.on_element_change()

    @property
    def saveWordCount(self):
        return self._saveWordCount

    @saveWordCount.setter
    def saveWordCount(self, newVal):
        if self._saveWordCount != newVal:
            self._saveWordCount = newVal
            self.on_element_change()

    @property
    def workPhase(self):
        return self._workPhase

    @workPhase.setter
    def workPhase(self, newVal):
        if self._workPhase != newVal:
            self._workPhase = newVal
            self.on_element_change()

    @property
    def chapterHeadingPrefix(self):
        return self._chapterHeadingPrefix

    @chapterHeadingPrefix.setter
    def chapterHeadingPrefix(self, newVal):
        if self._chapterHeadingPrefix != newVal:
            self._chapterHeadingPrefix = newVal
            self.on_element_change()

    @property
    def chapterHeadingSuffix(self):
        return self._chapterHeadingSuffix

    @chapterHeadingSuffix.setter
    def chapterHeadingSuffix(self, newVal):
        if self._chapterHeadingSuffix != newVal:
            self._chapterHeadingSuffix = newVal
            self.on_element_change()

    @property
    def partHeadingPrefix(self):
        return self._partHeadingPrefix

    @partHeadingPrefix.setter
    def partHeadingPrefix(self, newVal):
        if self._partHeadingPrefix != newVal:
            self._partHeadingPrefix = newVal
            self.on_element_change()

    @property
    def partHeadingSuffix(self):
        return self._partHeadingSuffix

    @partHeadingSuffix.setter
    def partHeadingSuffix(self, newVal):
        if self._partHeadingSuffix != newVal:
            self._partHeadingSuffix = newVal
            self.on_element_change()

    @property
    def customGoal(self):
        return self._customGoal

    @customGoal.setter
    def customGoal(self, newVal):
        if self._customGoal != newVal:
            self._customGoal = newVal
            self.on_element_change()

    @property
    def customConflict(self):
        return self._customConflict

    @customConflict.setter
    def customConflict(self, newVal):
        if self._customConflict != newVal:
            self._customConflict = newVal
            self.on_element_change()

    @property
    def customOutcome(self):
        return self._customOutcome

    @customOutcome.setter
    def customOutcome(self, newVal):
        if self._customOutcome != newVal:
            self._customOutcome = newVal
            self.on_element_change()

    @property
    def customChrBio(self):
        return self._customChrBio

    @customChrBio.setter
    def customChrBio(self, newVal):
        if self._customChrBio != newVal:
            self._customChrBio = newVal
            self.on_element_change()

    @property
    def customChrGoals(self):
        return self._customChrGoals

    @customChrGoals.setter
    def customChrGoals(self, newVal):
        if self._customChrGoals != newVal:
            self._customChrGoals = newVal
            self.on_element_change()

    @property
    def referenceDate(self):
        return self._referenceDate

    @referenceDate.setter
    def referenceDate(self, newVal):
        if self._referenceDate != newVal:
            if not newVal:
                self._referenceDate = None
                self.referenceWeekDay = None
            else:
                try:
                    self.referenceWeekDay = date.fromisoformat(newVal).weekday()
                except:
                    pass
                    # date and week day remain unchanged
                else:
                    self._referenceDate = newVal
                    self.on_element_change()

    def update_plot_lines(self):
        """Set section back references to PlotLine.sections and PlotPoint.sectionAssoc. """
        for scId in self.sections:
            self.sections[scId].scPlotPoints = {}
            self.sections[scId].scPlotLines = []
            for plId in self.plotLines:
                if scId in self.plotLines[plId].sections:
                    self.sections[scId].scPlotLines.append(plId)
                    for ppId in self.tree.get_children(plId):
                        if self.plotPoints[ppId].sectionAssoc == scId:
                            self.sections[scId].scPlotPoints[ppId] = plId
                            break

    def get_languages(self):
        """Determine the languages used in the document.
        
        Populate the self.languages list with all language codes found in the section contents.        
        Example:
        - language markup: 'Standard text <span xml:lang="en-AU"]Australian text</span>.'
        - language code: 'en-AU'
        """

        def languages(text):
            """Yield the language codes appearing in text.
            
            Positional arguments:
                text -- novx-formatted string to scan for language codes.
            """
            if text:
                m = LANGUAGE_TAG.search(text)
                while m:
                    text = text[m.span()[1]:]
                    yield m.group(1)
                    m = LANGUAGE_TAG.search(text)

        self.languages = []
        for scId in self.sections:
            text = self.sections[scId].sectionContent
            if text:
                for language in languages(text):
                    if not language in self.languages:
                        self.languages.append(language)

    def check_locale(self):
        """Check the document's locale (language code and country code).
        
        If the locale is missing, set the system locale.  
        If the locale doesn't look plausible, set "no language".      
        """
        if not self._languageCode or self._languageCode == 'None':
            # Language isn't set.
            try:
                sysLng, sysCtr = locale.getlocale()[0].split('_')
            except:
                # Fallback for old Windows versions.
                sysLng, sysCtr = locale.getdefaultlocale()[0].split('_')
            self._languageCode = sysLng
            self._countryCode = sysCtr
            self.on_element_change()
            return

        try:
            # Plausibility check: code must have two characters.
            if len(self._languageCode) == 2:
                if len(self._countryCode) == 2:
                    return
                    # keep the setting
        except:
            # code isn't a string
            pass
        # Existing language or country field looks not plausible
        self._languageCode = 'zxx'
        self._countryCode = 'none'
        self.on_element_change()

    def read_xml(self, xmlElement):
        super().read_xml(xmlElement)
        self.renumberChapters = xmlElement.get('renumberChapters', None) == '1'
        self.renumberParts = xmlElement.get('renumberParts', None) == '1'
        self.renumberWithinParts = xmlElement.get('renumberWithinParts', None) == '1'
        self.romanChapterNumbers = xmlElement.get('romanChapterNumbers', None) == '1'
        self.romanPartNumbers = xmlElement.get('romanPartNumbers', None) == '1'
        self.saveWordCount = xmlElement.get('saveWordCount', None) == '1'
        workPhase = xmlElement.get('workPhase', None)
        if workPhase in ('1', '2', '3', '4', '5'):
            self.workPhase = int(workPhase)
        else:
            self.workPhase = None

        # Author.
        self.authorName = self._get_element_text(xmlElement, 'Author')

        # Chapter heading prefix/suffix.
        self.chapterHeadingPrefix = self._get_element_text(xmlElement, 'ChapterHeadingPrefix')
        self.chapterHeadingSuffix = self._get_element_text(xmlElement, 'ChapterHeadingSuffix')

        # Part heading prefix/suffix.
        self.partHeadingPrefix = self._get_element_text(xmlElement, 'PartHeadingPrefix')
        self.partHeadingSuffix = self._get_element_text(xmlElement, 'PartHeadingSuffix')

        # Custom Goal/Conflict/Outcome.
        self.customGoal = self._get_element_text(xmlElement, 'CustomGoal')
        self.customConflict = self._get_element_text(xmlElement, 'CustomConflict')
        self.customOutcome = self._get_element_text(xmlElement, 'CustomOutcome')

        # Custom Character Bio/Goals.
        self.customChrBio = self._get_element_text(xmlElement, 'CustomChrBio')
        self.customChrGoals = self._get_element_text(xmlElement, 'CustomChrGoals')

        # Word count start/Word target.
        if xmlElement.find('WordCountStart') is not None:
            self.wordCountStart = int(xmlElement.find('WordCountStart').text)
        if xmlElement.find('WordTarget') is not None:
            self.wordTarget = int(xmlElement.find('WordTarget').text)

        # Reference date.
        self.referenceDate = self._get_element_text(xmlElement, 'ReferenceDate')

    def write_xml(self, xmlElement):
        super().write_xml(xmlElement)
        if self.renumberChapters:
            xmlElement.set('renumberChapters', '1')
        if self.renumberParts:
            xmlElement.set('renumberParts', '1')
        if self.renumberWithinParts:
            xmlElement.set('renumberWithinParts', '1')
        if self.romanChapterNumbers:
            xmlElement.set('romanChapterNumbers', '1')
        if self.romanPartNumbers:
            xmlElement.set('romanPartNumbers', '1')
        if self.saveWordCount:
            xmlElement.set('saveWordCount', '1')
        if self.workPhase is not None:
            xmlElement.set('workPhase', str(self.workPhase))

        # Author.
        if self.authorName:
            ET.SubElement(xmlElement, 'Author').text = self.authorName

        # Chapter heading prefix/suffix.
        if self.chapterHeadingPrefix:
            ET.SubElement(xmlElement, 'ChapterHeadingPrefix').text = self.chapterHeadingPrefix
        if self.chapterHeadingSuffix:
            ET.SubElement(xmlElement, 'ChapterHeadingSuffix').text = self.chapterHeadingSuffix

        # Part heading prefix/suffix.
        if self.partHeadingPrefix:
            ET.SubElement(xmlElement, 'PartHeadingPrefix').text = self.partHeadingPrefix
        if self.partHeadingSuffix:
            ET.SubElement(xmlElement, 'PartHeadingSuffix').text = self.partHeadingSuffix

        # Custom Goal/Conflict/Outcome.
        if self.customGoal:
            ET.SubElement(xmlElement, 'CustomGoal').text = self.customGoal
        if self.customConflict:
            ET.SubElement(xmlElement, 'CustomConflict').text = self.customConflict
        if self.customOutcome:
            ET.SubElement(xmlElement, 'CustomOutcome').text = self.customOutcome

        # Custom Character Bio/Goals.
        if self.customChrBio:
            ET.SubElement(xmlElement, 'CustomChrBio').text = self.customChrBio
        if self.customChrGoals:
            ET.SubElement(xmlElement, 'CustomChrGoals').text = self.customChrGoals

        # Word count start/Word target.
        if self.wordCountStart:
            ET.SubElement(xmlElement, 'WordCountStart').text = str(self.wordCountStart)
        if self.wordTarget:
            ET.SubElement(xmlElement, 'WordTarget').text = str(self.wordTarget)

        # Reference date.
        if self.referenceDate:
            ET.SubElement(xmlElement, 'ReferenceDate').text = self.referenceDate
