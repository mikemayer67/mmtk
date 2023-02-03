#!/usr/bin/env python

# Author: Michael A. Mayer
# Copyright: 2023, VMWishes
# License: UNLICENSE (http://unlicense.org)

import tkinter as tk
from tkinter import ttk

from demo_placeholderentry import PlaceholderEntryDemo
from demo_statuslabel import StatusLabelDemo

mw = tk.Tk()

f = ttk.Frame(mw)
f.pack(side="top",fill="both",expand=False)

s = ttk.Style()
def set_theme(theme):
    s.theme_use(theme)

themes = s.theme_names()
cur_theme = s.theme_use()
theme_menu = ttk.OptionMenu(f,tk.StringVar(),cur_theme,*themes,command=set_theme)
theme_menu.pack(side="right",expand=False,padx=8)
ttk.Label(f,text="Theme:").pack(side="right",expand=False)

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

