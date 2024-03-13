# Changelog


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
