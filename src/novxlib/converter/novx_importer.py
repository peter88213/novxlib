"""Provide a converter class for novelibre universal import.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novelibre
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from nvlib.model.converter.converter_ff import ConverterFf
from nvlib.model.converter.new_project_factory import NewProjectFactory
from nvlib.model.novx.novx_file import NovxFile
from nvlib.model.ods.ods_r_charlist import OdsRCharList
from nvlib.model.ods.ods_r_grid import OdsRGrid
from nvlib.model.ods.ods_r_itemlist import OdsRItemList
from nvlib.model.ods.ods_r_loclist import OdsRLocList
from nvlib.model.odt.odt_r_chapterdesc import OdtRChapterDesc
from nvlib.model.odt.odt_r_characters import OdtRCharacters
from nvlib.model.odt.odt_r_items import OdtRItems
from nvlib.model.odt.odt_r_locations import OdtRLocations
from nvlib.model.odt.odt_r_manuscript import OdtRManuscript
from nvlib.model.odt.odt_r_partdesc import OdtRPartDesc
from nvlib.model.odt.odt_r_plotlines import OdtRPlotlines
from nvlib.model.odt.odt_r_proof import OdtRProof
from nvlib.model.odt.odt_r_sectiondesc import OdtRSectionDesc
from nvlib.model.odt.odt_r_stages import OdtRStages


class NovxImporter(ConverterFf):
    """A converter for universal import.

    Support novelibre projects and most of the File subclasses 
    that can be read or written by OpenOffice/LibreOffice.

    Overrides the superclass constants EXPORT_SOURCE_CLASSES,
    EXPORT_TARGET_CLASSES, IMPORT_SOURCE_CLASSES, IMPORT_TARGET_CLASSES.

    Class constants:
        CREATE_SOURCE_CLASSES -- list of classes that - additional to HtmlImport
                        and HtmlOutline - can be exported to a new novelibre project.
    """
    EXPORT_SOURCE_CLASSES = [NovxFile]
    IMPORT_SOURCE_CLASSES = [
        OdsRCharList,
        OdsRGrid,
        OdsRItemList,
        OdsRLocList,
        OdtRChapterDesc,
        OdtRCharacters,
        OdtRItems,
        OdtRLocations,
        OdtRManuscript,
        OdtRPartDesc,
        OdtRPlotlines,
        OdtRProof,
        OdtRSectionDesc,
        OdtRStages,
    ]
    IMPORT_TARGET_CLASSES = [NovxFile]
    CREATE_SOURCE_CLASSES = []

    def __init__(self):
        """Change the newProjectFactory strategy.
        
        Extends the superclass constructor.
        """
        super().__init__()
        self.newProjectFactory = NewProjectFactory(self.CREATE_SOURCE_CLASSES)
