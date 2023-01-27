import unittest
from unittest import mock
from unittest.mock import patch

import tkinter as tk

from mmtk.status_label import (
    OptionError,
    AbstractOption,
    Synonym,
    TextOption,
    FontOption,
    Option,
    Options,
    StatusLabel,
)

from copy import deepcopy

class TestOptionClasses(unittest.TestCase):

    def setUp(self):
        self.states = ("info","warning","error")

        self.font_defaults = {
            "info": {"bold":"cow", "italic":True},
            "warning": {"bold":"pig", "italic":False},
            "error": {"color":"pink", },
        }

        self.option_defaults = {
            "info":{"underline":"please", "nothing":"junk", "font":"curlz"},
            "warning":{"underline":"maybe", "width":-5},
            "whatever":{"underline":"???"},
            None:{"font":"wingdingz"},
        }

    def test_abstract_option(self):
        result = AbstractOption.parse_key("test")
        self.assertEqual(result,("test",None))

        for state in ("info","warning","error"):
            result = AbstractOption.parse_key(state+"test")
            self.assertEqual(result,("test",state))

        with self.assertRaises(OptionError):
            result = AbstractOption.parse_key(None)

        with self.assertRaises(OptionError):
            result = AbstractOption.parse_key({1:1,2:3,3:"cat"})


    def test_synonym_config_entry(self):
        synonyms = {
            "bd":"borderwidth",
            "bg":"background",
            "fg":"foreground",
        }
        for synonym,target in synonyms.items():
            with mock.MagicMock() as tgt:
                tgt.name = target
                syn = Synonym(synonym,{target:tgt})
                self.assertEqual(syn.config_entry(), (synonym,"-"+target))
                for state in self.states:
                    self.assertEqual(
                        syn.config_entry(state), 
                        (state+synonym, "-"+state+target)
                    )

    def test_synonym_config_entries(self):
        synonyms = {
            "bd":"borderwidth",
            "bg":"background",
            "fg":"foreground",
        }
        for synonym,target in synonyms.items():
            with mock.MagicMock() as tgt:
                tgt.name = target
                syn = Synonym(synonym,{target:tgt})
                expected = set(
                    (state+synonym, "-"+state+target)
                    for state in ("",*self.states)
                )
                self.assertEqual( set(syn.config_entries()), expected )

    def test_synonym_update(self):
        # test that update chains to target option
        with mock.MagicMock() as tgt, mock.MagicMock() as widget:
            tgt.name = "foreground"
            syn = Synonym("fg",{"foreground":tgt})
            syn.update(widget,"green")
            self.assertEqual(tgt.update.call_count,1)
            self.assertEqual(tgt.update.call_args.args,(widget,"green",None))

        with mock.MagicMock() as tgt, mock.MagicMock() as widget:
            tgt.name = "background"
            syn = Synonym("bg",{"background":tgt})
            syn.update(widget,"purple", "info")
            self.assertEqual(tgt.update.call_count,1)
            self.assertEqual(tgt.update.call_args.args,(widget,"purple","info"))

    def test_synoynm_exceptions(self):
        with mock.MagicMock() as tgt:
            tgt.name = "background"
            options = {"background":tgt}
            with self.assertRaises(OptionError):
                syn = Synonym("junk",options)
            with self.assertRaises(OptionError):
                syn = Synonym("fg",options)


    def test_font_option_config_entry(self):
        for option in ("italic","bold"):
            fo = FontOption(option)
            for state in self.states:
                expected = (
                    state + option,
                    state + option.title(),
                    state.title() + option.title(),
                    False,
                    False,
                )
                self.assertEqual( fo.config_entry(state), expected )

    def test_font_option_defaults(self):
        fo = FontOption("bold",self.font_defaults)
        self.assertEqual( 
            fo.config_entry("info"),
            ("infobold","infoBold","InfoBold","cow","cow"),
        )
        self.assertEqual( 
            fo.config_entry("warning"),
            ("warningbold","warningBold","WarningBold","pig","pig"),
        )
        self.assertEqual( 
            fo.config_entry("error"),
            ("errorbold","errorBold","ErrorBold",False,False),
        )
        with self.assertRaises(OptionError):
            result = fo.config_entry()

    def test_font_option_config_entries(self):
        fo = FontOption("bold",self.font_defaults)
        expected = {
            ("infobold","infoBold","InfoBold","cow","cow"),
            ("warningbold","warningBold","WarningBold","pig","pig"),
            ("errorbold","errorBold","ErrorBold",False,False),
        }
        actual = fo.config_entries()
        self.assertEqual( set(actual), expected)

    def test_font_option_update(self):
        fo = FontOption("bold",self.font_defaults)

        with mock.MagicMock() as widget:
            widget.state = None
            fo.update(widget,"mini","info")
            expected = {
                ("infobold","infoBold","InfoBold","cow","mini"),
                ("warningbold","warningBold","WarningBold","pig","pig"),
                ("errorbold","errorBold","ErrorBold",False,False),
            }
            actual = fo.config_entries()
            self.assertEqual( set(actual), expected)
            self.assertEqual(widget.update_font.call_count,0)

        with mock.MagicMock() as widget:
            widget.state = "info"
            fo.update(widget,"breadbox","warning")
            expected = {
                ("infobold","infoBold","InfoBold","cow","mini"),
                ("warningbold","warningBold","WarningBold","pig","breadbox"),
                ("errorbold","errorBold","ErrorBold",False,False),
            }
            actual = fo.config_entries()
            self.assertEqual( set(actual), expected)
            self.assertEqual(widget.update_font.call_count,0)

        with mock.MagicMock() as widget:
            widget.state = "info"
            fo.update(widget,"giant","info")
            expected = {
                ("infobold","infoBold","InfoBold","cow","giant"),
                ("warningbold","warningBold","WarningBold","pig","breadbox"),
                ("errorbold","errorBold","ErrorBold",False,False),
            }
            actual = fo.config_entries()
            self.assertEqual( set(actual), expected)
            self.assertEqual(widget.update_font.call_count,1)
            self.assertEqual(widget.update_font.call_args.args,())

    def test_font_option_exceptions(self):
        with self.assertRaises(OptionError):
            fo = FontOption("oops")

        fo = FontOption("italic",self.font_defaults)
        with self.assertRaises(OptionError):
            result = fo.config_entry("nope")

        with mock.MagicMock() as widget, self.assertRaises(OptionError):
            widget.state=None
            fo.update(widget,"oops")


    def test_text_option_config_entry(self):
        to = TextOption()
        self.assertEqual(
            to.config_entry(),
            ("text","text","Text","",""),
        )

    def test_text_option_config_entries(self):
        to = TextOption()
        self.assertEqual(
            to.config_entries(),
            [("text","text","Text","","")],
        )

    def test_text_option_config_entries(self):
        to = TextOption()
        with mock.MagicMock() as widget:
            widget.state = None
            to.update(widget,"hello")
            self.assertEqual(
                to.config_entries(),
                [("text","text","Text","","hello")],
            )
            self.assertEqual(widget.update_text.call_count,1)
            self.assertEqual(widget.update_text.call_args.args,())

        with mock.MagicMock() as widget:
            widget.state = "info"
            to.update(widget,"bye")
            self.assertEqual(
                to.config_entries(),
                [("text","text","Text","","bye")],
            )
            self.assertEqual(widget.update_text.call_count,0)


    def test_option_config_entry(self):
        ref_config = tk.Label().configure()
        for option in ("anchor","background","relief","padx"):
            opt = Option(option)
            expected = ref_config[option]
            self.assertEqual( opt.config_entry(), expected )
            for state in self.states:
                self.assertEqual(
                    opt.config_entry(state),
                    (
                        state + expected[0],
                        state + expected[1][0].title() + expected[1][1:],
                        state.title() + expected[2],
                        expected[3],
                        expected[4],
                    )
                )

    def expected_config(self,option):
        rc = list(tk.Label().configure()[option])
        try:
            default = self.option_defaults[None][option]
            rc[3] = default
            rc[4] = default
        except KeyError:
            pass
        return tuple(rc)

    def expected_config_state(self,option,state):
        rc = list(tk.Label().configure()[option])
        try:
            default = self.option_defaults[state][option]
            rc[3] = default
            rc[4] = default
        except KeyError:
            try:
                default = self.option_defaults[None][option]
                rc[3] = default
                rc[4] = default
            except KeyError:
                pass
        return (
            state + rc[0],
            state + rc[1][0].upper() + rc[1][1:],
            state.title() + rc[2],
            rc[3],
            rc[4],
        )

    def test_option_defaults(self):
        for option in ("underline","width","font"):
            opt = Option(option,self.option_defaults)
            self.assertEqual(
                opt.config_entry(), 
                self.expected_config(option) )
            for state in self.states:
                self.assertEqual(
                    opt.config_entry(state),
                    self.expected_config_state(option,state)
                )

    def test_option_update(self):
        opt = Option("background")
        rc = {
            c[0]:(c[0],c[1],c[2],str(c[3]),c[4]) 
            for c in opt.config_entries()
        }

        with mock.MagicMock() as widget:
            widget.state = None
            opt.update(widget,"green","info")
            tmpl = rc["infobackground"]
            rc["infobackground"] = (*tmpl[:-1],"green")
            actual = {
                c[0]:(c[0],c[1],c[2],str(c[3]),c[4])
                for c in opt.config_entries()
            }
            self.assertEqual(actual,rc)
            self.assertEqual(widget.update_options.call_count,0)

        with mock.MagicMock() as widget:
            widget.state = "warning"
            opt.update(widget,"purple","warning")
            tmpl = rc["warningbackground"]
            rc["warningbackground"] = (*tmpl[:-1],"purple")
            actual = {
                c[0]:(c[0],c[1],c[2],str(c[3]),c[4])
                for c in opt.config_entries()
            }
            self.assertEqual(actual,rc)
            self.assertEqual(widget.update_options.call_count,1)
            self.assertEqual(widget.update_options.call_args.args,())

    def test_option_invalid_arguments(self):
        with self.assertRaises(OptionError):
            opt = Option("squishy")
        with self.assertRaises(OptionError):
            opt = Option("bd")
        with self.assertRaises(OptionError):
            opt = Option("background")
            result = opt.config_entry("crawl")
        with self.assertRaises(OptionError), mock.MagicMock() as w:
            opt = Option("background")
            opt.update(w,"red","fly")


#class Tests(unittest.TestCase):
#    builtin_defaults = {}
#
#    @classmethod
#    def setUpClass(cls):
#        mw = tk.Tk()
#        label_options = dict(tk.Label(mw).configure())
#        mw.destroy()
#
#        cls.base_options = {
#            k:v for k,v in label_options.items()
#            if k in StatusLabel.valid_options
#            if k not in ("italice","bold")
#        }
#
#        for state in StatusLabel.status_states:
#            for option in StatusLabel.valid_options:
#                if option in ("text"):
#                    continue
#                if option in ("bold","italic"):
#                    name = f"{state}{option}"
#                    cls.base_options[name] = (
#                        name,
#                        f"{state}{option.title()}",
#                        f"{state.title()}{option.title()}",
#                        False,
#                        False,
#                    )
#                else:
#                    name,*attr,value = label_options[option]
#                    name = f"{state}{name}"
#                    if attr:
#                        dbName,dbClass,default = attr
#                        attr = (
#                            f"{state}{dbName[0].upper()}{dbName[1:]}",
#                            f"{state.title()}{dbClass}",
#                            default,
#                        )
#                    else:
#                        value = f"-{state}{value[1:]}"
#                    cls.base_options[name] = (name,*attr,value)
#
#        for state,defaults in StatusLabel.option_defaults.items():
#            for k,v in defaults.items():
#                name = f"{state}{k}"
#                cls.base_options[name] = (
#                    name,
#                    cls.base_options[name][1],
#                    cls.base_options[name][2],
#                    v,
#                    v,
#                )
#
#        print("ok")
#
#    def setUp(self):
#        self.mw = tk.Tk()
#
#    def tearDown(self):
#        self.mw.destroy()
#
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
#
#    def test_config(self):
#        sl = StatusLabel(self.mw)
#        sl.pack()
#        actual = sl.configure()
#        self.assertEqual(actual,ref_options)
#
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
#    def test_partition_kwargs(self):
#        actual = StatusLabel._partition_kwargs()
#        expected = ({},{})
#        self.assertEqual(actual,expected)
#
#        actual = StatusLabel._partition_kwargs(
#            info_background = "green",
#            info_foreground = "blue",
#            info_font = "helvetica",
#            warning_font = "courier",
#            warning_background = "black",
#            info_stuff = "ok",
#            stuff = "nope",
#            font = "handwriting",
#            info_test = "test",
#        )
#        expected = (
#            {
#                "stuff":"nope",
#                "font":"handwriting",
#            },
#            {
#                "info": {
#                    "background":"green",
#                    "foreground":"blue",
#                    "font":"helvetica",
#                    "stuff":"ok",
#                    "test":"test",
#                },
#                "warning": {
#                    "font":"courier",
#                    "background":"black",
#                },
#            }
#        )
#        self.assertEqual(actual,expected)
#
#
#    def test_partition_kwargs_exceptions(self):
#        with self.assertRaises(KeyError):
#            StatusLabel._partition_kwargs(info_text="test",validate=True)
#        with self.assertRaises(KeyError):
#            StatusLabel._partition_kwargs(italic=True,validate=True)
#        with self.assertRaises(KeyError):
#            StatusLabel._partition_kwargs(test=3,validate=True)
#        with self.assertRaises(KeyError):
#            StatusLabel._partition_kwargs(warning_test=None,validate=True)
#
#
#    def test_valid_kwargs(self):
#        for opt in StatusLabel.valid_options:
#            if opt in ("italic","bold"):
#                self.assertFalse(
#                    StatusLabel._valid_option(opt),
#                    f"Invalid option {opt} passed validation test",
#                )
#            else:
#                self.assertTrue(
#                    StatusLabel._valid_option(opt),
#                    f"Valid option {opt} failed validation test",
#                )
#
#        for state in ("info","warning","error"):
#            for opt in StatusLabel.valid_options:
#                if opt in ("text"):
#                    self.assertFalse(
#                        StatusLabel._valid_option(opt,state),
#                        f"Invalid option {state}_{opt} passed validation test",
#                    )
#                else:
#                    self.assertTrue(
#                        StatusLabel._valid_option(opt,state),
#                        f"Valid option {state}_{opt} failed validation test",
#                    )
#
#        for opt in StatusLabel.option_synonyms.keys():
#            self.assertTrue(
#                StatusLabel._valid_option(opt),
#                f"Valid synonym {opt} failed validation test",
#            )
#            for state in ("info","warning","error"):
#                self.assertTrue(
#                    StatusLabel._valid_option(opt,state),
#                    f"Valid synonym {state}_{opt} failed validation test",
#                )
#
#        opt = "junk"
#        self.assertFalse(
#            StatusLabel._valid_option(opt),
#            f"Invalid option {opt} passed validation test",
#        )
#        for state in ("info","warning","error"):
#            self.assertFalse(
#                StatusLabel._valid_option(opt,state),
#                f"Invalid option {state}_{opt} passed validation test",
#            )
#
#
