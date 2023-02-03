#!/usr/bin/env python

# Author: Michael A. Mayer
# Copyright: 2023, VMWishes
# License: UNLICENSE (http://unlicense.org)

import tkinter as tk
from tkinter import ttk

from demo import Demo
from mmtk import PlaceholderEntry

class PlaceholderEntryDemo(Demo):

    def _build(self):
        self._add("Enter Userid")
        self._add("Enter Password",show='#')
        self._add("Red Example",placeholder_color="red")
        self._add("Not Italic Example",placeholder_italic=False)

        alt_font = {'family':'courier', 'size':18}
        self._add("Alternate Font",placeholder_font=alt_font)

    def _add(self,placeholder,**kwargs):
        PlaceholderEntry(
            self.frame,
            placeholder,
            **kwargs
        ).pack(
            side="top",
            fill="x",
            expand=False,
        )

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath('..'))
    mw = tk.Tk()
    PlaceholderEntryDemo(mw)
    mw.mainloop()
