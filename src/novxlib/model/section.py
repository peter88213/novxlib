"""Provide a class for novelibre section representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from datetime import datetime, date, timedelta
import re
from novxlib.novx_globals import _
from novxlib.model.basic_element_tags import BasicElementTags

#--- Regular expressions for counting words and characters like in LibreOffice.
# See: https://help.libreoffice.org/latest/en-GB/text/swriter/guide/words_count.html
ADDITIONAL_WORD_LIMITS = re.compile('--|—|–|\<\/p\>')
# this is to be replaced by spaces when counting words

NO_WORD_LIMITS = re.compile('\<note\>.*?\<\/note\>|\<comment\>.*?\<\/comment\>|\<.+?\>')
# this is to be replaced by empty strings when counting words


class Section(BasicElementTags):
    """novelibre section representation."""
    PACING = ['A', 'R', 'C']
    # emulating an enumeration for the section Action/Reaction/Custom type

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
            scPacing=None,
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

        #--- Initialize properties.
        self._scType = scType
        self._scPacing = scPacing
        self._status = status
        self._appendToPrev = appendToPrev
        self._goal = goal
        self._conflict = conflict
        self._outcome = outcome
        self._plotNotes = plotNotes
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
    def scPacing(self):
        # 0 = Action
        # 1 = Reaction
        # 2 = Custom
        return self._scPacing

    @scPacing.setter
    def scPacing(self, newVal):
        if self._scPacing != newVal:
            self._scPacing = newVal
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
    def plotNotes(self):
        # Dict of {plot line ID: text}
        try:
            return dict(self._plotNotes)
        except TypeError:
            return None

    @plotNotes.setter
    def plotNotes(self, newVal):
        if self._plotNotes != newVal:
            self._plotNotes = newVal
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
            else:
                try:
                    newDate = date.fromisoformat(newVal)
                    self._weekDay = newDate.weekday()
                except:
                    pass
                    # date and week day remain unchanged
                else:
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

    def read_xml(self, xmlElement):
        super().read_xml(xmlElement)

    def write_xml(self, xmlElement):
        super().write_xml(xmlElement)
