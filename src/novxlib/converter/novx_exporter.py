"""Provide a converter class for universal export from a novelibre project. 

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.converter.converter_ff import ConverterFf
from novxlib.novx.novx_file import NovxFile
from novxlib.odt.odt_w_proof import OdtWProof
from novxlib.odt.odt_w_manuscript import OdtWManuscript
from novxlib.odt.odt_w_sectiondesc import OdtWSectionDesc
from novxlib.odt.odt_w_chapterdesc import OdtWChapterDesc
from novxlib.odt.odt_w_partdesc import OdtWPartDesc
from novxlib.odt.odt_w_brief_synopsis import OdtWBriefSynopsis
from novxlib.odt.odt_w_export import OdtWExport
from novxlib.odt.odt_w_characters import OdtWCharacters
from novxlib.odt.odt_w_items import OdtWItems
from novxlib.odt.odt_w_locations import OdtWLocations
from novxlib.odt.odt_w_xref import OdtWXref
from novxlib.odt.odt_w_plot import OdtWPlot
from novxlib.ods.ods_w_charlist import OdsWCharList
from novxlib.ods.ods_w_loclist import OdsWLocList
from novxlib.ods.ods_w_itemlist import OdsWItemList
from novxlib.ods.ods_w_sectionlist import OdsWSectionList
from novxlib.ods.ods_w_plot_list import OdsWPlotList


class NovxExporter(ConverterFf):
    """A converter for universal export from a novelibre project.

    Instantiate a NovxFile object as sourceFile and a
    Novel subclass object as targetFile for file conversion.

    Overrides the superclass constants EXPORT_SOURCE_CLASSES, EXPORT_TARGET_CLASSES.    
    """
    EXPORT_SOURCE_CLASSES = [NovxFile]
    EXPORT_TARGET_CLASSES = [OdtWProof,
                             OdtWManuscript,
                             OdtWBriefSynopsis,
                             OdtWSectionDesc,
                             OdtWChapterDesc,
                             OdtWPartDesc,
                             OdtWExport,
                             OdtWCharacters,
                             OdtWItems,
                             OdtWLocations,
                             OdtWXref,
                             OdtWPlot,
                             OdsWCharList,
                             OdsWLocList,
                             OdsWItemList,
                             OdsWSectionList,
                             OdsWPlotList,
                             ]
