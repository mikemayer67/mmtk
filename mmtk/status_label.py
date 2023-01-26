import tkinter as tk
from tkinter import ttk

import re
from copy import deepcopy
from abs import abstractmethod

class OptionError(ValueError):
    def __init__(self,err):
        super().__init__(err)

class AbstractOption:
    states = ("info", "warning", "error")

    def __init__(self,name):
        self.name = name
        self.values = dict()

    @abstractmethod
    def config_entry(self,state=None):
        pass

    def config_entries(self):
        return [
            self.config_entry(state)
            for state in self.values.keys()
        ]

    @abstractmethod
    def update(self,value,state=None):
        pass

    @classmethod
    def parse_key(cls,key):
        states = "|".join(cls.states)
        try:
            m = re.match(rf"({states})_?(.*)",option)
        except:
            raise OptionError(f"Cannot parse option key: {key}")
        if m:
            return m.group(2), m.group(1)
        else:
            return option, None

class Synonym(AbstractOption):
    def __init__(self,synonym,target):
        super().__init__(synonym)
        self.target = target
        self.values.update({state:None for state in (None,*self.states)})

    def config_entry(self,state=None):
        return (f"{state}{self.name}",f"-{state}{self.target.name}")

    def update(self,widget,value,state=None):
        self.target.update(widget,value,state)

class FontOption(AbstractOption):
    def __init__(self,option,defaults):
        super().__init__(option)
        self.values.update({
            state:defaults.get(state,{}).get(option,False)
            for state in self.states
        })
        self.defaults = deepcopy(self.values)

    def config_entry(self,state=None):
        if state is None:
            raise OptionError(f"{self.name} option requires a status state modifier")
        return (
            f"{state}{self.name}",
            f"{state}{self.name.title()}",
            f"{state.title()}{self.name.title()}",
            self.defaults[state],
            self.values[state],
        )
    def update(self,widget,value,state=None):
        if state is None:
            raise OptionError(f"{self.name} option requires a status state modifier")
        self.values[state] = value
        if widget.state == state:
            widget.update_font()

class TextOption(AbstractOption):
    def __init__(self):
        super().__init__("text")

    def config_entry(self,state=None):
        if state:
            raise OptionError("text option does not support status states")
        name,*attr,value = tk.Label().configure("text")
        return (name,*attr,self.options[None])

    def update(self,widget,value,state=None):
        if state:
            raise OptionError("text option does not support status states")
        self.options[None] = value
        if widget.state == None:
            widget.configure(text=value)


class Option(AbstractOption):
    def __init__(self,option,defaults):
        super().__init__(option)
        self.values.update({
            state:defaults.get(state,{}).get(option,None)
            for state in (None,*self.states)
        })
        self.defaults = deepcopy(self.values)

    def config_entry(self,state=None):
        name,dbname,dbclass,default,value = tk.Label().configure(self.name)
        if state is None:
            default = self.defaults.get(state,default)
            value = self.values.get(state,value)
        else:
            name = f"{state}{self.name}"
            dbname = f"{state}{self.name[0].upper()}{self.name[1:]}"
            dbclass = f"{state.title()}{self.name[0].upper()}{self.name[1:]}"
            default = self.defaults.get(None,default)
            default = self.defaults.get(state,default)
            candidate_values = (
                self.values.get(state,None),
                self.defaults.get(state,None),
                self.values.get(None,None),
                self.defaults.get(None,None),
            )
            value = next((v for v in candidate_values if v is not None),value)
        return (name, dbname, dbclass, default, value)

    def update(self,widget,value,state=None):
        self.options[state] = value
        if widget.state == state:
            widget.update_option(self.name,value)


class Options:
    defaults = {
        "info" : {
            "italic":False,
            "bold":False,
        },
        "warning" : {
            "background":"#fc8",
            "foreground":"black",
            "italic":True,
            "bold":False,
        },
        "error" : {
            "background":"#f00",
            "foreground":"white",
            "italic":False,
            "bold":True,
        },
    }

    def __init__(self,widget,**values):
        self.widget = widget
        self.options = dict()

        self.options.update({
            option:Option(option,self.defaults)
            for option in (
              'anchor', 'background', 'bold', 'borderwidth', 'cursor', 
              'font', 'foreground', 'height', 'justify', 'padx', 'pady', 
              'relief', 'underline', 'width', 'wraplength',
            )
        })
        self.options.update({
            synonym:Synonym(synonym,self.options[target])
            for synonym,target in (
                ("bg","background"),
                ("fg","foreground"),
                ("bd","borderwidth"),
            )
        })
        self.options.update({
            option:FontOption(option,self.defaults)
            for option in ("italic","bold")
        })
        self.options["text"] = TextOption()

        for key,value in values.items():
            self.configure({key,value})


    def configure(self,key=None,**kwargs):
        if kwargs and key:
            raise TypeError("Cannot specify both key and kwargs")
        if type(key) is dict:
            kwargs = key
            key = None

        if key:
            try:
                option,state = AbstractOption.parse_key(key)
                return self.options[option].config_entry(state)
            except KeyError:
                raise OptionError(f"invalid option: {key}")

        elif kwargs:
            for key,value in kwargs.items():
                option,state = AbstractOption.parse_key(key)
                self.options[option].update(self.widget,value,state)

        else:
            return sorted([
                config 
                for option in self.options.values()
                for config in option.config_entries()
            ])

    def cget(self,key):
        return self.configure(key)[-1]



class StatusLabel (tk.Label):
    """Custom widget derived from tk.Label which modifies its appearance
    based on its current status state: empty, info, warning, or error.

    The StatusLabel widget supports many of the same options as tk.Label,
    but not all.  In particular, it does not support use of a textvariable,
    any of the active, highlight, or disabled options, or the state or
    takefocus options.  It does support use of the bg, fg, and bd 
    synonyms for background, foreground, and borderwidth.  In addition,
    while it supports use of the text option in cget or getitem, it does 
    not support it in configure or setitem.

    To specify options that apply to one of the three status states,
    simply prepend the status state to the option name, e.g. 
    info_background.

    In addition to the options inherited from tk.Label, there are two 
    additional options that may be specified: italic and bold.  These
    apply if the state is info, warning, or error and the corresponding
    font has not been specified.  In this case the base font will be
    used with italicization or boldness added.

    The following table outlines all of the options recognized by
    StatusLabel.  Where there are built-in default values, that 
    value is shown in the table.

    +---------------------+---------+---------+---------+---------+
    | option              |  empty  |  info   | warning |  error  |
    +=====================+=========+=========+=========+=========+
    | anchor              |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | background (bg)     |    x    |    x    |  #fc8   |  #f00   |
    +---------------------+---------+---------+---------+---------+
    | bold                |         |  False  |  False  |  True   |
    +---------------------+---------+---------+---------+---------+
    | borderwidth (bd)    |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | cursor              |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | font                |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | foreground (fg)     |    x    |    x    |    x    |  #fff   |
    +---------------------+---------+---------+---------+---------+
    | height              |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | italic              |         |  False  |   True  |  False  |
    +---------------------+---------+---------+---------+---------+
    | justify             |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | padx                |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | pady                |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | relief              |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | text                |    x    |         |         |         |
    +---------------------+---------+---------+---------+---------+
    | underline           |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | width               |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | wraplength          |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    """

    def configure(self,key=None,**kwargs):
        """configure widget resources
        This method overrides the method inherited from tk.Label
        """
        self.options.configure(key,**kwargs)

    config = configure

    def cget(self,key):
        """Query widget configuration resource
        This method overrides the method inherited from tk.Label
        """
        return self.options.cget(key)

    def __init__( self, parent, **kwargs):

        self.options = Options(self,**kwargs)

        super().__init__(parent,**kwargs)
        self.text = self["text"]
        self.status = None

#        """
#        StatusLabel contructor
#
#        Args:
#            parent (widget): same first argument as any tkinter widget
#            info_xxx (misc): appearance settings when status level is info
#            warning_xxx (misc): appearance settings when status level is warning
#            error_xxx (misc): appearance settings when status level is error
#            xxx values
#                background (color): background color
#                foreground (color): foreground color
#                font (str or tuple or tk.font.Font): label font
#                italic (bool): italicize default font if font isn't specified
#                bold (bool): bolden default font if font isn't specified
#        """
#        self.styles = dict()
#        for status in ("info","warning","error"):
#            self.styles[status] = dict()
#            for attr in ("background","foreground","font","italic","bold"):
#                key = f"{status}_{attr}"
#                try:
#                    self.styles[status][attr] = kwargs[key]
#                    del kwargs[key]
#                except KeyError:
#                    self.styles[status][attr] = StatusLabel.defaults[status][attr]
#
#        for status,style in self.styles.items():
#            self.styles[status]["font"] = self.resolve_font(style["font"])
#
#        super().__init__(parent,*args,**kwargs)
#
#        self.styles[None] = { 
#            k:self.cget(k) for k in ("background","foreground","font")
#        }
#
#    @staticmethod
#    def resolve_font(font):
#        if font is None:
#            return font
#
#        if type(font) is str:
#            font = tk.font.nametofont(font)
#        elif type(font) is dict:
#            font = tk.font.Font(**font)
#
#        if type(font) is tk.font.Font:
#            return font
#
#        raise ValueError(f"Could not convert {font} to a tk.font.Font")
#
#
#    def info(self,message):
#        self.style("info")
#        self['text'] = message
#
#    def warning(self,message):
#        self.style("warning")
#        self['text'] = message
#
#    def error(self,message):
#        self.style("error")
#        self['text'] = message
#
#    def clear(self):
#        self.style(None)
#        self['text'] = ""
#
#    def style(self,status):
#        bg = self.styles[status]["background"]
#        fg = self.styles[status]["foreground"]
#        font = self.styles[status]["font"]
#
#        if font is None:
#            font = self.styles[None]["font"]
#            if type(font) is str:
#                font = tk.font.nametofont(font)
#            font_attr = font.actual()
#            if self.styles[status]["italic"]:
#                font_attr["slant"] = "italic"
#            if self.styles[status]["bold"]:
#                font_attr["weight"] = "bold"
#            font = tk.font.Font(**font_attr)
#
#        self.configure(
#            background=bg,
#            foreground=fg,
#            font=font,
#        )
#
