import tkinter as tk
from tkinter.font import Font, nametofont

import re
from copy import deepcopy
from abc import abstractmethod

class OptionError(ValueError):
    def __init__(self,err):
        super().__init__(err)

StatusStates = ("info", "warning", "error")

def parse_key(key):
    states = "|".join(StatusStates)
    try:
        m = re.match(rf"({states})_?(.*)",key)
    except:
        raise OptionError(f"Cannot parse option key: {key}")

    return (m.group(2), m.group(1)) if m else (key,None)


class Synonym():
    states = ("info", "warning", "error")
    _synonym_map = {
        "bg":"background",
        "fg":"foreground",
        "bd":"borderwidth",
    }
    recognized_synonyms = _synonym_map.keys()

    def __init__(self,synonym,options):
        self.name = synonym
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
            for state in (None,*StatusStates)
        ]

    def update(self,value,state=None):
        self.target.update(value,state)

    def value(self,state=None):
        return self.target.value(state)


class Option:
    recognized_options = {
      'anchor', 'background', 'borderwidth', 'cursor', 
      'font', 'foreground', 'height', 'justify', 'padx', 'pady', 
      'relief', 'underline', 'width', 'wraplength',
    }
    status_states = (None,*StatusStates)
    option_type = "status"
    def __init__(self,option,common_value=None,**state_values):
        self.name = option

        if option not in self.recognized_options:
            raise OptionError(f"Unknown {self.option_type}: {option}")

        self._setup_config(common_value,**state_values)

        self.values = dict()
        for state in self.status_states:
            self.values[state] = state_values.get(state,self.common)

    def _setup_config(self,common_value,**state_values):
        self.inherited = tk.Label().configure(self.name)

        if common_value is None:
            self.common = self.inherited[-1]
            self.default = self.inherited[-2]
        else:
            self.common = common_value
            self.default = common_value

    def _get_config(self,state):
        value = self.values[state]
        if value is None:
            value = self.values[None]
        if value is None:
            value = self.default
        return self.default, value

    def config_entry(self,state=None):
        if state not in self.status_states:
            raise OptionError(f"Invalid option: {state or ''}{self.name}")

        name,dbname,dbclass,default,value = self.inherited

        try:
            default,value = self._get_config(state)
        except KeyError:
            raise RuntimeError(f"Coding error... should not get here")

        if state is not None:
            name = f"{state}{self.name}"
            dbname = f"{state}{dbname[0].upper()}{dbname[1:]}"
            dbclass = f"{state.title()}{dbclass}"

        return (name, dbname, dbclass, default, value)

    def config_entries(self):
        return [ self.config_entry(state) for state in self.status_states ]

    def update(self,value,state=None):
        if state not in self.status_states:
            raise OptionError(f"Invalid option: {state or ''}{self.name}")
        self.values[state] = value

    def value(self,state=None):
        try:
            return self.values[state]
        except KeyError:
            raise OptionError(f"Invalid state: {state}")


class FontOption(Option):
    recognized_options = {"italic","bold"}
    status_states = StatusStates
    option_type = "font"
    def __init__(self,option,common_value=False,**state_values):
        common_value = bool(common_value)
        super().__init__(option,common_value,**state_values)
        self.defaults = deepcopy(self.values)

    def _setup_config(self,common_value,**state_values):
        self.inherited = (
            self.name, self.name, self.name.title(), common_value, common_value
        )
        self.common = common_value
        self.default = common_value

    def _get_config(self,state):
        return self.defaults[state], self.values[state]


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
        defaults = dict()
        for state,options in self.defaults.items():
            for option,value in options.items():
                try:
                    defaults[option][state] = value
                except KeyError:
                    defaults[option] = {state:value}

        self.widget = widget
        self.options = dict()

        self.options.update({
            option:Option(option,**defaults)
            for option in Option.recognized_options
        })
        self.options.update({
            synonym:Synonym(synonym,self.options)
            for synonym in Synonym.recognized_synonyms
        })
        self.options.update({
            option:FontOption(option,**defaults)
            for option in FontOption.recognized_options
        })

        self.configure(**values)


    def configure(self,key=None,**kwargs):
        if kwargs and key:
            raise TypeError("Cannot specify both key and kwargs")
        if type(key) is dict:
            kwargs = key
            key = None

        if key:
            try:
                option,state = parse_key(key)
                if state:
                    return self.options[option].config_entry(state)
                else:
                    return self.options[option].config_entry()
            except (KeyError,TypeError) as e:
                raise OptionError(f"invalid option: {key}")

        elif kwargs:
            for key,value in kwargs.items():
                try:
                    option,state = parse_key(key)
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
        if key.endswith("font"):
            _,state = parse_key(key)
            return self.font(state)
        else:
            return self.configure(key)[-1]

    def font(self,state=None):
        if not state:
            return self.configure("font")[-1]

        font = self.configure(state+"font")[-1]
        italic = self.cget(state+"italic")
        bold = self.cget(state+"bold")

        if not (bold or italic):
            return font

        if type(font) is str:
            font = nametofont(font)
        elif type(font) is dict:
            font = Font(**font)

        if not isinstance(font,Font):
            raise OptionError(f"Cannot create font from: {font}")

        font = font.actual()
        if bold:
            font['weight'] = tk.font.BOLD
        if italic:
            font['slant'] = tk.font.ITALIC

        return Font(**font)

    def __call__(self,state=""):
        rval = dict()
        for name,option in self.options.items():
            if type(option) == Option:
                rval[name] = self.cget(state+name)
        return rval


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
        self.state = None

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
