import unittest

import tkinter as tk
from mmttk import StatusLabel

from unittest.mock import patch

from copy import deepcopy


class Tests(unittest.TestCase):
    builtin_defaults = {}

    @classmethod
    def setUpClass(cls):
        mw = tk.Tk()
        label_options = dict(tk.Label(mw).configure())
        mw.destroy()

        cls.base_options = {
            k:v for k,v in label_options.items()
            if k in StatusLabel.valid_options
            if k not in ("italice","bold")
        }

        for state in StatusLabel.status_states:
            for option in StatusLabel.valid_options:
                if option in ("text"):
                    continue
                if option in ("bold","italic"):
                    name = f"{state}{option}"
                    cls.base_options[name] = (
                        name,
                        f"{state}{option.title()}",
                        f"{state.title()}{option.title()}",
                        False,
                        False,
                    )
                else:
                    name,*attr,value = label_options[option]
                    name = f"{state}{name}"
                    if attr:
                        dbName,dbClass,default = attr
                        attr = (
                            f"{state}{dbName[0].upper()}{dbName[1:]}",
                            f"{state.title()}{dbClass}",
                            default,
                        )
                    else:
                        value = f"-{state}{value[1:]}"
                    cls.base_options[name] = (name,*attr,value)

        for state,defaults in StatusLabel.option_defaults.items():
            for k,v in defaults.items():
                name = f"{state}{k}"
                cls.base_options[name] = (
                    name,
                    cls.base_options[name][1],
                    cls.base_options[name][2],
                    v,
                    v,
                )

        print("ok")

    def setUp(self):
        self.mw = tk.Tk()

    def tearDown(self):
        self.mw.destroy()

#    def test_init_defaults(self):
#        all_options = set(
#            opt for opt in StatusLabel.valid_options
#            if opt not in StatusLabel.option_synonyms
#        )
#        normal_options = set( 
#            opt for opt in all_options if opt not in ("italic","bold")
#        )
#        status_options = set(
#            opt for opt in all_options if opt not in ("text")
#        )
#
#        status_label = StatusLabel(self.mw)
#        actual_options = status_label.configure()
#        actual_keys = set(actual_options[None].keys())
#        self.assertEqual(actual_keys, normal_options)
#        for state in StatusLabel.status_states:
#            actual_keys = set(actual_options[state].keys())
#            self.assertEqual(actual_keys, status_options)
#
#        for state,options in StatusLabel.option_defaults.items():
#            for k,v in options.items():
#                self.assertEqual(actual_options[state][k],v)
#
#
#    def test_init_customized(self):
#        all_options = set(
#            opt for opt in StatusLabel.valid_options
#            if opt not in StatusLabel.option_synonyms
#        )
#        normal_options = set( 
#            opt for opt in all_options if opt not in ("italic","bold")
#        )
#        status_options = set(
#            opt for opt in all_options if opt not in ("text")
#        )
#
#        status_label = StatusLabel(
#            self.mw,
#            font="test font",
#            info_font = "info font",
#            warning_font = "warning font",
#            error_italic = True,
#            bg = "test color",
#        )
#        actual_options = status_label.configure()
#        actual_keys = set(actual_options[None].keys())
#        self.assertEqual(actual_keys, normal_options)
#        for state in StatusLabel.status_states:
#            actual_keys = set(actual_options[state].keys())
#            self.assertEqual(actual_keys, status_options)
#
#        self.assertEqual(actual_options[None]["font"],"test font")
#        self.assertEqual(actual_options["info"]["font"],"info font")
#        self.assertEqual(actual_options["warning"]["font"],"warning font")
#        self.assertEqual(actual_options["error"]["italic"],True)
#        self.assertEqual(actual_options[None]["background"],"test color")
#
#    def test_init_exceptions(self):
#        with self.assertRaises(TypeError):
#            sl = StatusLabel(self.mw,"bad arg")
#        with self.assertRaises(AttributeError):
#            sl = StatusLabel("missing parent")
#        with self.assertRaises(KeyError):
#            sl = StatusLabel(self.mw,italic=True)
#        with self.assertRaises(KeyError):
#            sl = StatusLabel(self.mw,info_text="hello")
#        with self.assertRaises(KeyError):
#            sl = StatusLabel(self.mw,strkey="hello")

#    def test_cvt_opt(self):
#        ref_options = dict(tk.Label(self.mw).configure())
#        sl = StatusLabel(self.mw,info_bd=25)
#        sl.pack()
#
#        # inherited from tk.Level
#        actual = sl._cvt_opt(ref_options['background'],"info")
#        expected = (
#            "infobackground",
#            "infoBackground",
#            ref_options["background"][2],
#            ref_options["background"][3],
#            ref_options["background"][4],
#        )
#        self.assertEqual(actual,expected)
#
#        # StatusLabel default value
#        actual = sl._cvt_opt(ref_options['background'],"warning")
#        expected = (
#            "warningbackground",
#            "warningBackground",
#            ref_options["background"][2],
#            StatusLabel.option_defaults["warning"]["background"],
#            StatusLabel.option_defaults["warning"]["background"],
#        )
#        self.assertEqual(actual,expected)
#
#        # explicitly set on init
#        actual = sl._cvt_opt(ref_options['borderwidth'],"info")
#        expected = (
#            "infoborderwidth",
#            "infoBorderWidth",
#            ref_options["borderwidth"][2],
#            ref_options["borderwidth"][3],
#            25,
#        )
#        self.assertEqual(actual,expected)
#
#        # explicitly set overrides StatusLabel default value
#        sl = StatusLabel(self.mw,warning_bg="test_color")
#        actual = sl._cvt_opt(ref_options['background'],"warning")
#        expected = (
#            "warningbackground",
#            "warningBackground",
#            ref_options["background"][2],
#            StatusLabel.option_defaults["warning"]["background"],
#            "test_color",
#        )
#        self.assertEqual(actual,expected)
#
#        # synonym
#        actual = sl._cvt_opt(ref_options['bg'],"info")
#        expected = (
#            "infobg",
#            "-infobackground",
#        )
#        self.assertEqual(actual,expected)
#
#    def test_config_with_key(self):
#        ref_options = dict(tk.Label(self.mw).configure())
#        
#        sl = StatusLabel(self.mw)
#        sl.pack()
#
#        with (
#            patch.object(tk.Misc,"configure") as mock_config,
#            patch.object(StatusLabel,"_cvt_opt") as mock_cvt,
#        ):
#            actual = sl.configure("background")
#            self.assertEqual(mock_config.call_count,1)
#            self.assertEqual(mock_cvt.call_count,0)
#
#        with (
#            patch.object(tk.Misc,"configure") as mock_config,
#            patch.object(StatusLabel,"_cvt_opt") as mock_cvt,
#        ):
#            actual = sl.configure("info_background")
#            self.assertEqual(mock_config.call_count,1)
#            self.assertEqual(mock_cvt.call_count,1)
#

    def test_config(self):
        sl = StatusLabel(self.mw)
        sl.pack()
        actual = sl.configure()
        self.assertEqual(actual,ref_options)

#    def test_cget(self):
#        sl = StatusLabel(self.mw)
#        sl.pack()
#
#        with (
#            patch.object(StatusLabel,'_cget') as mock_inst,
#            patch.object(StatusLabel,"cget_default") as mock_class,
#        ):
#            sl.cget("option")
#            self.assertEqual(mock_inst.call_count,1)
#            self.assertEqual(mock_class.call_count,0)
#
#        with (
#            patch.object(StatusLabel,'_cget') as mock_inst,
#             patch.object(StatusLabel,"cget_default") as mock_class,
#        ):
#            StatusLabel.cget("option")
#            self.assertEqual(mock_inst.call_count,0)
#            self.assertEqual(mock_class.call_count,1)
#
#
    def test_partition_kwargs(self):
        actual = StatusLabel._partition_kwargs()
        expected = ({},{})
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
        expected = (
            {
                "stuff":"nope",
                "font":"handwriting",
            },
            {
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
            }
        )
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


