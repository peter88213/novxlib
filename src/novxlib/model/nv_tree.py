"""Provide a class for a noveltree project tree substitute.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.novx_globals import AC_ROOT
from novxlib.novx_globals import ARC_PREFIX
from novxlib.novx_globals import CHAPTER_PREFIX
from novxlib.novx_globals import CH_ROOT
from novxlib.novx_globals import CR_ROOT
from novxlib.novx_globals import IT_ROOT
from novxlib.novx_globals import LC_ROOT
from novxlib.novx_globals import PN_ROOT


class NvTree:
    """noveltree project structure, emulating the ttk.Treeview interface.
    
    This allows independence from the tkinter library.
    """

    def __init__(self):
        self.roots = {
            CH_ROOT:[],
            CR_ROOT:[],
            LC_ROOT:[],
            IT_ROOT:[],
            AC_ROOT:[],
            PN_ROOT:[],
            }
        # values : listed children's IDs
        self.srtSections = {}
        # key: chapter ID
        # value : section ID
        self.srtTurningPoints = {}
        # key: arc ID
        # value : turning point ID

    def append(self, parent, iid):
        """Creates a new item with identifier iid."""
        if parent in self.roots:
            self.roots[parent].append(iid)
            if parent == CH_ROOT:
                self.srtSections[iid] = []
            elif parent == AC_ROOT:
                self.srtTurningPoints[iid] = []
        elif parent.startswith(CHAPTER_PREFIX):
            try:
                self.srtSections[parent].append(iid)
            except:
                self.srtSections[parent] = [iid]
        elif parent.startswith(ARC_PREFIX):
            try:
                self.srtTurningPoints[parent].append(iid)
            except:
                self.srtTurningPoints[parent] = [iid]

    def delete(self, *items):
        """Delete all specified items and all their descendants. The root
        item may not be deleted."""
        raise NotImplementedError

    def delete_children(self, parent):
        """Delete all parent's descendants."""
        if parent in self.roots:
            self.roots[parent] = []
            if parent == CH_ROOT:
                self.srtSections = {}
            elif parent == AC_ROOT:
                self.srtTurningPoints = {}
        elif parent.startswith(CHAPTER_PREFIX):
            self.srtSections[parent] = []
        elif parent.startswith(ARC_PREFIX):
            self.srtTurningPoints[parent] = []

    def get_children(self, item):
        """Returns the list of children belonging to item."""
        if item in self.roots:
            return self.roots[item]

        elif item.startswith(CHAPTER_PREFIX):
            return self.srtSections.get(item, [])

        elif item.startswith(ARC_PREFIX):
            return self.srtTurningPoints.get(item, [])

    def index(self, item):
        """Return the integer index of item within its parent's list
        of children."""
        raise NotImplementedError

    def insert(self, parent, index, iid):
        """Create a new item with identifier iid."""
        if parent in self.roots:
            self.roots[parent].insert(index, iid)
            if parent == CH_ROOT:
                self.srtSections[iid] = []
            elif parent == AC_ROOT:
                self.srtTurningPoints[iid] = []
        elif parent.startswith(CHAPTER_PREFIX):
            try:
                self.srtSections[parent].insert(index, iid)
            except:
                self.srtSections[parent] = [iid]
        elif parent.startswith(ARC_PREFIX):
            try:
                self.srtTurningPoints.insert(index, iid)
            except:
                self.srtTurningPoints[parent] = [iid]

    def move(self, item, parent, index):
        """Move item to position index in parent's list of children.

        It is illegal to move an item under one of its descendants. If
        index is less than or equal to zero, item is moved to the
        beginning, if greater than or equal to the number of children,
        it is moved to the end. If item was detached it is reattached.
        """
        raise NotImplementedError

    def next(self, item):
        """Return the identifier of item's next sibling, or '' if item
        is the last child of its parent."""
        raise NotImplementedError

    def parent(self, item):
        """Return the ID of the parent of item, or '' if item is at the
        top level of the hierarchy."""
        raise NotImplementedError

    def prev(self, item):
        """Return the identifier of item's previous sibling, or '' if
        item is the first child of its parent."""
        raise NotImplementedError

    def reset(self):
        """Clear the tree."""
        for item in self.roots:
            self.roots[item] = []
        self.srtSections = {}
        self.srtTurningPoints = {}

    def set_children(self, item, newchildren):
        """Replaces item’s child with newchildren."""
        if item in self.roots:
            self.roots[item] = newchildren[:]
            if item == CH_ROOT:
                self.srtSections = {}
            elif item == AC_ROOT:
                self.srtTurningPoints = {}
        elif item.startswith(CHAPTER_PREFIX):
            self.srtSections[item] = newchildren[:]
        elif item.startswith(ARC_PREFIX):
            self.srtTurningPoints[item] = newchildren[:]


if __name__ == '__main__':
    thisTree = NvTree()
