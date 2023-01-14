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
        phe = PlaceholderEntry(self.mw,placeholder=placeholder)

        self.assertTrue(type(phe) is PlaceholderEntry)
        self.assertTrue(isinstance(phe, ttk.Entry))

        self.assertEqual(
            phe._nametowidget(phe.winfo_parent()),
            self.mw
        )

        self.assertEqual(phe.placeholder_text, placeholder)

    def test_placeholder_color(self):
        phe = PlaceholderEntry(self.mw,placeholder="TestString")

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
        phe = PlaceholderEntry(self.mw,placeholder="TestString")

        entry_font = phe.entry_font.actual()
        phe_font = phe.placeholder_font.actual()

        self.assertEqual(phe_font['family'], entry_font['family'])
        self.assertEqual(phe_font['slant'],'italic')

    def test_placeholder_style(self):
        phe = PlaceholderEntry(self.mw,placeholder="TestString")

        s = ttk.Style()
        self.assertEqual(
            s.lookup('Placeholder.TEntry','foreground'),
            phe.placeholder_color
        )

    def test_toggle_placeholder(self):
        placeholder = "TestString"
        phe = PlaceholderEntry(self.mw,placeholder=placeholder,show='#')

        self.assertTrue(phe.showing_placeholder)
        self.assertEqual(phe['show'],'')
        actual_font = font.nametofont(str(phe['font'])).actual()
        expected_font = phe.placeholder_font.actual()
        self.assertEqual(actual_font, expected_font)
        self.assertEqual(phe['style'],'Placeholder.TEntry')
        self.assertEqual(phe.get(),placeholder)

        phe.hide_placeholder()
        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe['show'],'#')
        actual_font = font.nametofont(str(phe['font'])).actual()
        expected_font = phe.entry_font.actual()
        self.assertEqual(actual_font, expected_font)
        self.assertEqual(phe['style'],'TEntry')
        self.assertEqual(phe.get(),'')

    def test_focus_in(self):
        placeholder = "TestString"
        phe = PlaceholderEntry(self.mw,placeholder=placeholder)

        self.assertTrue(phe.showing_placeholder)
        self.assertEqual(phe.get(),placeholder)

        phe.handle_focus_in()

        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe.get(),'')


    def test_focus_out(self):
        placeholder = "TestString"
        phe = PlaceholderEntry(self.mw,placeholder=placeholder)

        self.assertTrue(phe.showing_placeholder)
        self.assertEqual(phe.get(),placeholder)

        phe.handle_focus_in()
        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe.get(),'')

        phe.handle_focus_out()
        self.assertTrue(phe.showing_placeholder)
        self.assertEqual(phe.get(),placeholder)

        phe.handle_focus_in()
        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe.get(),'')

        some_text = "some text"
        phe.insert(0,some_text)

        phe.handle_focus_out()
        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe.get(),some_text)

        phe.handle_focus_in()
        self.assertFalse(phe.showing_placeholder)
        self.assertEqual(phe.get(),some_text)

        phe.delete(0,'end')
        phe.handle_focus_out()
        self.assertTrue(phe.showing_placeholder)
        self.assertEqual(phe.get(),placeholder)








        












        



