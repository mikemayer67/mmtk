#!/usr/bin/env python

# Author: Michael A. Mayer
# Copyright: 2023, VMWishes
# License: UNLICENSE (http://unlicense.org)

import tkinter as tk
from tkinter import ttk

from demo import Demo
from mmtk import StatusLabel

config_values = {
    "anchor":"nw n ne w center e sw s se".split(" "),
    "background":"red orange yellow green blue purple".split(" "),
    "foreground":"red orange yellow green blue purple".split(" "),
    "relief":"flat sunken raised ridge groove".split(" "),
    "borderwidth": [str(n) for n in range(10)],
    "padx": [str(n) for n in range(10)],
    "pady": [str(n) for n in range(10)],
    "width": [str(n) for n in range(10,120,10)],
    "italic":("False","True"),
    "bold":("False","True"),
}

class StatusLabelDemo(Demo):
    def __init__(self,*args,**kwargs):
        self.states = (None,"info","warning","error")
        self.config = {k:dict() for k in self.states}
        super().__init__(*args,**kwargs)

    def _build(self):
        self._add_example()
        self._add_config()

    def _add_example(self):
        f = ttk.LabelFrame(self.frame,text="Example")
        f.pack(side="top",fill="x",expand=False)

        self.status_label = StatusLabel(f)
        self.status_label.pack(fill="x",expand=False)

        self.state = tk.IntVar()

        f = ttk.Frame(self.frame)
        f.pack(side="top",fill="x",expand=False)
        f = ttk.Frame(f)
        f.pack(side="right",expand=False)

        for value,text in enumerate(("normal",*self.states[1:])):
            b = ttk.Radiobutton(
                f,
                text=text,
                value=value,
                variable=self.state,
                command=self._handle_state,
            )
            b.pack(side="left",expand=False,padx=5)

    def _add_config(self):
        f = ttk.LabelFrame(self.frame,text="Status Config")
        f.pack(side="top",fill="x",expand=False)

        f.columnconfigure(0,weight=0)
        for i in range(1,5):
            f.columnconfigure(i,weight=1)

        header_font = tk.font.nametofont('TkDefaultFont').actual()
        header_font['weight'] = 'bold'
        header_font = tk.font.Font(**header_font)

        for i,state in enumerate(("normal",*self.states[1:])):
            ttk.Label(
                f,
                text=state,
                font=header_font
            ).grid(
                row=0,
                column=i+1,
            )

        row = 0
        for option,values in config_values.items():
            if option not in ("italic","bold"):
                values.insert(0,"-")

            row += 1
            ttk.Label(
                f,
                text=f"{option}: ",
                font=header_font,
            ).grid(
                row=row,
                column=0,
                sticky="e",
            )

            for i,state in enumerate(self.states):
                if option in ("bold","italic") and state is None:
                    continue

                sv = tk.StringVar()
                self.config[state][option] = sv
                ttk.OptionMenu(
                    f,
                    sv,
                    values[0],
                    *values,
                    command=lambda v,s=state,o=option:self._update_config(o,s,v),
                ).grid(
                    row=row,
                    column=i+1,
                    sticky="news",
                )

    def _handle_state(self,*args,**kwargs):
        state = self.state.get()
        if state == 0:
            self.status_label.clear()
        elif state == 1:
            self.status_label.info("Just to let you know")
        elif state == 2:
            self.status_label.warning("This does NOT look good")
        elif state == 3:
            self.status_label.error("Oh shit!  Look what you've done...")

    def _update_config(self,option,state,value):
        if value == "-":
            value = None
        config = { (state or "")+option : value }
        self.status_label.configure(**config)


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.abspath('..'))
    mw = tk.Tk()
    StatusLabelDemo(mw)
    mw.mainloop()

