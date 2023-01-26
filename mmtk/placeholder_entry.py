import tkinter as tk
from tkinter import ttk
from tkinter import font

class PlaceholderEntry (ttk.Entry):
    """Custom widget derived from ttkEntry.  Provides "placeholder" text in an
    empty entry field when it is not in focus.
    """

    def __init__(
        self,
        parent,
        placeholder_text,
        *args,
        placeholder_font=None,
        placeholder_italic=True,
        placeholder_color=None,
        **kwargs
    ):
        """
        PlaceholderEntry contructor

        Args:
            parent (widget): same first argument as any tkinter widget
            placeholder_text (str): Text to appear when the entry is empty
            placeholder_font (see below): Font to use for the placeholder text (optional)
            placeholder_italic (bool): Display placeholder text in italics (default=True)
            placeholder_color (str): Color to use for the placeholder text (optional)

            - The placholder font can be any of the following:
              - a recognized font name
              - a tkinter.font.Font instance
              - a dictionary of font attributes
            - The default font is based on the ttk.Entry font 
              - If placeholder_italic is True, it will be modified to be italic
              - Otherwise, it will be identical to the ttk.Entry font

            - The default placeholder color is used if not specified.
              - a 2:1 mix of the foreground and background colors

            All other args or kwargs are passed along to the ttk.Entry
            constructor.
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
