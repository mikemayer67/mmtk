import unittest

import tkinter as tk
from mmttk import StatusLabel

from unittest.mock import patch

from copy import deepcopy

class Tests(unittest.TestCase):
    builtin_defaults = {}

    @classmethod
    def setUpClass(cls):
        cls.builtin_defaults = deepcopy(StatusLabel.option_defaults)

    def setUp(self):
        StatusLabel.option_defaults = deepcopy(self.builtin_defaults)
        self.mw = tk.Tk()

    def tearDown(self):
        self.mw.destroy()

    def test_init_defaults(self):
        all_options = set(
            opt for opt in StatusLabel.valid_options
            if opt not in StatusLabel.option_synonyms
        )
        normal_options = set( 
            opt for opt in all_options if opt not in ("italic","bold")
        )
        status_options = set(
            opt for opt in all_options if opt not in ("text")
        )

        status_label = StatusLabel(self.mw)
        actual_options = status_label.configure()
        actual_keys = set(actual_options[None].keys())
        self.assertEqual(actual_keys, normal_options)
        for state in StatusLabel.status_states:
            actual_keys = set(actual_options[state].keys())
            self.assertEqual(actual_keys, status_options)

        for state,options in StatusLabel.option_defaults.items():
            for k,v in options.items():
                self.assertEqual(actual_options[state][k],v)


    def test_init_customized(self):
        all_options = set(
            opt for opt in StatusLabel.valid_options
            if opt not in StatusLabel.option_synonyms
        )
        normal_options = set( 
            opt for opt in all_options if opt not in ("italic","bold")
        )
        status_options = set(
            opt for opt in all_options if opt not in ("text")
        )

        status_label = StatusLabel(
            self.mw,
            font="test font",
            info_font = "info font",
            warning_font = "warning font",
            error_italic = True,
            bg = "test color",
        )
        actual_options = status_label.configure()
        actual_keys = set(actual_options[None].keys())
        self.assertEqual(actual_keys, normal_options)
        for state in StatusLabel.status_states:
            actual_keys = set(actual_options[state].keys())
            self.assertEqual(actual_keys, status_options)
        self.assertEqual(actual_options[None]["font"],"test font")
        self.assertEqual(actual_options["info"]["font"],"info font")
        self.assertEqual(actual_options["warning"]["font"],"warning font")
        self.assertEqual(actual_options["error"]["italic"],True)
        self.assertEqual(actual_options[None]["background"],"test color")

    def test_init_exceptions(self):
        with self.assertRaises(TypeError):
            sl = StatusLabel(self.mw,"bad arg")
        with self.assertRaises(AttributeError):
            sl = StatusLabel("missing parent")
        with self.assertRaises(KeyError):
            sl = StatusLabel(self.mw,italic=True)
        with self.assertRaises(KeyError):
            sl = StatusLabel(self.mw,info_text="hello")
        with self.assertRaises(KeyError):
            sl = StatusLabel(self.mw,strkey="hello")

    def test_configure(self):
        sl = StatusLabel(self.mw)
        sl.pack()

        with (
            patch.object(StatusLabel,'_configure') as mock_inst,
             patch.object(StatusLabel,"configure_defaults") as mock_class,
        ):
            sl.configure(text="help me")
            self.assertEqual(mock_inst.call_count,1)
            self.assertEqual(mock_class.call_count,0)

        with (
            patch.object(StatusLabel,'_configure') as mock_inst,
             patch.object(StatusLabel,"configure_defaults") as mock_class,
        ):
            StatusLabel.configure(text="help me")
            self.assertEqual(mock_inst.call_count,0)
            self.assertEqual(mock_class.call_count,1)

    def test_cget(self):
        sl = StatusLabel(self.mw)
        sl.pack()

        with (
            patch.object(StatusLabel,'_cget') as mock_inst,
             patch.object(StatusLabel,"cget_default") as mock_class,
        ):
            sl.cget("option")
            self.assertEqual(mock_inst.call_count,1)
            self.assertEqual(mock_class.call_count,0)

        with (
            patch.object(StatusLabel,'_cget') as mock_inst,
             patch.object(StatusLabel,"cget_default") as mock_class,
        ):
            StatusLabel.cget("option")
            self.assertEqual(mock_inst.call_count,0)
            self.assertEqual(mock_class.call_count,1)


    def test_partition_kwargs(self):
        actual = StatusLabel._partition_kwargs()
        expected = {k:dict() for k in ("info","warning","error",None)}
        self.assertEqual(actual,expected)

        actual = StatusLabel._partition_kwargs(
            info_background = "green",
            info_foreground = "blue",
            info_font = "helvetica",
            warning_font = "courier",
            warning_background = "black",
            info_stuff = "ok",
            stuff = "nope",
            font = "handwriting",
            info_test = "test",
        )
        expected = {
            "info": {
                "background":"green",
                "foreground":"blue",
                "font":"helvetica",
                "stuff":"ok",
                "test":"test",
            },
            "warning": {
                "font":"courier",
                "background":"black",
            },
            "error": {},
            None: {
                "stuff":"nope",
                "font":"handwriting",
            },
        }
        self.assertEqual(actual,expected)

    def test_partition_kwargs_exceptions(self):
        with self.assertRaises(KeyError):
            StatusLabel._partition_kwargs(info_text="test",validate=True)
        with self.assertRaises(KeyError):
            StatusLabel._partition_kwargs(italic=True,validate=True)
        with self.assertRaises(KeyError):
            StatusLabel._partition_kwargs(test=3,validate=True)
        with self.assertRaises(KeyError):
            StatusLabel._partition_kwargs(warning_test=None,validate=True)


    def test_configure_defaults(self):
        expected = deepcopy(StatusLabel.option_defaults)
        actual = StatusLabel.configure_defaults()
        self.assertEqual(actual,expected)

        actual = StatusLabel.configure(info_new = "howdy")
        expected["info"]["new"] = "howdy"
        self.assertEqual(actual,expected)

        actual = StatusLabel.configure(error_italic=True)
        expected["error"]["italic"] = True
        self.assertEqual(actual,expected)

        actual = StatusLabel.configure()
        self.assertEqual(actual,expected)

    def test_cget_defaults(self):
        for state, defaults in StatusLabel.option_defaults.items():
            for option, value in defaults.items():
                if state:
                    self.assertEqual(StatusLabel.cget(f"{state}{option}"), value)
                    self.assertEqual(StatusLabel.cget(f"{state}_{option}"), value)
                    self.assertEqual(StatusLabel.cget(f"{state}__{option}"), value)
                else:
                    self.assertEqual(StatusLabel.cget(option), value)


    def test_valid_kwargs(self):
        for opt in StatusLabel.valid_options:
            if opt in ("italic","bold"):
                self.assertFalse(
                    StatusLabel._valid_option(opt),
                    f"Invalid option {opt} passed validation test",
                )
            else:
                self.assertTrue(
                    StatusLabel._valid_option(opt),
                    f"Valid option {opt} failed validation test",
                )

        for state in ("info","warning","error"):
            for opt in StatusLabel.valid_options:
                if opt in ("text"):
                    self.assertFalse(
                        StatusLabel._valid_option(opt,state),
                        f"Invalid option {state}_{opt} passed validation test",
                    )
                else:
                    self.assertTrue(
                        StatusLabel._valid_option(opt,state),
                        f"Valid option {state}_{opt} failed validation test",
                    )

        for opt in StatusLabel.option_synonyms.keys():
            self.assertTrue(
                StatusLabel._valid_option(opt),
                f"Valid synonym {opt} failed validation test",
            )
            for state in ("info","warning","error"):
                self.assertTrue(
                    StatusLabel._valid_option(opt,state),
                    f"Valid synonym {state}_{opt} failed validation test",
                )

        opt = "junk"
        self.assertFalse(
            StatusLabel._valid_option(opt),
            f"Invalid option {opt} passed validation test",
        )
        for state in ("info","warning","error"):
            self.assertFalse(
                StatusLabel._valid_option(opt,state),
                f"Invalid option {state}_{opt} passed validation test",
            )


