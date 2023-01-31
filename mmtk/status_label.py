import tkinter as tk
from tkinter.font import Font, nametofont

import re
from copy import deepcopy
from abc import abstractmethod


################################################################################
# Support values, exceptions, and functions
################################################################################
INFO = "info"
WARNING = "warning"
ERROR = "error"
StatusStates = (INFO,WARNING,ERROR)

class OptionError(ValueError):
    """The exception class used by StatusLabel"""
    def __init__(self,err):
        super().__init__(err)

def parse_key(key):
    """Parses a StatusLabel option key into its base widget option and status state

    Args:
        key (str): A StatusLabel widget option
    Returns (tuple):
        - widget option (str): stateless widget option
        - status state (str): status state (or None)
    Raises: 
        OptionError if the specifed key is not a recognized StatusLabel option
    """
    states = "|".join(StatusStates)
    try:
        m = re.match(rf"({states})_?(.*)",key)
    except:
        raise OptionError(f"Cannot parse option key: {key}")

    return (m.group(2), m.group(1)) if m else (key,None)


################################################################################
# StatusLabel wdiget options:
# - Option
# - FontOption
# - Synonym
################################################################################

####################
# Option
####################

class Option:
    """Base class for all StatusLabel configuration options.

    Maintains the default value for the option as well as the current
    option value for each of the 4 possible states of a StatuLabel
    widget.

    Each corresponds to a single Tk widget option (e.g. background).
    It then extends this option for each of the status states (e.g.
    infobackground, warningbackground, and errorbackground).

    The full list of recognized options can be optained from the
    class method `recognized_options`
    """

    @classmethod
    def recognized_options(cls):
        """Returns the list of all tk.Label options used by StatusLabel"""
        return {
            'anchor', 'background', 'borderwidth', 'cursor', 
            'font', 'foreground', 'height', 'justify', 'padx', 'pady', 
            'relief', 'underline', 'width', 'wraplength',
        }
    _status_statess =(None, *StatusStates)
    _option_type = "status"

    def __init__(self,option,common_value=None,**state_values):
        """Option constructor
        Args:
            option (str): One of the recognized StatusLabel widget options
            common_value: base option value (see below)
            state_values (kwargs): state option values (see below)

            The common value is used by all states (including normal) if
            not overridden for a given status state

            The state option values are specified as kwargs where the key
            is the status state and the value is the option value for that
            state (e.g. info="red", warning="green")

        Raises: OptionError if the specified option is not one of the
        recognized base options.
        """
        self.name = option

        if option not in self.recognized_options():
            raise OptionError(f"Unknown {self._option_type}: {option}")

        self._setup_config(common_value,**state_values)

        self.values = dict()
        for state in self._status_statess:
            self.values[state] = state_values.get(state,self.common)

    def _setup_config(self,common_value,**state_values):
        """initializes the Option type specific common and default values"""
        self.inherited = tk.Label().configure(self.name)

        if common_value is None:
            self.common = self.inherited[-1]
            self.default = self.inherited[-2]
        else:
            self.common = common_value
            self.default = common_value

    def _get_config(self,state):
        """retrieves the default and current option values for a given state"""
        value = self.values[state]
        if value is None:
            value = self.values[None]
        if value is None:
            value = self.default
        return self.default, value

    def config_entry(self,state=None):
        """constructs the record for this option when StatusLabel's 
        configure method is called to retrieve configuration items.

        Args:
            state (str or None): the state for which to retrieve the option
        Returns: tuple
            - name (str): the option name
            - dbname (str): the option name as it appears in Tk database
            - dbclass (str): the option class used in the Tk database
            - default: The default value if not otherwise set
            - value: The current value (either default or as set)
        Raises: OptionError if an invalid state is specified

        For state specific values, the name, dbname, and dbclass will
        each be prefixed with the corredsponding state.
        """
        if state not in self._status_statess:
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
        """constructs all of the records associated with this option...
        the base option and all of the state specific variants
        Returns: list (see `config_entry` for more info)
        """
        return [ self.config_entry(state) for state in self._status_statess ]

    def update(self,value,state=None):
        """updates the option value for the specified state
        Args:
            value: new value to set for the option
            state (str or None), the state with which to associate the value
        Raises: OptionError if an invalid state is specified.
        """
        if state not in self._status_statess:
            raise OptionError(f"Invalid option: {state or ''}{self.name}")
        self.values[state] = value

    def value(self,state=None):
        """returns the option value for the specified state
        Args:
            state (str or None), the state with which to associate the value
        Raises: OptionError if an invalid state is specified.
        """
        try:
            return self.values[state]
        except KeyError:
            raise OptionError(f"Invalid state: {state}")


####################
# Font Option
####################

class FontOption(Option):
    """Font specific StatusLabel configuration options.

    More specifically, state specific font modifiers.  These allow for 
    a common base font whose slant or weight can be modified by state
    without needing to explicitly set a font option for each state.

    Unlike Option, these options do not correspond to any existing
    Tk widget options.  Rather, they provide a means for modifying
    the font option.  

    As these are meant to override the font, these options only apply
    for the info, warning, and error status states. (e.g.
    infoitalic, warningitalic, and erroritalic, but not just italic).

    The associated value for all FontOptions is alwasys a boolean.
    """

    @classmethod
    def recognized_options(cls):
        """Returns the list of all font modifier options used by StatusLabel"""
        return {"italic","bold"}

    _status_statess = StatusStates
    _option_type = "font"

    def __init__(self,option,common_value=False,**state_values):
        """Option constructor
        Args:
            option (str): One of the recognized StatusLabel font modifiers
            common_value: base option value (see below)
            state_values (kwargs): state option values (see below)

            The common value is used by all states (including normal) if
            not overridden for a given status state

            The state option values are specified as kwargs where the key
            is the status state and the value is the option value for that
            state (e.g. info="red", warning="green")

        Raises: OptionError if the specified option is not one of the
        recognized font options.
        """
        common_value = bool(common_value)
        super().__init__(option,common_value,**state_values)
        self.defaults = deepcopy(self.values)

    def _setup_config(self,common_value,**state_values):
        """overrides the inherited _setup_config for font modifier options"""
        self.inherited = (
            self.name, self.name, self.name.title(), common_value, common_value
        )
        self.common = common_value
        self.default = common_value

    def _get_config(self,state):
        """overrides the inherited _get_config for font modifier options"""
        return self.defaults[state], self.values[state]


####################
# Synonym
####################

class Synonym():
    """StatusLabel configuration option synonyms

    Maintains the base and state specific mappings between the recoginized
    option synonyms and the corresponding StatusLabel widget options.

    Like with Option, these each correspond to Tk widget synonyms.
    Similarly, each extends this synoym for each of the status states (e.g.
    infobg, warningbg, or errorbg)

    The full list of recognized synonyms can be optained from the
    class method `recognized_synonyms`
    """
    _synonym_map = {
        "bg":"background",
        "fg":"foreground",
        "bd":"borderwidth",
    }
    @classmethod
    def recognized_synonyms(cls):
        """Returns the list of all tk.Label synonyms used by StatusLabel"""
        return set(cls._synonym_map.keys())

    def __init__(self,synonym,options):
        """Synonym constructor
        Args:
            synonym (str): One of the recognized StatusLabel synonyms
            options (dict): Currently constructed Option instances
        Raises: OptionError if
            - invalid StatusLabel base synonym is specified
            - the provided options don't contain the target Option
        """
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
        """constructs the record for this synonym when StatusLabel's 
        configure method is called to retrieve configuration items.

        Args:
            state (str or None): the state for which to retrieve the option
            follow_link (bool): return info about the target rather than the synonym
        Returns: tuple
            - If follow_link is True
              - name (str): the target option name
              - dbname (str): the target option name as it appears in Tk database
              - dbclass (str): the target option class used in the Tk database
              - default: The (target) default value if not otherwise set
              - value: The (target) current value (either default or as set)
            - If follow_link is False
              - name (str): the synonym name
              - target (str): the target option name (in Tk format)

        Raises: OptionError if an invalid state is specified

        For state specific values, the name, dbname, and dbclass will
        each be prefixed with the corredsponding state.
        """
        if follow_link:
            return self.target.config_entry(state)
        else:
            state = state if state else ""
            return (f"{state}{self.name}",f"-{state}{self.target.name}")

    def config_entries(self):
        """constructs all of the records associated with this synonym...
        the base synonym and all of the state specific variants
        Returns: list (see `config_entry` for more info)
        """
        return [ 
            self.config_entry(state,follow_link=False) 
            for state in (None,*StatusStates)
        ]

    def update(self,value,state=None):
        """updates the value of the target option for the specified state
        Args:
            value: new value to set for the option
            state (str or None), the state with which to associate the value
        Raises: OptionError if an invalid state is specified.
        """
        self.target.update(value,state)

    def value(self,state=None):
        """returns the value of the target option for the specified state
        Args:
            state (str or None), the state with which to associate the value
        Raises: OptionError if an invalid state is specified.
        """
        return self.target.value(state)


################################################################################
# Options - Complete set of all Option, FontOption, and Synonym instances
################################################################################

class Options:
    """Collection of all of the options and synonyms associated with a
    given StatusLabel widget instance
    """
    _defaults = {
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

    def __init__(self,**values):
        """Options constructor
        Args:
            values (kwargs): StatusLabel widget options and values
        Raises: OptionError if any of the value keywords is not recognized
        """
        defaults = dict()
        for state,options in self._defaults.items():
            for option,value in options.items():
                try:
                    defaults[option][state] = value
                except KeyError:
                    defaults[option] = {state:value}

        self.options = dict()

        for option in Option.recognized_options():
            self.options[option] = Option(option,**defaults.get(option,{}))
        for option in FontOption.recognized_options():
            self.options[option] = FontOption(option,**defaults.get(option,{}))
        for synonym in Synonym.recognized_synonyms():
            self.options[synonym] = Synonym(synonym,self.options)

        self.configure(**values)


    def configure(self,key=None,**kwargs):
        """Bridget between StatusLabel's configure method and the state
        dependent widget options

        Args:
            key (str): option keyword
            option values (kwargs): optional

        To set one or more widget options, use keyword arguments of the form 
        option=value. For example, to set a widget's font, you might use an 
        argument such as “font=('serif', 12)”.

        If you provide no arguments, the method will return a dictionary of all 
        the widget's current option values. In this dictionary, the keys will be 
        the option names, and each related value will be a tuple 
        (name, dbName, dbClass, default, current):

        If you provide a single option keyword, the configure tuple will be
        returned for just that option.
        """
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
            modified_states = set()
            for key,value in kwargs.items():
                try:
                    option,state = parse_key(key)
                    self.options[option].update(value,state)
                except KeyError:
                    raise OptionError(f"invalid option: {key}")
                else:
                    modified_states.add(state)
            return modified_states

        else:
            return dict(
                sorted([
                    (config[0],config)
                    for option in self.options.values()
                    for config in option.config_entries()
                ])
            )

    def cget(self,key):
        """Returns the current value for the specified option key"""
        if key.endswith("font"):
            _,state = parse_key(key)
            return self.font(state)
        else:
            return self.configure(key)[-1]

    def font(self,state=None):
        """Returns the current font for the specifed state.
        This combines the font option with any state specific font mondifiers.

        Raises: OptionError if an invalid state is specified
        """
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

    def kwargs(self,state=""):
        """Returns a dictionary of all the currently set options for the
        specified state in a form suitable for passing to tk.Label's
        configure method.

        Raises: OptionError if an invalid state is specified
        """
        rval = dict()
        for name,option in self.options.items():
            if type(option) == Option:
                rval[name] = self.cget((state or "")+name)
        return rval


################################################################################
# StatusLabel - Finally, we get to the widget itself
################################################################################

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

    def __init__( self, parent, text="", **kwargs):
        self.options = Options(**kwargs)

        self._state = None
        self._text = text

        kwargs = self.options.kwargs()
        super().__init__(parent, text=text, **kwargs)

    @property
    def state(self):
        return self._state

    @property
    def text(self):
        return self._text


    def configure(self,key=None,**kwargs):
        """configure widget resources
        This method overrides the method inherited from tk.Label
        """
        if key == "text":
            return super().configure(key)

        result = self.options.configure(key,**kwargs)
        if type(result) is not set:
            return result
        if self._state in result:
            config = self.options.kwargs(self._state)
            super().configure(**config)

    config = configure

    def cget(self,key):
        """Query widget configuration resource
        This method overrides the method inherited from tk.Label
        """
        if key == "text":
            return super().cget(key)
        return self.options.cget(key)

    def info(self,msg):
        self._set_state(INFO,msg)

    def warning(self,msg):
        self._set_state(WARNING,msg)

    def error(self,msg):
        self._set_state(ERROR,msg)

    def clear(self,text=None):
        if text is not None:
            self._text = text
        if text is None:
            self._text = ""
        self._set_state(None,self._text)

    def _set_state(self,state,msg):
        if self._state != state:
            self._state = state
            config = self.options.kwargs(state)
            super().config(**config)
        super().config(text=msg)

    def __getitem__(self,key):
        return self.cget(key)

    def __setitem__(self,key,value):
        self.configure(key,value)



