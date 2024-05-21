"""Provide a class for novelibre section representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from datetime import datetime, date, timedelta
from datetime import time
import re

from novxlib.model.basic_element_tags import BasicElementTags
from novxlib.novx_globals import _
from novxlib.novx_globals import string_to_list
import xml.etree.ElementTree as ET

# Regular expressions for counting words and characters like in LibreOffice.
# See: https://help.libreoffice.org/latest/en-GB/text/swriter/guide/words_count.html
ADDITIONAL_WORD_LIMITS = re.compile('--|—|–|\<\/p\>')
# this is to be replaced by spaces when counting words

NO_WORD_LIMITS = re.compile('\<note\>.*?\<\/note\>|\<comment\>.*?\<\/comment\>|\<.+?\>')
# this is to be replaced by empty strings when counting words


class Section(BasicElementTags):
    """novelibre section representation."""

    SCENE = ['-', 'A', 'R', 'x']
    # emulating an enumeration for the scene Action/Reaction/Other type

    STATUS = [
        None,
        _('Outline'),
        _('Draft'),
        _('1st Edit'),
        _('2nd Edit'),
        _('Done')
    ]
    # emulating an enumeration for the section completion status

    NULL_DATE = '0001-01-01'
    NULL_TIME = '00:00:00'

    def __init__(self,
            scType=None,
            scene=None,
            status=None,
            appendToPrev=None,
            goal=None,
            conflict=None,
            outcome=None,
            plotNotes=None,
            scDate=None,
            scTime=None,
            day=None,
            lastsMinutes=None,
            lastsHours=None,
            lastsDays=None,
            characters=None,
            locations=None,
            items=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)
        self._sectionContent = None
        self.wordCount = 0
        # To be updated by the sectionContent setter

        # Initialize properties.
        self._scType = scType
        self._scene = scene
        self._status = status
        self._appendToPrev = appendToPrev
        self._goal = goal
        self._conflict = conflict
        self._outcome = outcome
        self._plotlineNotes = plotNotes
        try:
            newDate = date.fromisoformat(scDate)
            self._weekDay = newDate.weekday()
            self._localeDate = newDate.strftime('%x')
            self._date = scDate
        except:
            self._weekDay = None
            self._localeDate = None
            self._date = None
        self._time = scTime
        self._day = day
        self._lastsMinutes = lastsMinutes
        self._lastsHours = lastsHours
        self._lastsDays = lastsDays
        self._characters = characters
        self._locations = locations
        self._items = items

        self.scPlotLines = []
        # Back references to PlotLine.sections
        self.scPlotPoints = {}
        # Back references to TurningPoint.sectionAssoc
        # key: plot point ID, value: plot line ID

    @property
    def sectionContent(self):
        return self._sectionContent

    @sectionContent.setter
    def sectionContent(self, text):
        """Set sectionContent updating word count and letter count."""
        if self._sectionContent != text:
            self._sectionContent = text
            if text is not None:
                text = ADDITIONAL_WORD_LIMITS.sub(' ', text)
                text = NO_WORD_LIMITS.sub('', text)
                wordList = text.split()
                self.wordCount = len(wordList)
            else:
                self.wordCount = 0
            self.on_element_change()

    @property
    def scType(self):
        # 0 = Normal
        # 1 = Unused
        # 2 = Level 1 stage
        # 3 = Level 2 stage
        return self._scType

    @scType.setter
    def scType(self, newVal):
        if self._scType != newVal:
            self._scType = newVal
            self.on_element_change()

    @property
    def scene(self):
        # 0 = N/A
        # 1 = Action
        # 2 = Reaction
        # 3 = Custom
        return self._scene

    @scene.setter
    def scene(self, newVal):
        if self._scene != newVal:
            self._scene = newVal
            self.on_element_change()

    @property
    def status(self):
        # 1 - Outline
        # 2 - Draft
        # 3 - 1st Edit
        # 4 - 2nd Edit
        # 5 - Done
        return self._status

    @status.setter
    def status(self, newVal):
        if self._status != newVal:
            self._status = newVal
            self.on_element_change()

    @property
    def appendToPrev(self):
        # if True, append section to the previous one without section separator
        return self._appendToPrev

    @appendToPrev.setter
    def appendToPrev(self, newVal):
        if self._appendToPrev != newVal:
            self._appendToPrev = newVal
            self.on_element_change()

    @property
    def goal(self):
        return self._goal

    @goal.setter
    def goal(self, newVal):
        if self._goal != newVal:
            self._goal = newVal
            self.on_element_change()

    @property
    def conflict(self):
        return self._conflict

    @conflict.setter
    def conflict(self, newVal):
        if self._conflict != newVal:
            self._conflict = newVal
            self.on_element_change()

    @property
    def outcome(self):
        return self._outcome

    @outcome.setter
    def outcome(self, newVal):
        if self._outcome != newVal:
            self._outcome = newVal
            self.on_element_change()

    @property
    def plotlineNotes(self):
        # Dict of {plot line ID: text}
        try:
            return dict(self._plotlineNotes)
        except TypeError:
            return None

    @plotlineNotes.setter
    def plotlineNotes(self, newVal):
        if self._plotlineNotes != newVal:
            self._plotlineNotes = newVal
            self.on_element_change()

    @property
    def date(self):
        # yyyy-mm-dd
        return self._date

    @date.setter
    def date(self, newVal):
        if self._date != newVal:
            if not newVal:
                self._date = None
                self._weekDay = None
                self._localeDate = None
                self.on_element_change()
                return

            try:
                newDate = date.fromisoformat(newVal)
                self._weekDay = newDate.weekday()
            except:
                return
                # date and week day remain unchanged

            try:
                self._localeDate = newDate.strftime('%x')
            except:
                self._localeDate = newVal
            self._date = newVal
            self.on_element_change()

    @property
    def weekDay(self):
        # the number of the day ot the week
        return self._weekDay

    @property
    def localeDate(self):
        # the preferred date representation for the current locale
        return self._localeDate

    @property
    def time(self):
        # hh:mm:ss
        return self._time

    @time.setter
    def time(self, newVal):
        if self._time != newVal:
            self._time = newVal
            self.on_element_change()

    @property
    def day(self):
        return self._day

    @day.setter
    def day(self, newVal):
        if self._day != newVal:
            self._day = newVal
            self.on_element_change()

    @property
    def lastsMinutes(self):
        return self._lastsMinutes

    @lastsMinutes.setter
    def lastsMinutes(self, newVal):
        if self._lastsMinutes != newVal:
            self._lastsMinutes = newVal
            self.on_element_change()

    @property
    def lastsHours(self):
        return self._lastsHours

    @lastsHours.setter
    def lastsHours(self, newVal):
        if self._lastsHours != newVal:
            self._lastsHours = newVal
            self.on_element_change()

    @property
    def lastsDays(self):
        return self._lastsDays

    @lastsDays.setter
    def lastsDays(self, newVal):
        if self._lastsDays != newVal:
            self._lastsDays = newVal
            self.on_element_change()

    @property
    def characters(self):
        # list of character IDs
        try:
            return self._characters[:]
        except TypeError:
            return None

    @characters.setter
    def characters(self, newVal):
        if self._characters != newVal:
            self._characters = newVal
            self.on_element_change()

    @property
    def locations(self):
        # List of location IDs
        try:
            return self._locations[:]
        except TypeError:
            return None

    @locations.setter
    def locations(self, newVal):
        if self._locations != newVal:
            self._locations = newVal
            self.on_element_change()

    @property
    def items(self):
        # List of Item IDs
        try:
            return self._items[:]
        except TypeError:
            return None

    @items.setter
    def items(self, newVal):
        if self._items != newVal:
            self._items = newVal
            self.on_element_change()

    def day_to_date(self, referenceDate):
        """Convert day to specific date.
        
        Positional argument:
        referenceDate: str -- reference date in isoformat.

        On success, return True. Otherwise return False. 
        """
        if not self._date:
            try:
                deltaDays = timedelta(days=int(self._day))
                refDate = date.fromisoformat(referenceDate)
                self.date = date.isoformat(refDate + deltaDays)
                self._day = None
            except:
                self.date = None
                return False

        return True

    def date_to_day(self, referenceDate):
        """Convert specific date to day.
        
        Positional argument:
        referenceDate: str -- reference date in isoformat.
        
        On success, return True. Otherwise return False. 
        """
        if not self._day:
            try:
                sectionDate = date.fromisoformat(self._date)
                referenceDate = date.fromisoformat(referenceDate)
                self._day = str((sectionDate - referenceDate).days)
                self.date = None
            except:
                self._day = None
                return False

        return True

    def from_xml(self, xmlElement):
        super().from_xml(xmlElement)
        # Attributes.
        typeStr = xmlElement.get('type', '0')
        if typeStr in ('0', '1', '2', '3'):
            self.scType = int(typeStr)
        else:
            self.scType = 1
        status = xmlElement.get('status', None)
        if status in ('2', '3', '4', '5'):
            self.status = int(status)
        else:
            self.status = 1
        scene = xmlElement.get('scene', 0)
        if scene in ('1', '2', '3'):
            self.scene = int(scene)
        else:
            self.scene = 0

        if not self.scene:
            # looking for deprecated attribute from DTD 1.3
            scPacing = xmlElement.get('pacing', None)
            if scPacing in ('1', '2'):
                self.scene = int(scPacing) + 1

        self.appendToPrev = xmlElement.get('append', None) == '1'

        # Goal/Conflict/outcome.
        self.goal = self._xml_element_to_text(xmlElement.find('Goal'))
        self.conflict = self._xml_element_to_text(xmlElement.find('Conflict'))
        self.outcome = self._xml_element_to_text(xmlElement.find('Outcome'))

        # Plot notes.
        xmlPlotNotes = xmlElement.find('PlotNotes')
        # looking for deprecated element from DTD 1.3
        if xmlPlotNotes is None:
            xmlPlotNotes = xmlElement
        plotNotes = {}
        for xmlPlotLineNote in xmlPlotNotes.iterfind('PlotlineNotes'):
            plId = xmlPlotLineNote.get('id', None)
            plotNotes[plId] = self._xml_element_to_text(xmlPlotLineNote)
        self.plotlineNotes = plotNotes

        # Date/Day and Time.
        if xmlElement.find('Date') is not None:
            dateStr = xmlElement.find('Date').text
            try:
                date.fromisoformat(dateStr)
            except:
                self.date = None
            else:
                self.date = dateStr
        elif xmlElement.find('Day') is not None:
            dayStr = xmlElement.find('Day').text
            try:
                int(dayStr)
            except ValueError:
                self.day = None
            else:
                self.day = dayStr

        if xmlElement.find('Time') is not None:
            timeStr = xmlElement.find('Time').text
            try:
                time.fromisoformat(timeStr)
            except:
                self.time = None
            else:
                self.time = timeStr

        # Duration.
        self.lastsDays = self._get_element_text(xmlElement, 'LastsDays')
        self.lastsHours = self._get_element_text(xmlElement, 'LastsHours')
        self.lastsMinutes = self._get_element_text(xmlElement, 'LastsMinutes')

        # Characters references.
        scCharacters = []
        xmlCharacters = xmlElement.find('Characters')
        if xmlCharacters is not None:
            crIds = xmlCharacters.get('ids', None)
            if crIds is not None:
                for crId in string_to_list(crIds, divider=' '):
                    scCharacters.append(crId)
        self.characters = scCharacters

        # Locations references.
        scLocations = []
        xmlLocations = xmlElement.find('Locations')
        if xmlLocations is not None:
            lcIds = xmlLocations.get('ids', None)
            if lcIds is not None:
                for lcId in string_to_list(lcIds, divider=' '):
                    scLocations.append(lcId)
        self.locations = scLocations

        # Items references.
        scItems = []
        xmlItems = xmlElement.find('Items')
        if xmlItems is not None:
            itIds = xmlItems.get('ids', None)
            if itIds is not None:
                for itId in string_to_list(itIds, divider=' '):
                    scItems.append(itId)
        self.items = scItems

        # Content.
        if xmlElement.find('Content'):
            xmlStr = ET.tostring(
                xmlElement.find('Content'),
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
                self.sectionContent = xmlStr
            else:
                self.sectionContent = '<p></p>'
        else:
            self.sectionContent = '<p></p>'

    def get_end_date_time(self):
        """Return the section end (date, time, day) tuple calculated from start and duration."""
        endDate = None
        endTime = None
        endDay = None
        # Calculate end date from section section duration.
        if self.lastsDays:
            lastsDays = int(self.lastsDays)
        else:
            lastsDays = 0
        if self.lastsHours:
            lastsSeconds = int(self.lastsHours) * 3600
        else:
            lastsSeconds = 0
        if self.lastsMinutes:
            lastsSeconds += int(self.lastsMinutes) * 60
        sectionDuration = timedelta(days=lastsDays, seconds=lastsSeconds)
        if self.time:
            if self.date:
                try:
                    sectionStart = datetime.fromisoformat(f'{self.date} {self.time}')
                    sectionEnd = sectionStart + sectionDuration
                    endDate, endTime = sectionEnd.isoformat().split('T')
                except:
                    pass
            else:
                try:
                    if self.day:
                        dayInt = int(self.day)
                    else:
                        dayInt = 0
                    startDate = (date.min + timedelta(days=dayInt)).isoformat()
                    sectionStart = datetime.fromisoformat(f'{startDate} {self.time}')
                    sectionEnd = sectionStart + sectionDuration
                    endDate, endTime = sectionEnd.isoformat().split('T')
                    endDay = str((date.fromisoformat(endDate) - date.min).days)
                    endDate = None
                except:
                    pass
        return endDate, endTime, endDay

    def to_xml(self, xmlElement):
        super().to_xml(xmlElement)
        if self.scType:
            xmlElement.set('type', str(self.scType))
        if self.status > 1:
            xmlElement.set('status', str(self.status))
        if self.scene > 0:
            xmlElement.set('scene', str(self.scene))
        if self.appendToPrev:
            xmlElement.set('append', '1')

        # Goal/Conflict/Outcome.
        if self.goal:
            xmlElement.append(self._text_to_xml_element('Goal', self.goal))
        if self.conflict:
            xmlElement.append(self._text_to_xml_element('Conflict', self.conflict))
        if self.outcome:
            xmlElement.append(self._text_to_xml_element('Outcome', self.outcome))

        # Plot notes.
        if self.plotlineNotes:
            for plId in self.plotlineNotes:
                if not plId in self.scPlotLines:
                    continue

                if not self.plotlineNotes[plId]:
                    continue

                xmlPlotlineNotes = self._text_to_xml_element('PlotlineNotes', self.plotlineNotes[plId])
                xmlPlotlineNotes.set('id', plId)
                xmlElement.append(xmlPlotlineNotes)

        # Date/Day and Time.
        if self.date:
            ET.SubElement(xmlElement, 'Date').text = self.date
        elif self.day:
            ET.SubElement(xmlElement, 'Day').text = self.day
        if self.time:
            ET.SubElement(xmlElement, 'Time').text = self.time

        # Duration.
        if self.lastsDays and self.lastsDays != '0':
            ET.SubElement(xmlElement, 'LastsDays').text = self.lastsDays
        if self.lastsHours and self.lastsHours != '0':
            ET.SubElement(xmlElement, 'LastsHours').text = self.lastsHours
        if self.lastsMinutes and self.lastsMinutes != '0':
            ET.SubElement(xmlElement, 'LastsMinutes').text = self.lastsMinutes

        # Characters references.
        if self.characters:
            attrib = {'ids':' '.join(self.characters)}
            ET.SubElement(xmlElement, 'Characters', attrib=attrib)

        # Locations references.
        if self.locations:
            attrib = {'ids':' '.join(self.locations)}
            ET.SubElement(xmlElement, 'Locations', attrib=attrib)

        # Items references.
        if self.items:
            attrib = {'ids':' '.join(self.items)}
            ET.SubElement(xmlElement, 'Items', attrib=attrib)

        # Content.
        sectionContent = self.sectionContent
        if sectionContent:
            if not sectionContent in ('<p></p>', '<p />'):
                xmlElement.append(ET.fromstring(f'<Content>{sectionContent}</Content>'))
