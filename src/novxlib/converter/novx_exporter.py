"""Provide a converter class for universal export from a novelibre project. 

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novelibre
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from nvlib.model.converter.converter_ff import ConverterFf
from nvlib.model.novx.novx_file import NovxFile
from nvlib.model.ods.ods_w_charlist import OdsWCharList
from nvlib.model.ods.ods_w_grid import OdsWGrid
from nvlib.model.ods.ods_w_itemlist import OdsWItemList
from nvlib.model.ods.ods_w_loclist import OdsWLocList
from nvlib.model.ods.ods_w_plot_list import OdsWPlotList
from nvlib.model.ods.ods_w_sectionlist import OdsWSectionList
from nvlib.model.odt.odt_w_brief_synopsis import OdtWBriefSynopsis
from nvlib.model.odt.odt_w_chapterdesc import OdtWChapterDesc
from nvlib.model.odt.odt_w_characters import OdtWCharacters
from nvlib.model.odt.odt_w_export import OdtWExport
from nvlib.model.odt.odt_w_items import OdtWItems
from nvlib.model.odt.odt_w_locations import OdtWLocations
from nvlib.model.odt.odt_w_manuscript import OdtWManuscript
from nvlib.model.odt.odt_w_partdesc import OdtWPartDesc
from nvlib.model.odt.odt_w_plotlines import OdtWPlotlines
from nvlib.model.odt.odt_w_proof import OdtWProof
from nvlib.model.odt.odt_w_sectiondesc import OdtWSectionDesc
from nvlib.model.odt.odt_w_stages import OdtWStages
from nvlib.model.odt.odt_w_xref import OdtWXref


class NovxExporter(ConverterFf):
    """A converter for universal export from a novelibre project.

    Instantiate a NovxFile object as sourceFile and a
    Novel subclass object as targetFile for file conversion.

    Overrides the superclass constants EXPORT_SOURCE_CLASSES, EXPORT_TARGET_CLASSES.    
    """
    EXPORT_SOURCE_CLASSES = [NovxFile]
    EXPORT_TARGET_CLASSES = [
        OdsWCharList,
        OdsWGrid,
        OdsWItemList,
        OdsWLocList,
        OdsWPlotList,
        OdsWSectionList,
        OdtWBriefSynopsis,
        OdtWChapterDesc,
        OdtWCharacters,
        OdtWExport,
        OdtWItems,
        OdtWLocations,
        OdtWManuscript,
        OdtWPartDesc,
        OdtWPlotlines,
        OdtWProof,
        OdtWSectionDesc,
        OdtWStages,
        OdtWXref,
    ]
