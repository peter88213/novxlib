"""Provide a generic filter class for template-based file export.

All specific filters inherit from this class.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""


class Filter:
    """Filter an entity (chapter/section/character/location/item) by filter criteria.
    
    Strategy class, implementing filtering criteria for template-based export.
    This is a stub with no filter criteria specified.
    """

    def accept(self, source, eId):
        """Check whether an entity matches the filter criteria.
        
        Positional arguments:
            source -- File instance holding the entity to check.
            eId -- ID of the entity to check.       
        
        Return True if the entity is not to be filtered out.
        This is a stub to be overridden by subclass methods implementing filters.
        """
        return True

