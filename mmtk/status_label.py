import tkinter as tk
from tkinter import ttk

import re
from copy import deepcopy
from abc import abstractmethod

class OptionError(ValueError):
    def __init__(self,err):
        super().__init__(err)

class AbstractOption:
    states = ("info", "warning", "error")

    def __init__(self,name):
        self.name = name

    @abstractmethod
    def value(self):
        pass

    @abstractmethod
    def config_entry(self,state=None):
        pass

    @abstractmethod
    def config_entries(self):
        pass

    @abstractmethod
    def update(self,value,state=None):
        pass

    @classmethod
    def parse_key(cls,key):
        states = "|".join(cls.states)
        try:
            m = re.match(rf"({states})_?(.*)",key)
        except:
            raise OptionError(f"Cannot parse option key: {key}")
        if m:
            return m.group(2), m.group(1)
        else:
            return key, None

    @classmethod
    def validate(cls,*,state=None):
        if state is not None and state not in cls.states:
            raise OptionError(f"Invalid status state: {state}")

class Synonym(AbstractOption):
    _synonym_map = {
        "bg":"background",
        "fg":"foreground",
        "bd":"borderwidth",
    }
    recognized_synonyms = _synonym_map.keys()

    def __init__(self,synonym,options):
        super().__init__(synonym)
        try:
            target_option = self._synonym_map[synonym]
        except KeyError:
            raise OptionError(f"Unknown synonym option: {synonym}")
        try:
            self.target = options[target_option]
        except KeyError:
            raise OptionError(f"Cannot find target option: {target_option}")

    def config_entry(self,state=None,*,follow_link=True):
        if follow_link:
            return self.target.config_entry(state)
        else:
            state = state if state else ""
            return (f"{state}{self.name}",f"-{state}{self.target.name}")

    def config_entries(self):
        return [ 
            self.config_entry(state,follow_link=False) 
            for state in (None,*self.states)
        ]

    def update(self,value,state=None):
        self.target.update(value,state)

    def value(self,state=None):
        return self.target.value(state)


class FontOption(AbstractOption):
    recognized_options = ("italic","bold")
    def __init__(self,option,defaults=None):
        if option not in self.recognized_options:
            raise OptionError(f"Unrecognized font modifier: {option}")

        super().__init__(option)
        self.values = dict()
        for state in self.states:
            try:
                self.values[state] = defaults[state][option]
            except (KeyError,TypeError) as e:
                self.values[state] = False
        self.defaults = deepcopy(self.values)

    def config_entry(self,state=None):
        self.validate(state=state)
        if state is None:
            raise OptionError(f"{self.name} option requires a status state modifier")
        return (
            f"{state}{self.name}",
            f"{state}{self.name.title()}",
            f"{state.title()}{self.name.title()}",
            self.defaults[state],
            self.values[state],
        )

    def config_entries(self):
        return [ self.config_entry(state) for state in self.states ]

    def update(self,value,state=None):
        self.validate(state=state)
        if state is None:
            raise OptionError(f"{self.name} option requires a status state modifier")
        self.values[state] = value

    def value(self,state=None):
        self.validate(state=stete)
        return self.values[state]


class TextOption(AbstractOption):
    def __init__(self):
        super().__init__("text")
        self._value = ""

    def config_entry(self):
        return ("text","text","Text","",self._value)

    def config_entries(self):
        return [ self.config_entry() ]

    def update(self,value):
        self._value = value

    def value(self,state=None):
        self.validate(state=state)
        return self._value


class Option(AbstractOption):
    recognized_options = (
      'anchor', 'background', 'borderwidth', 'cursor', 
      'font', 'foreground', 'height', 'justify', 'padx', 'pady', 
      'relief', 'underline', 'width', 'wraplength',
    )
    def __init__(self,option,defaults=None):
        if option not in self.recognized_options:
            raise OptionError(f"Unknown option: {option}")

        super().__init__(option)

        self.values = dict()
        self.defaults = dict()
        self.inherited = tk.Label().configure(option)

        try:
            value = defaults[None][option]
            self.defaults[None] = value
            self.values[None] = value
        except (KeyError,TypeError) as e:
            self.defaults[None] = self.inherited[-2]
            self.values[None] = self.inherited[-1]

        for state in self.states:
            try:
                value = defaults[state][option]
                self.values[state] = value
                self.defaults[state] = value
            except (KeyError,TypeError) as e:
                self.values[state] = None
                self.defaults[state] = None

    def config_entry(self,state=None):
        self.validate(state=state)

        name,dbname,dbclass,default,value = self.inherited
        if state is None:
            name = self.name
        else:
            name = f"{state}{self.name}"
            dbname = f"{state}{dbname[0].upper()}{dbname[1:]}"
            dbclass = f"{state.title()}{dbclass}"

        default = self.defaults[state]
        if default is None:
            default = self.defaults[None]

        value = self.values[state]
        if value is None:
            value = self.defaults[state]
        if value is None:
            value = self.values[None]
        if value is None:
            value = self.defaults[None]
            
        return (name, dbname, dbclass, default, value)

    def config_entries(self):
        return [ self.config_entry(state) for state in (None,*self.states) ]

    def update(self,value,state=None):
        self.validate(state=state)
        self.values[state] = value

    def value(self,state=None):
        self.validate(state=state)
        return self.values[state]


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
            for option in Option.recognized_options
        })
        self.options.update({
            synonym:Synonym(synonym,self.options)
            for synonym in Synonym.recognized_synonyms
        })
        self.options.update({
            option:FontOption(option,self.defaults)
            for option in FontOption.recognized_options
        })
        self.options["text"] = TextOption()

        self.configure(**values)


    def configure(self,key=None,**kwargs):
        if kwargs and key:
            raise TypeError("Cannot specify both key and kwargs")
        if type(key) is dict:
            kwargs = key
            key = None

        if key:
            try:
                option,state = AbstractOption.parse_key(key)
                if state:
                    return self.options[option].config_entry(state)
                else:
                    return self.options[option].config_entry()
            except (KeyError,TypeError) as e:
                raise OptionError(f"invalid option: {key}")

        elif kwargs:
            for key,value in kwargs.items():
                try:
                    option,state = AbstractOption.parse_key(key)
                    self.options[option].update(value,state)
                except KeyError:
                    raise OptionError(f"invalid option: {key}")

        else:
            return dict(
                sorted([
                    (config[0],config)
                    for option in self.options.values()
                    for config in option.config_entries()
                ])
            )

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
        return self.options.configure(key,**kwargs)

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
