import tkinter as tk
from tkinter import ttk
from tkinter import font

class StatusLabel (ttk.Label):
    """Custom widget derived from ttk.Label.  Adds methods to change appearance
    based on type of status (info, warning, error).

    Note that this class introduces the following ttk Styles:
        - StatusLabelInfo.TLabel
        - StatusLabelWarning.TLabel
        - StatusLabelError.TLabel
    """

    def __init__(
        self,
        parent,
        placeholder_text,
        *args,
        info_italic=True,
        info_bold=False,
        info_color="c0c0c0",
        info_bg=None,
        warning_italic=True,
        warning_bold=False,
        warning_color="#c00000",
        warning_bg=None,
        error_italic=False,
        error_bold=False,
        error_color="#ff0000",
        error_bg=None,
        **kwargs
    ):
        """
        StatusLabel contructor

        Args:
            parent (widget): same first argument as any tkinter widget
            info_italic (bool): Display info messages in italic
            info_bold (bool): Display info messages in bold
            info_color (str): Font color for info messages
            info_bg (str): Background color for info messages
            warning_italic (bool): Display warning messages in italic
            warning_bold (bool): Display warning messages in bold
            warning_color (str): Font color for warning messages
            warning_bg (str): Background color for warning messages
            error_italic (bool): Display error messages in italic
            error_bold (bool): Display error messages in bold
            error_color (str): Font color for error messages
            error_bg (str): Background color for error messages
        """
        self.placeholder_text = placeholder_text
        super().__init__(parent,*args,**kwargs)

        self.show = self['show']

        self.entry_font = font.nametofont(str(self['font']))
        if type(placeholder_font) is font.Font:
            self.placeholder_font = placeholder_font
        else:
            self.placeholder_font = self._determine_placeholder_font(
                placeholder_font,
                placeholder_italic,
            )

        if placeholder_color is None:
            self.placeholder_color = self._determine_placeholder_color()
        else:
            self.placeholder_color = placeholder_color

        self._create_placeholder_style()

        self._show_placeholder()

        self.bind('<FocusIn>',self._handle_focus_in)
        self.bind('<FocusOut>',self._handle_focus_out)


    def _determine_placeholder_color(self):
        s = ttk.Style()
        def element_rgb(element):
            rgb = self.winfo_rgb(s.lookup('TEntry',element))
            return tuple(c//256 for c in rgb)

        fg = element_rgb('foreground')
        bg = element_rgb('background')

        return '#' + ''.join(f"{(2*f+b)//3:02x}" for f,b in zip(fg,bg))

    def _determine_placeholder_font(self,placeholder_font,italic):
        if placeholder_font is None:
            font_attr = self.entry_font.actual()
            if italic:
                font_attr['slant'] = 'italic'
            return font.Font(**font_attr)
        elif type(placeholder_font) is str:
            return font.nametofont(placeholder_font)
        elif type(placeholder_font) is dict:
            return font.Font(**placeholder_font)
        else:
            # don't know how to handle it... let Tkinter deal with it.
            return font

    def _create_placeholder_style(self):
        self.placeholder_style = f"{id(self)}.TEntry"
        s = ttk.Style()
        s.configure(self.placeholder_style, foreground=self.placeholder_color)

    def _show_placeholder(self):
        self.showing_placeholder = True
        self['show'] = ''
        self['font'] = self.placeholder_font
        self['style'] = self.placeholder_style
        self.delete(0,'end')
        self.insert(0,self.placeholder_text)

    def _hide_placeholder(self):
        self.showing_placeholder = False
        self['show'] = self.show
        self['font'] = self.entry_font
        self['style'] = 'TEntry'
        self.delete(0,'end')

    def _handle_focus_in(self,event=None):
        if self.showing_placeholder:
            self._hide_placeholder()

    def _handle_focus_out(self,event=None):
        if not self.get():
            self._show_placeholder()
