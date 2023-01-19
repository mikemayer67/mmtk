import tkinter as tk
from tkinter import ttk

from copy import deepcopy

class StatusLabel (tk.Label):
    """Custom widget derived from ttk.Label.  Adds methods to change appearance
    based on type of status (info, warning, error).

    The default appearance can be modified through the StatusLabel.defaults
    dictionary.  The three primary keys ("info", "warning", and "error")
    reflect the current status level.  The secondary keys ("background", 
    "foreground", "font", "italic", and "bold") are the apperance 
    attributes that change with status level.  Any attribute that is
    set to None will use the default ttk.Label value, with the following
    exception.  When font is set to None, the italic and bold attributes
    will modify the default font accordingly.

    Note that StatusLabel actually derives from tk.Label rather than ttk.Label
    as the latter does not allow background styling on all operating systems.
    """

    defaults = {
        "info" : {
            "background":None,
            "foreground":None,
            "font":None,
            "italic":False,
            "bold":False,
        },
        "warning" : {
            "background":"#fc8",
            "foreground":None,
            "font":None,
            "italic":True,
            "bold":False,
        },
        "error" : {
            "background":"#f00",
            "foreground":"white",
            "font":None,
            "italic":False,
            "bold":True,
        },
    }

    def __init__( self, parent, *args, **kwargs):
        """
        StatusLabel contructor

        Args:
            parent (widget): same first argument as any tkinter widget
            info_xxx (misc): appearance settings when status level is info
            warning_xxx (misc): appearance settings when status level is warning
            error_xxx (misc): appearance settings when status level is error
            xxx values
                background (color): background color
                foreground (color): foreground color
                font (str or tuple or tk.font.Font): label font
                italic (bool): italicize default font if font isn't specified
                bold (bool): bolden default font if font isn't specified
        """
        self.styles = dict()
        for status in ("info","warning","error"):
            self.styles[status] = dict()
            for attr in ("background","foreground","font","italic","bold"):
                key = f"{status}_{attr}"
                try:
                    self.styles[status][attr] = kwargs[key]
                    del kwargs[key]
                except KeyError:
                    self.styles[status][attr] = StatusLabel.defaults[status][attr]

        for status,style in self.styles.items():
            self.styles[status]["font"] = self.resolve_font(style["font"])

        super().__init__(parent,*args,**kwargs)

        self.styles[None] = { 
            k:self.cget(k) for k in ("background","foreground","font")
        }

    @staticmethod
    def resolve_font(font):
        if font is None:
            return font

        if type(font) is str:
            font = tk.font.nametofont(font)
        elif type(font) is dict:
            font = tk.font.Font(**font)

        if type(font) is tk.font.Font:
            return font

        raise ValueError(f"Could not convert {font} to a tk.font.Font")


    def info(self,message):
        self.style("info")
        self['text'] = message

    def warning(self,message):
        self.style("warning")
        self['text'] = message

    def error(self,message):
        self.style("error")
        self['text'] = message

    def clear(self):
        self.style(None)
        self['text'] = ""

    def style(self,status):
        bg = self.styles[status]["background"]
        fg = self.styles[status]["foreground"]
        font = self.styles[status]["font"]

        if font is None:
            font = self.styles[None]["font"]
            if type(font) is str:
                font = tk.font.nametofont(font)
            font_attr = font.actual()
            if self.styles[status]["italic"]:
                font_attr["slant"] = "italic"
            if self.styles[status]["bold"]:
                font_attr["weight"] = "bold"
            font = tk.font.Font(**font_attr)

        self.configure(
            background=bg,
            foreground=fg,
            font=font,
        )

