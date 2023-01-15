#!/usr/bin/env python

import os
import sys

import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.abspath('..'))

from mmttk import PlaceholderEntry

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

for phe in phes:
    phe.pack(side='top',fill='x',expand=1)

mw.mainloop()
