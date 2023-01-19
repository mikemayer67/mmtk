#!/usr/bin/env python

import os
import sys

import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.abspath('..'))

from mmttk import PlaceholderEntry
from mmttk import StatusLabel

mw = tk.Tk()

f = ttk.Frame(mw,width=200,height=100)
f.pack(fill='both',expand=True)

phes = (
    PlaceholderEntry(f,"Enter Userid"),
    PlaceholderEntry(f,"Enter Password",show='#'),
    PlaceholderEntry(f,"Red Example",placeholder_color="red"),
    PlaceholderEntry(f,"Not Italic Example",placeholder_italic=False),
    PlaceholderEntry(f,"Alternate Font",placeholder_font={
        'family':'courier', 
        'size':18,
    }),
)

full_row = {"side":"top", "fill":"x", "expand":False}

for phe in phes:
    phe.pack(**full_row)

ttk.Frame(f,height=5).pack(**full_row)

status = StatusLabel(f)
status.pack(**full_row)

ttk.Frame(f,height=5).pack(**full_row)

ff = ttk.Frame(f)
ff.pack(**full_row)

def set_info():
    status.info("Just to let you know")

def set_warning():
    status.warning("This doesn't look good")

def set_error():
    status.error("Oh shit... Now look what you've done")

def clear():
    status.clear()

ttk.Button(
    ff,
    text="Info",
    command=set_info,
).pack(side="left")
ttk.Button(
    ff,
    text="Warn",
    command=set_warning,
).pack(side="left")
ttk.Button(
    ff,
    text="Error",
    command=set_error,
).pack(side="left")
ttk.Button(
    ff,
    text="Clear",
    command=clear,
).pack(side="left")


mw.mainloop()
