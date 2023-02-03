# Author: Michael A. Mayer
# Copyright: 2023, VMWishes
# License: UNLICENSE (http://unlicense.org)

import tkinter as tk
from tkinter import ttk

class Demo:
    def __init__(self,parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both",expand=True,padx=8,pady=8)
        self._build()
