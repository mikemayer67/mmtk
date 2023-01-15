import unittest

import tkinter as tk
from tkinter import ttk
from tkinter import font

from mmttk import PlaceholderEntry

class Tests(unittest.TestCase):
    def setUp(self):
        self.mw = tk.Tk()

    def tearDown(self):
        self.mw.destroy()

    def test_basic_constructor(self):
        placeholder = "TestString"
        phe = PlaceholderEntry(self.mw,placeholder)

        self.assertTrue(type(phe) is PlaceholderEntry)
        self.assertTrue(isinstance(phe, ttk.Entry))

        self.assertEqual(
            phe._nametowidget(phe.winfo_parent()),
            self.mw
        )

        self.assertEqual(phe.placeholder_text, placeholder)

    def test_constructor_with_color(self):
        color = "green"
        phe = PlaceholderEntry(self.mw,"TestString",placeholder_color=color)

        expected_rgb = self.mw.winfo_rgb(color)
        actual_rgb = self.mw.winfo_rgb(phe.placeholder_color)
        self.assertEqual(actual_rgb, expected_rgb)

        color = "#123456"
        phe = PlaceholderEntry(self.mw,"TestString",placeholder_color=color)

        expected_rgb = self.mw.winfo_rgb(color)
        actual_rgb = self.mw.winfo_rgb(phe.placeholder_color)
        self.assertEqual(actual_rgb, expected_rgb)


    def test_constructor_italic_arg(self):
        phe = PlaceholderEntry(self.mw,"TestString",placeholder_italic=True)

        entry_font = phe.entry_font.actual()
        phe_font = phe.placeholder_font.actual()

        self.assertEqual(phe_font['family'], entry_font['family'])
        self.assertEqual(phe_font['slant'],'italic')

        phe = PlaceholderEntry(self.mw,"TestString",placeholder_italic=False)

        entry_font = phe.entry_font.actual()
        phe_font = phe.placeholder_font.actual()

        self.assertEqual(phe_font['family'], entry_font['family'])
        self.assertEqual(phe_font['slant'],entry_font['slant'])


    def test_constructor_with_font(self):
        # test font by name
        fontname = 'TkDefaultFont'
        phe = PlaceholderEntry(self.mw,"TestString", placeholder_font=fontname)

        expected_font = font.nametofont(fontname)
        self.assertEqual(phe.placeholder_font.actual(),expected_font.actual())

        # test font.Font
        placeholder_font = font.nametofont('TkFixedFont')
        phe = PlaceholderEntry(self.mw,"TestString",
                               placeholder_font=placeholder_font)

        self.assertEqual(phe.placeholder_font.actual(),placeholder_font.actual())

        # test font attributes
        placeholder_font_attr = font.nametofont('TkTextFont').actual()
        phe = PlaceholderEntry(self.mw,"TestString",
                               placeholder_font=placeholder_font_attr)

        self.assertEqual(phe.placeholder_font.actual(),placeholder_font_attr)


    def test_placeholder_color(self):
        phe = PlaceholderEntry(self.mw,"TestString")

        s = ttk.Style()
        fg = self.mw.winfo_rgb(s.lookup('TEntry','foreground'))
        bg = self.mw.winfo_rgb(s.lookup('TEntry','background'))
        ph = self.mw.winfo_rgb(phe.placeholder_color)

        fg = tuple(c//256 for c in fg)
        bg = tuple(c//256 for c in bg)
        ph = tuple(c//256 for c in ph)

        expected_ph = tuple((2*f+b)//3 for f,b in zip(fg,bg))

        self.assertEqual(ph,expected_ph)

    def test_placeholder_font(self):
        phe = PlaceholderEntry(self.mw,"TestString")

        entry_font = phe.entry_font.actual()
        phe_font = phe.placeholder_font.actual()

        self.assertEqual(phe_font['family'], entry_font['family'])
        self.assertEqual(phe_font['slant'],'italic')

    def test_placeholder_style(self):
        phe = PlaceholderEntry(self.mw,"TestString")

        s = ttk.Style()
        self.assertEqual(
            s.lookup(phe.placeholder_style,'foreground'),
            phe.placeholder_color
        )

    def test_toggle_placeholder(self):
        placeholder = "TestString"
        phe = PlaceholderEntry(self.mw,placeholder,show='#')

        self.assertTrue(phe.showing_placeholder)
        self.assertEqual(phe['show'],'')
        actual_font = font.nametofont(str(phe['font'])).actual()
        expected_font = phe.placeholder_font.actual()
        self.assertEqual(actual_font, expected_font)
        self.assertEqual(phe['style'],phe.placeholder_style)
        self.assertEqual(phe.get(),placeholder)

        phe._hide_placeholder()
        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe['show'],'#')
        actual_font = font.nametofont(str(phe['font'])).actual()
        expected_font = phe.entry_font.actual()
        self.assertEqual(actual_font, expected_font)
        self.assertEqual(phe['style'],'TEntry')
        self.assertEqual(phe.get(),'')

        phe._show_placeholder()
        self.assertTrue(phe.showing_placeholder)
        self.assertEqual(phe['show'],'')
        actual_font = font.nametofont(str(phe['font'])).actual()
        expected_font = phe.placeholder_font.actual()
        self.assertEqual(actual_font, expected_font)
        self.assertEqual(phe['style'],phe.placeholder_style)
        self.assertEqual(phe.get(),placeholder)

    def test_focus_in(self):
        placeholder = "TestString"
        phe = PlaceholderEntry(self.mw,placeholder)

        self.assertTrue(phe.showing_placeholder)
        self.assertEqual(phe.get(),placeholder)

        phe._handle_focus_in()

        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe.get(),'')


    def test_focus_out(self):
        placeholder = "TestString"
        phe = PlaceholderEntry(self.mw,placeholder)

        self.assertTrue(phe.showing_placeholder)
        self.assertEqual(phe.get(),placeholder)

        phe._handle_focus_in()
        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe.get(),'')

        phe._handle_focus_out()
        self.assertTrue(phe.showing_placeholder)
        self.assertEqual(phe.get(),placeholder)

        phe._handle_focus_in()
        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe.get(),'')

        some_text = "some text"
        phe.insert(0,some_text)

        phe._handle_focus_out()
        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe.get(),some_text)

        phe._handle_focus_in()
        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe.get(),some_text)

        phe.delete(0,'end')
        phe._handle_focus_out()
        self.assertTrue(phe.showing_placeholder)
        self.assertEqual(phe.get(),placeholder)








        












        



