import tkinter as tk
from tkinter import ttk

import re
from copy import deepcopy

class StatusLabel (tk.Label):
    """Custom widget derived from tk.Label which modifies its appearance
    based on its current status state: normal, info, warning, or error.

    The StatusLabel widget supports nearly all the same options as tk.Label.
    (See the table below).  To specify an option that applies in the 
    normal state, simply use the option name from tk.Label.  To specify
    an option that applies in the info, warning, or error state, prepend
    the state name to the option (with an optinoal underline).  Unspecified
    options for the normal state inherit their value from tk.Label.
    Unspecified options for any of the status states inherit their value
    from the normal state.

    The Statistical widget supports 2 additional status state options:
    italic and bold.  These each take a boolean value and apply only when
    the corresponding font is not specified.  In this case, the font is
    formed from the normal state font, italicized or boldened as the
    options dictate.

    Finally, the StatusLabel supports the notion of default option
    values.  These are applied when a StatusLabel widget is constructed.
    Any changes to the default value will have no effect on already
    constructed widgets.  The default values can be modified using
    the `configure` method as a class method.  Similarly, they can be
    explored using the `cget` method a class method.

    The following table outlines all of the options recognized by
    StatusLabel.  Where there are built-in default values, that 
    value is shown in the table.

    +---------------------+---------+---------+---------+---------+
    | option              | normal  |  info   | warning |  error  |
    +=====================+=========+=========+=========+=========+
    | activebackground    |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | activeforeground    |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
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
    | disabledforeground  |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | font                |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | foreground (fg)     |    x    |    x    |    x    |  #fff   |
    +---------------------+---------+---------+---------+---------+
    | height              |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | highlightbackground |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | highlightcolor      |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | highlightthickness  |    x    |    x    |    x    |    x    |
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
    | state               |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | takefocus           |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | text                |    x    |   get   |   get   |   get   | (1)
    +---------------------+---------+---------+---------+---------+
    | underline           |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | width               |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+
    | wraplength          |    x    |    x    |    x    |    x    |
    +---------------------+---------+---------+---------+---------+

    (1) The text option can be queried in any status state, but 
        can only be set in the normal state.  To set the text in
        a status state, use the `info`, `warning`, or `error` methods.
    """

    status_states = ("info", "warning", "error")

    valid_options = (
        'activebackground', 'activeforeground', 'anchor', 'background', 'bg',
        'bold', 'borderwidth', 'bd', 'cursor', 'disabledforeground', 'font',
        'foreground', 'fg', 'height', 'highlightbackground', 'highlightcolor',
        'highlightthickness', 'italic', 'justify', 'padx', 'pady', 'relief',
        'state', 'takefocus', 'text', 'underline', 'width', 'wraplength',
    )
    
    option_synonyms = {
        'bg':'background',
        'fg':'foreground',
        'bd':'borderwidth',
    }

    option_defaults = {
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
        None : {},
    }

    def configure(*args,**kwargs):
        assert len(args) in (0,1), (
            "configure must be called with only keyword arguments"
        )
        if len(args) == 1:
            self = args[0]
            assert isinstance(self,StatusLabel)
            return self._configure(**kwargs)
        else:
            return StatusLabel.configure_defaults(**kwargs)

    def cget(*args):
        assert len(args) in (1,2), (
            "cget must be called with a single parameter"
        )
        if len(args) == 2:
            self,option = args
            assert isinstance(self,StatusLabel)
            return self._cget(option)
        else:
            return StatusLabel.cget_default(*args)

    def _configure(self,**kwargs):
        if kwargs:
            parsed_kwargs = cls._partition_kwargs(**kwargs)
            for k,v in self.options.items():
                v.update(parsed_kwargs[k])
        return self.options

    @classmethod
    def configure_defaults(cls,**kwargs):
        if kwargs:
            parsed_kwargs = cls._partition_kwargs(**kwargs)
            for k,v in cls.option_defaults.items():
                v.update(parsed_kwargs[k])
        return cls.option_defaults

    @classmethod
    def _parse_option(cls,option):
        states = "|".join(cls.status_states)
        m = re.match(rf"({states})_*(.*)",option)
        state = m.group(1) if m else None
        option = m.group(2) if m else option
        option = cls.option_synonyms.get(option,option)
        return option, state

    def _cget(self,option):
        option, state = self._parse_option(option)
        return self.options[state][option]

    @classmethod
    def cget_default(cls,option):
        option, state = cls._parse_option(option)
        return cls.option_defaults[state][option]

    @classmethod
    def _partition_kwargs(cls,*,validate=False,**kwargs):
        rval = {k:dict() for k in (None,*cls.status_states)}
        for option,value in kwargs.items():
            option, state = cls._parse_option(option)

            if validate and not cls._valid_option(option,state):
                raise KeyError(f"Invalid option {option}")
            rval[state][option] = value
        return rval

    @classmethod
    def _valid_option(cls,option,state=None):
        if option not in cls.valid_options:
            return False
        if state is None and option in ("italic","bold"):
            return False
        if state and option in ("text"):
            return False
        return True


    def __init__( self, parent, **kwargs):
        super().__init__(parent)
        self.status = None

        def parse_value(v):
            v = v[-1]
            try: v = int(v.string)
            except: pass
            return v

        inherited_options = {
            k:parse_value(v) for k,v in tk.Label(parent).configure().items()
            if len(v) > 2 
            if self._valid_option(k)
        }

        self.options = { None: deepcopy(inherited_options) }
        del inherited_options["text"]
        for state in self.status_states:
            self.options[state] = deepcopy(inherited_options)

        for state, options in self.option_defaults.items():
            self.options[state].update(options)

        kwargs = self._partition_kwargs(**kwargs,validate=True)
        for state, options in kwargs.items():
            self.options[state].update(options)






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
