"""Provide a class for ODS section list export.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import SECTIONLIST_SUFFIX
from novxlib.novx_globals import _
from novxlib.ods.ods_writer import OdsWriter


class OdsWSectionList(OdsWriter):
    """ODS section list writer."""

    DESCRIPTION = _('Section list')
    SUFFIX = SECTIONLIST_SUFFIX

    # Column width:
    # co1 2.000cm
    # co2 3.000cm
    # co3 4.000cm
    # co4 8.000cm

    # Header structure:
    # Section link
    # Section title
    # Section description
    # Date
    # Time
    # Tags
    # Section notes
    # A/R
    # Goal
    # Conflict
    # Outcome
    # Section
    # Words total
    # Word count
    # Characters
    # Locations
    # Items

    _fileHeader = f'''{OdsWriter._CONTENT_XML_HEADER}{DESCRIPTION}" table:style-name="ta1" table:print="false">
    <table:table-column table:style-name="co1" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co3" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co4" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co2" table:default-cell-style-name="ce2"/>
    <table:table-column table:style-name="co1" table:default-cell-style-name="ce4"/>
    <table:table-column table:style-name="co3" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co4" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co1" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co4" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co4" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co4" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co1" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co1" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co1" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co3" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co3" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co3" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co1" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co1" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co3" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co3" table:default-cell-style-name="Default"/>
    <table:table-column table:style-name="co3" table:default-cell-style-name="Default"/>
    <table:table-row table:style-name="ro1" table:visibility="collapse">
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Section link</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Section title</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Section description</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="ce1" office:value-type="string">
      <text:p>Date</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="ce3" office:value-type="string">
      <text:p>Time</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Tags</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Section notes</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>A/R</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Goal</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Conflict</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Outcome</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Section</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Words total</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Word count</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Characters</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Locations</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>Items</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" table:number-columns-repeated="1003"/>
    </table:table-row>
    <table:table-row table:style-name="ro1">
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Section link")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Section title")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Section description")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="ce1" office:value-type="string">
      <text:p>{_("Date")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="ce3" office:value-type="string">
      <text:p>{_("Time")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Tags")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Section notes")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("A/R")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Goal")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Conflict")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Outcome")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Section")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Words total")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Word count")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Characters")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Locations")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" office:value-type="string">
      <text:p>{_("Items")}</text:p>
     </table:table-cell>
     <table:table-cell table:style-name="Heading" table:number-columns-repeated="1003"/>
    </table:table-row>

'''

    _sectionTemplate = '''   <table:table-row table:style-name="ro2">
     <table:table-cell table:formula="of:=HYPERLINK(&quot;file:///$ProjectPath/$ProjectName$ManuscriptSuffix.odt#$ID%7Cregion&quot;;&quot;$ID&quot;)" office:value-type="string" office:string-value="$ID">
      <text:p>$ID</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="string">
      <text:p>$Title</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="string">
      <text:p>$Desc</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="date" office:date-value="$Date">
      <text:p>$Date</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="time" office:time-value="$OdsTime">
      <text:p>$scTime</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="string">
      <text:p>$Tags</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="string">
      <text:p>$Notes</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="string">
      <text:p>$ReactionSection</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="string">
      <text:p>$Goal</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="string">
      <text:p>$Conflict</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="string">
      <text:p>$Outcome</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="float" office:value="$SectionNumber">
      <text:p>$SectionNumber</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="float" office:value="$WordsTotal">
      <text:p>$WordsTotal</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="float" office:value="$WordCount">
      <text:p>$WordCount</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="string">
      <text:p>$Characters</text:p>
     </table:table-cell>
     <table:table-cell office:value-type="string">
      <text:p>$Locations</text:p>
     </table:table-cell>
     <table:table-cell>
      <text:p>$Items</text:p>
     </table:table-cell>
    </table:table-row>

'''

    _fileFooter = OdsWriter._CONTENT_XML_FOOTER

