"""Provide a facade class for a Tkinter based GUI.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from tkinter import messagebox

from novxlib.novx_globals import _
from novxlib.ui.ui import Ui
import tkinter as tk


class UiTk(Ui):
    """UI subclass implementing a Tkinter facade.
    
    Public instance variables: 
        root -- tk root window.
    """

    def __init__(self, title):
        """Initialize the GUI window.
        
        Positional arguments:
            title -- application title to be displayed at the window frame.
            
        Extends the superclass constructor.
        """
        super().__init__(title)
        self.title = title
        self.root = tk.Tk()
        self.root.minsize(400, 150)
        self.root.resizable(width='false', height='false')
        self.root.title(title)
        self._appInfo = tk.Label(self.root, text='')
        self._appInfo.pack(padx=20, pady=5)
        self._processInfo = tk.Label(self.root, text='', padx=20)
        self._processInfo.pack(pady=20, fill='both')
        self.root.quitButton = tk.Button(text=_("Quit"), command=quit)
        self.root.quitButton.config(height=1, width=10)
        self.root.quitButton.pack(pady=10)

    def ask_yes_no(self, text):
        """Query yes or no with a pop-up box.
        
        Positional arguments:
            text -- question to be asked in the pop-up box. 
            
        Overrides the superclass method.       
        """
        return messagebox.askyesno(_("WARNING"), text)

    def set_status(self, message):
        """Show how the converter is doing.
        
        Positional arguments:
            message -- message to be displayed. 
            
        Display the message at the _processinfo label.
        Overrides the superclass method.
        """
        if message.startswith('!'):
            self._processInfo.config(bg='red')
            self._processInfo.config(fg='white')
            self.infoHowText = message.split('!', maxsplit=1)[1].strip()
        else:
            self._processInfo.config(bg='green')
            self._processInfo.config(fg='white')
            self.infoHowText = message
        self._processInfo.config(text=self.infoHowText)

    def set_info(self, message):
        """Show what the converter is going to do.
        
        Positional arguments:
            message -- message to be displayed. 
            
        Display the message at the _appinfo label.
        Overrides the superclass method.
        """
        self.infoWhatText = message
        self._appInfo.config(text=message)

    def show_open_button(self, open_cmd):
        """Add an 'Open' button to the main window.
        
        Positional argument:
            open_cmd -- subclass method that opens the file.
        """
        self.root.openButton = tk.Button(text=_("Open"), command=open_cmd)
        self.root.openButton.config(height=1, width=10)
        self.root.openButton.pack(pady=10)

    def show_warning(self, message):
        """Display a warning message box."""
        messagebox.showwarning(self.title, message)

    def start(self):
        """Start the Tk main loop."""
        self.root.mainloop()

