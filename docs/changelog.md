# Changelog

### v4.5.3

- Fix a regression from v4.5.2 where "None" values in dictionary type properties may raise exceptions.

### v4.5.2

- Validating model object property types.

### v4.5.1

- Prevent overwriting novx files with incomplete XML structures in case of conversion errors. 

### v4.5.0

- Add a "Chapter beginning" paragraph style for export.
- Translate the custom ODT style names.

### v4.4.2

- Prevent overwriting an existing localization when importing novx_globals.

### v4.4.1

- Fix a bug where on_element_change() is not called when Novel.referenceDate is set to None.

### v4.4.0

- Use the customized field titles for document export.

### v4.3.0

- Provide a moonphase module.
- Provide new helper functions for date calculation.
- Refactor.

### v4.2.2

Verify XML input:
- Check whether project notes IDs start with the correct prefix.

### v4.2.1

Verify XML input:
- Check whether IDs start with the correct prefix.

### v4.2.0

Verify XML input:
- ISO-formatted date
- ISO-formatted time
- Strings representing numbers

### v4.1.0

- Add novxService class.

### v4.0.2

- Fix a bug where the Section "scene" attribute is falisfied when being read from XML. 

### v4.0.1

- Refactor, changing the API.

#### DTD 1.4

- Fix errors from DTD 1.3.
- Introduce a new SECTION attribute scene (0: Not a scene, 1: Action scene, 2: Reaction scene, 3: Other scene). 
- Remove the PlotNotes element and promote PlotlineNotes.
- Make the path and full path subelements of Link. This is because the
values may contain spaces, so they cannot be NMTOKEN attributes.

### v3.7.4

- When parsing ODT, skip redundant language tags.
- Refactor the OdtParser and OdsParser classes.

### v3.7.3

- Do not write xml elements for empty plot notes.
- Change the ODT "ViewLayoutColumns" setting to single page.
- Update css: Render comment as block element.

### v3.7.2

- Refactor: Undo some changes from v3.7.1.

### v3.7.1

- Fix a regression from v3.6.0 where data export raises an exception when trying to get the timestamp.
- Fix a suspected bug in the NvTree.insert() method.
- Refactor: Simplify control structures; return early.

### v3.7.0

- Refactor, making the list intersection a global function.

### v3.6.0

- Refactor, moving the XML read/write routines from NovxFile to the model elements.
- Refactor, adding some novelibre NvModel features to NovxFile.
- Check the novx xml root tag.

### v3.5.4

- Slightly refactor the XML indent helper function. 

### v3.5.3

- Fix a bug where scenes might get lost during splitting, if split markers are not placed as intended. 

### v3.5.2

- Have Converter set the default locale when creating a new project.

### v3.5.1

- Indent the novx files up to the content paragraph level, but not inline elements within paragraphs.

### v3.5.0

No longer pretty-print the novx xml files.

This fixes a bug where single spaces between emphasized text in section content are lost.

### v3.4.1

- Update plot line hyperlinks in the plotlist.
- Add plot line hyperlinks to the plot grid.
- Do not insert section dividers when using stage templates in file export.
- Update test data.

### v3.4.0

New document types:

- Story structure export and import.
- Plot line descriptions export and import.

### v3.3.0

Store links with a fallback path (#10).

- Update DTD version to 1.3
- Update the BasicElements.links setter method.
- Read and write the additional full link path in NovxFile.

### v3.2.0

Store notes with all elements except project notes (#7).
Store links with all elements (#8).

- Update DTD version to 1.2.
- Add "Notes" to the FileExport mapping dictionaries (#7).

Change the model class hierarchy.

- New class: BasicElementNotes(BasicElement)
- New class: BasicElementTags(BasicElementNotes)
- WorldElement gets notes.

Refactor the NovxFile read and write methods.

### v3.1.0

- Add Section.STATUS class constant.
- Update section list structure.
- Import tags from Plot Grid even if empty.

### v3.0.1

- Provide weekday names and month names for all languages.
- Use the isleap() function from the standard calendar module.

### v3.0.0

Provide local date format for display

- Make Section.weekDay a property.
- New property Section.localeDate
- Reset date and day to None instead to empty string.
- Use localized date and "Day" translation for the "ScDate" file export placeholder.
- Add date-related placeholders for the section export.
- Restore the novx to shortcode conversion parser.

### v2.0.1

- Fix a bug where imported sections are split at the 
  "####" mark, but not appended as they should. 

### v2.0.0

- Fix a regression from v1.5.0 where faulty plot lists are generated. 
- Refactor the code for novelibre v3.0 API.
- Remove the yw7 file format support.

### v1.5.0

- Update DTD to v1.1: Add section arc notes.
- Add notes to the section for each associated arc.
- Provide an ODS Plot grid for export and import.
- Make the ODS Section list export-only.
- Rewording: Arc -> Plot line.

### v1.4.2

- Provide translated headers for ODS export.

### v1.4.1

- More robust ODS file reading.

### v1.4.0

- Add date/time information to the section list.
- Extend the ODS table validation when writing back.  

### v1.3.1

- Replace the "Segoe UI 10" font with "Calibri 10.5"
  for ODF document export.
- Fix a bug where links do not work in the ODS plot list 
  if scene titles contain false double quotes.
  
### v1.3.0

- Initialize Arc.sections with optional parameter.
- Refactor: Replace "Turning point" with "Plot point" without affecting the API.

### v1.2.1

- Catch odt parsing errors.

### v1.2.0

- Make the FileExport filter instance variables "public".
- Prepare all odt document types for filtering on export.

### v1.1.0

- Provide character age calculation.

### v1.0.1

- Fix a bug where turning points appear in the wrong ods 
  and html table columns.

### v1.0.0

- Release under the LGPLv3 license.

Based on novxlib-Alpha v0.30.0
