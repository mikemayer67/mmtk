#!/usr/bin/env python

import tkinter as tk
from tkinter import ttk

from mmttk import PlaceholderEntry

mw = tk.Tk()

f = ttk.Frame(mw,width=200,height=100)
f.pack(fill='both',expand=True)

phe1 = PlaceholderEntry(f,placeholder="Enter Userid")
phe2 = PlaceholderEntry(f,placeholder="Enter Password",show='#')

phe1.pack(side='top',fill='x',expand=1)
phe2.pack(side='top',fill='x',expand=1)

mw.mainloop()
