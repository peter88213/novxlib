# Template and placeholder specifications for file export

Template-based file export: The application script iterates over chapters, sections, characters, locations, and items, selecting a template for each and replacing the placeholders with project data.

## List of templates

### Project level templates

- **fileHeader** (Text at the beginning of the exported file)
- **fileFooter** (Text at the end of the exported file)

### Chapter level templates

- **partTemplate** (chapter header; applied to chapters marked "section beginning")
- **chapterTemplate** (chapter header; applied to all "used" and "normal" chapters unless a "part template" exists)
- **unusedChapterTemplate** (chapter header; applied to chapters marked "unused")
- **chapterEndTemplate** (chapter footer; applied to all "used" and "normal" chapters unless a "part template" exists)
- **unusedChapterEndTemplate** (chapter footer; applied to chapters marked "unused")


### Section level templates

- **sectionTemplate** (applied to "used" sections within "normal" chapters)
- **firstSectionTemplate** (applied  to sections at the beginning of the chapter)
- **appendedSectionTemplate** (applied to sections marked "append to previous")
- **unusedSectionTemplate** (applied to "unused" sections)
- **sectionDivider** (lead sections, beginning from the second in chapter)


### World building templates

- **characterSectionHeading** (precedes the characters)
- **characterTemplate** (applied to each character)
- **locationSectionHeading** (precedes the locations)
- **locationTemplate** (applied to each location)
- **itemSectionHeading** (precedes the items)
- **itemTemplate** (applied to each item)



## Placeholders

### Syntax

There are two options:

1. `$Placeholder` -- If the placeholder is followed by a character that is clearly recognizable as a separator, e.g. a blank. 
2. `${Placeholder}` -- If the placeholder is followed by a character that is not recognizable as a separator.


### "Project template" placeholders

- **$Title** - Project title
- **$Desc** - Project description, html-formatted
- **$AuthorName** - Author's name
- **$AuthorBio** - Information about the author


- **$FieldTitle1** - Rating names: field 1
- **$FieldTitle2** - Rating names: field 2
- **$FieldTitle3** - Rating names: field 3
- **$FieldTitle4** - Rating names: field 4

- **$Language** - Language code acc. to ISO 639-1
- **$Country** - Country code acc. to ISO 3166-2

### "Chapter template" placeholders

- **$ID** - Chapter ID,
- **$ChapterNumber** - Chapter number (in sort order),

- **$Title** - Chapter title
- **$Desc** - Chapter description, html-formatted

- **$Language** - Language code acc. to ISO 639-1
- **$Country** - Country code acc. to ISO 3166-2

### "Section template" placeholders

- **$ID** - Section ID,
- **$SectionNumber** - Section number (in sort order),

- **$Title** - Section title
- **$Desc** - Section description, html-formatted

- **$WordCount** - Section word count
- **$WordsTotal** - Accumulated word count including the current section

- **$Status** - Section completion status (Outline, Draft etc.)
- **$SectionContent** - Section content

- **$Date** - Specific section date (yyyy-mm-dd)
- **$Time** - Time section begins: (hh:mm)
- **$OdsTime** - Time section begins: (PThhHmmMssS)
- **$Day** - Day section begins 
 
- **$ScDate** - Date or day (localized)

- **$DateYear** - Year
- **$DateMonth** - Month (number) 
- **$DateDay** - Day (number)
- **$DateWeekday** - Day of the week (name)
- **$MonthName** - Month (name)

- **$LastsDays** - Amount of time section lasts: days
- **$LastsHours** - Amount of time section lasts: hours
- **$LastsMinutes** - Amount of time section lasts: minutes

- **Duration** - Combination of days and hours and minutes

- **$ReactionSection** - A(ction) or R(eaction)
- **$Goal** - The section protagonist's goal, html-formatted
- **$Conflict** - The section conflict, html-formatted
- **$Outcome** - The section outcome, html-formatted
- **$Tags** - Comma-separated list of section tags

- **$Characters** - Comma-separated list of characters assigned to the section
- **$Viewpoint** - Viewpoint character
- **$Locations** - Comma-separated list of locations assigned to the section
- **$Items** - Comma-separated list of items assigned to the section

- **$Notes** - Section notes

- **$Language** - Language code acc. to ISO 639-1
- **$Country** - Country code acc. to ISO 3166-2


### "Character template" placeholders

- **$ID** - Character ID

- **$Title** - Character's name
- **$FullName** - Character's full name)
- **$AKA** - Alternative name

- **$Status** - Major/minor character
- **$Tags** - Character tags

- **$Desc** - Character description
- **$Bio** - The character's biography
- **$Goals** - The character's goals in the story
- **$Notes** - Character notes)

### "Location template" placeholders

- **$ID** - Location ID

- **$Title** - Location's name
- **$AKA** - Alternative name
- **$Desc** - Location description
- **$Tags** - Location tags

### "Item template" placeholders

- **$ID** - Item ID

- **$Title** - Item's name
- **$AKA** - Alternative name
- **$Desc** - Item description
- **$Tags** - Item tags
