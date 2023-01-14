import tkinter as tk
from tkinter import ttk
from tkinter import font

class PlaceholderEntry (ttk.Entry):
    def __init__(self,parent,*args,placeholder,**kwargs):
        self.placeholder_text = placeholder
        super().__init__(parent,*args,**kwargs)

        self.show = self['show']

        self._determine_placeholder_color()
        self._determine_placeholder_font()
        self._create_placeholder_style()

        self.show_placeholder()

        self.bind('<FocusIn>',self.handle_focus_in)
        self.bind('<FocusOut>',self.handle_focus_out)

    def _determine_placeholder_color(self):
        s = ttk.Style()
        def element_rgb(element):
            rgb = self.winfo_rgb(s.lookup('TEntry',element))
            return tuple(c//256 for c in rgb)

        fg = element_rgb('foreground')
        bg = element_rgb('background')

        self.placeholder_color = (
            '#' + 
            ''.join(f"{(2*f+b)//3:02x}" for f,b in zip(fg,bg))
        )

    def _determine_placeholder_font(self):
        self.entry_font = font.nametofont(str(self['font']))
        font_attr = self.entry_font.actual()
        font_attr['slant'] = 'italic'
        self.placeholder_font = font.Font(**font_attr)

    def _create_placeholder_style(self):
        s = ttk.Style()
        s.configure('Placeholder.TEntry', foreground=self.placeholder_color)

    def show_placeholder(self):
        self.showing_placeholder = True
        self['show'] = ''
        self['font'] = self.placeholder_font
        self['style'] = 'Placeholder.TEntry'
        self.delete(0,'end')
        self.insert(0,self.placeholder_text)

    def hide_placeholder(self):
        self.showing_placeholder = False
        self['show'] = self.show
        self['font'] = self.entry_font
        self['style'] = 'TEntry'
        self.delete(0,'end')

    def handle_focus_in(self,event=None):
        if self.showing_placeholder:
            self.hide_placeholder()

    def handle_focus_out(self,event=None):
        if not self.get():
            self.show_placeholder()
