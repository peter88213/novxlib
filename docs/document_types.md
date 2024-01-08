# Document types

The document types are recognized by a suffix added to the noveltree project name.

_Example_ 

- noveltree project file name = `normal.novx`
- Exported manuscript file name = `normal_manuscript_tmp.odt`

## General

-   [Document language](#document-language)

## Export from noveltree

### Generate ODT (text document)

-   [Export chapters and sections](#export-chapters-and-sections) -- no suffix
-   [Export chapters and sections for proof reading](#export-chapters-and-sections-for-proof-reading) -- suffix = `_proof_tmp`
-   [Export manuscript with chapter and section sections](#export-manuscript-with-chapter-and-section-sections) -- suffix = `_manuscript_tmp`
-   [Export section descriptions](#export-section-descriptions) -- suffix = `_sections_tmp`
-   [Export chapter descriptions](#export-chapter-descriptions) -- suffix = `_chapters_tmp`
-   [Export part descriptions](#export-part-descriptions) -- suffix = `_parts_tmp`
-   [Export character descriptions](#export-character-descriptions) -- suffix = `_characters_tmp`
-   [Export location descriptions](#export-location-descriptions) -- suffix = `_locations_tmp`
-   [Export item descriptions](#export-item-descriptions) -- suffix = `_items_tmp`
-   [Export cross reference](#export-cross-reference) -- suffix = `_xref`
-   [Export brief synopsis](#export-brief-synopsis) -- suffix = `_brf_synopsis`


### Generate ODS (spreadsheet document)

-   [Export character list](#export-character-list) -- suffix = `_charlist_tmp`
-   [Export location list](#export-location-list) -- suffix = `_loclist_tmp`
-   [Export item list](#export-item-list) -- suffix = `_itemlist_tmp`
-   [Export section list](#export-section-list) -- suffix = `_sectionlist_tmp`

## Import to an existing noveltree project

### Source: ODT file (text document)

-   [Import chapters and sections for proof reading](#import-chapters-and-sections-for-proof-reading) -- suffix = `_proof`
-   [Import manuscript with chapter and section sections](#import-manuscript-with-chapter-and-section-sections) -- suffix = `_manuscript`
-   [Import section descriptions](#import-section-descriptions) -- suffix = `_sections_tmp`
-   [Import chapter descriptions](#import-chapter-descriptions) -- suffix = `_chapters_tmp`
-   [Import part descriptions](#import-part-descriptions) -- suffix = `_parts_tmp`
-   [Import character descriptions](#import-character-descriptions) -- suffix = `_characters_tmp`
-   [Import location descriptions](#import-location-descriptions) -- suffix = `_locations_tmp`
-   [Import item descriptions](#import-item-descriptions) -- suffix = `_items_tmp`

### Source: ODS file (spreadsheet document)

-   [Import character list](#import-character-list) -- suffix = `_charlist_tmp`
-   [Import location list](#import-location-list) -- suffix = `_loclist_tmp`
-   [Import item list](#import-item-list) -- suffix = `_itemlist_tmp`
-   [Import section list](#import-section-list) -- suffix = `_sectionlist_tmp`
-   [Import plot list](#import-plot-list) -- suffix = `_plotlist`

## Create a new noveltree project

### Source: ODT file (text document)

-   [Import work in progress](#import-work-in-progress) -- no suffix
-   [Import outline](#import-outline) -- no suffix


------------------------------------------------------------------------

## General

### Document language

ODF documents are generally assigned a language that determines spell checking and country-specific character substitutions. In addition, Office Writer lets you assign text passages to languages other than the document language to mark foreign language usage or to suspend spell checking. 

#### Document overall

- If a document language (Language code acc. to ISO 639-1 and country code acc. to ISO 3166-2) is detected in the source document during conversion to *noveltree* format, these codes are set as noveltree project variables. 

- If language code and country code exist as project variables during conversion from *noveltree* format, they are inserted into the generated ODF document. 

- If no language and country code exist as project variables when converting from *noveltree* format, language and country code from the operating system settings are entered into the generated ODF document. 

- The language and country codes are checked superficially. If they obviously do not comply with the ISO standards, they are replaced by the values for "No language". These are:
    - Language = zxx
    - Country = none


[Top of page](#top)


## Export chapters and sections

Write noveltree chapters and sections into a new OpenDocument
text document (odt).

-   The document is placed in the same folder as the project.
-   Document's **filename**: `<project name>.odt`.
-   Only "normal" chapters and sections are exported. Chapters and
    Sections of the "Unused" type are not exported.
-   Part titles appear as first level heading.
-   Chapter titles appear as second level heading.
-   Sections are separated by `* * *`. The first line is not
    indented.
-   Starting from the second paragraph, paragraphs begin with
    indentation of the first line.
-   Sections marked "attach to previous section" appear like
    continuous paragraphs.


[Top of page](#top)

------------------------------------------------------------------------

## Export chapters and sections for proof reading

Write noveltree chapters and sections into a new OpenDocument
text document (odt) with section markers. File name suffix is
`_proof_tmp`.

-   Only "normal" chapters and sections are exported. Chapters and
    Sections of the "Unused" type are not exported.
-   The document contains section `[sc...]` markers. **Do not touch lines
    containing the markers** if you want to be able to write the
    document back to *noveltree* format.
-   The document contains part, chapter, and section headings. However, changes will not be written back.
-   Chapters and sections can neither be rearranged nor deleted. 
-   When editing the document, you can split sections by inserting headings or a section divider:
    -   *Heading 1* → New part title. Optionally, you can add a description, separated by `|`.
    -   *Heading 2* → New chapter title. Optionally, you can add a description, separated by `|`.
    -   `###` → Section divider. Optionally, you can append the 
        section title to the section divider. You can also add a description, separated by `|`.
-   Text markup: Bold and italics are re-imported. Other highlighting such
    as underline and strikethrough are lost.


[Top of page](#top)

------------------------------------------------------------------------

## Export manuscript with invisible section marks

Write noveltree chapters and sections into a new OpenDocument
text document (odt) with sections (to be seen in the Navigator). 
File name suffix is `_manuscript_tmp`.

-   Only "normal" chapters and sections are exported. Chapters and
    Sections of the "Unused" type are not exported.
-   Part titles appear as first level heading.
-   Chapter titles appear as second level heading.
-   Chapters and sections can neither be rearranged nor deleted.
-   With *OpenOffice/LibreOffice Writer*, you can split sections by inserting headings or a section divider:
    -  *Heading 1* → New part title. Optionally, you can add a description, separated by `|`.
    -  *Heading 2* → New chapter title. Optionally, you can add a description, separated by `|`.
    -  `###` → Section divider. Optionally, you can append the 
       section title to the section divider. You can also add a description, separated by `|`.
-   Text markup: Bold and italics are re-imported. Other highlighting such
    as underline and strikethrough are lost.

[Top of page](#top)

------------------------------------------------------------------------

## Export section descriptions

Generate a new OpenDocument text document (odt) containing chapter
titles and section descriptions that can be edited and written back to
noveltree format. File name suffix is
`_sections_tmp`.

[Top of page](#top)

------------------------------------------------------------------------

## Export chapter descriptions

Generate a new OpenDocument text document (odt) containing chapter
titles and chapter descriptions that can be edited and written back to
noveltree format. File name suffix is
`_chapters_tmp`.

[Top of page](#top)

------------------------------------------------------------------------

## Export part descriptions

Generate a new OpenDocument text document (odt) containing part titles
and part descriptions that can be edited and written back to noveltree
format. File name suffix is
`_parts_tmp`.


[Top of page](#top)

------------------------------------------------------------------------

## Export character descriptions

Generate a new OpenDocument text document (odt) containing
character descriptions, bio, goals, and notes that can be edited in Office
Writer and written back to noveltree format. File name suffix is
`_characters_tmp`.

[Top of page](#top)

------------------------------------------------------------------------

## Export location descriptions

Generate a new OpenDocument text document (odt) containing
location descriptions that can be edited in Office Writer and written
back to noveltree format. File name suffix is `_locations_tmp`.

[Top of page](#top)

------------------------------------------------------------------------

## Export item descriptions

Generate a new OpenDocument text document (odt) containing
item descriptions that can be edited in Office Writer and written back
to noveltree format. File name suffix is `_items_tmp`.

[Top of page](#top)

------------------------------------------------------------------------

## Export cross reference

Generate a new OpenDocument text document (odt) containing
navigable cross references. File name suffix is `_xref`. The cross
references are:

-   Sections per character,
-   sections per location,
-   sections per item,
-   sections per tag,
-   characters per tag,
-   locations per tag,
-   items per tag.

[Top of page](#top)

------------------------------------------------------------------------

## Export brief synopsis

Generate a brief synopsis with chapter and sections titles. File name
suffix is `_brf_synopsis`.

-   Only "normal" chapters and sections are exported. Chapters and
    sections marked "unused" are not exported.
-   Part titles appear as first level heading.
-   Chapter titles appear as second level heading.
-   Section titles appear as plain paragraphs.

[Top of page](#top)

------------------------------------------------------------------------

## Export character list

Generate a new OpenDocument spreadsheet (ods) containing a
character list that can be edited in Office Calc and written back to
noveltree format. File name suffix is `_charlist_tmp`.

You may change the sort order of the rows. You may also add or remove
rows. New entities must get a unique ID.

[Top of page](#top)

------------------------------------------------------------------------

## Export location list

Generate a new OpenDocument spreadsheet (ods) containing a
location list that can be edited in Office Calc and written back to
noveltree format. File name suffix is `_loclist_tmp`.

You may change the sort order of the rows. You may also add or remove
rows. New entities must get a unique ID.

[Top of page](#top)

------------------------------------------------------------------------

## Export item list

Generate a new OpenDocument spreadsheet (ods) containing an
item list that can be edited in Office Calc and written back to noveltree
format. File name suffix is `_itemlist_tmp`.

You may change the sort order of the rows. You may also add or remove
rows. New entities must get a unique ID.

[Top of page](#top)

------------------------------------------------------------------------

## Export section list

Generate a new OpenDocument spreadsheet (ods) listing the following:

- Hyperlink to the manuscript's section section
- Section title
- Section description
- Tags
- Section notes
- A/R
- Goal
- Conflict
- Outcome
- Sequential section number
- Words total
- Word count
- Status
- Characters
- Locations
- Items

Only "normal" sections get a row in the section list. 
Sections of the "Unused" type are omitted.

File name suffix is `_sectionlist_tmp`.

[Top of page](#top)

------------------------------------------------------------------------

## Import section list

The following columns can be written back to the noveltree project:

- Title
- Description
- Tags (comma-separated)
- Section notes
- A/R (action/reaction section)
- Goal
- Conflict
- Outcome
- Status ('Outline', 'Draft', '1st Edit', '2nd Edit', 'Done')

[Top of page](#top)

------------------------------------------------------------------------


