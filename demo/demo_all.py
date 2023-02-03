#!/usr/bin/env python

# Author: Michael A. Mayer
# Copyright: 2023, VMWishes
# License: UNLICENSE (http://unlicense.org)

import tkinter as tk
from tkinter import ttk

from demo_placeholderentry import PlaceholderEntryDemo
from demo_statuslabel import StatusLabelDemo

mw = tk.Tk()

nb = ttk.Notebook(mw)
nb.pack(side="top", fill="both",expand=True)

f = ttk.Frame(nb)
f.pack(fill="both",expand=True)
nb.add(f,text="PlaceholderEntry")
phe = PlaceholderEntryDemo(f)

f = ttk.Frame(nb)
f.pack(fill="both",expand=True)
nb.add(f,text="StatusLabel")
phe = StatusLabelDemo(f)

mw.mainloop()

