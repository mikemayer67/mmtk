#!/usr/bin/env python

import os
import sys

import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.abspath('..'))

from mmtk import PlaceholderEntry
from mmtk import StatusLabel

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

ff = tk.Frame(f,relief="groove",borderwidth=3)
ff.pack(**full_row,padx=3,pady=3)

def get_value(v):
    xlat = {"(None)":None,"True":True,"False":False}
    for n in range(10):
        xlat[str(n)] = n
    return xlat.get(v,v)

row = 0
state_v = tk.StringVar()
state_v.set("(None)")
state_om = tk.OptionMenu(ff,state_v,"(None)","info","warning","error")
tk.Label(ff,text="state:").grid(row=row,column=0,sticky="e")
state_om.grid(row=row,column=1,sticky="w")
row += 1

config_vars = dict()

class UpdateConfig:
    def __init__(self,option):
        self.option = option
    def __call__(self,value):
        state = get_value(state_v.get())
        if not state and self.option in ("italic","bold"):
            return
        config = { (state or "") + self.option: get_value(value) }
        status.configure(**config)

#            'anchor', 'background', 'borderwidth', 'cursor', 
#            'font', 'foreground', 'height', 'justify', 'padx', 'pady', 
#            'relief', 'underline', 'width', 'wraplength',

config_values = {
    "anchor":"nw n ne w center e sw s se".split(" "),
    "background":"red orange yellow green blue purple".split(" "),
    "foreground":"red orange yellow green blue purple".split(" "),
    "relief":"flat sunken raised ridge groove".split(" "),
    "borderwidth": [str(n) for n in range(1,10)],
    "italic":("False","True"),
    "bold":("False","True"),
}
for option,values in config_values.items():
    if option not in ("italic","bold"):
        values.insert(0,"(None)")
    sv = tk.StringVar()
    config_vars[option] = sv
    sv.set(values[0])
    tk.Label(ff,text=option+":").grid(row=row,column=0,sticky="e")
    om = tk.OptionMenu(ff,sv,*values,command=UpdateConfig(option))
    om.grid(row=row,column=1,sticky="w")
    row += 1


mw.mainloop()
