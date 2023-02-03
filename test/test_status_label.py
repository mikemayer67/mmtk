# Author: Michael A. Mayer
# Copyright: 2023, VMWishes
# License: UNLICENSE (http://unlicense.org)

import unittest
from unittest import mock
from unittest.mock import patch
from unittest.mock import MagicMock

import tkinter as tk
from tkinter.font import Font
import re
from numbers import Number

from mmtk.status_label import (
    Option,
    Synonym,
    FontOption,
    Options,
    StatusLabel,
)
from mmtk.status_label import (
    OptionError,
    parse_key,
)

from copy import deepcopy

class TestOptionClasses(unittest.TestCase):

    def setUp(self):
        self.states = ("info","warning","error")

        self.font_defaults = {
            "bold": {
                "info":"cow",
                "warning":"pig",
            },
            "italic": {
                "info":True,
                "warning":False,
            },
        }

        self.option_defaults = {
            "underline": {
                "info":"please",
                "warning":"maybe",
                "whatever":"???",
            },
            "font": {"info":"curlz", None:"wingdingz"},
            "width": {"warning":-5},
        }

    def test_abstract_option(self):
        result = parse_key("test")
        self.assertEqual(result,("test",None))

        for state in ("info","warning","error"):
            result = parse_key(state+"test")
            self.assertEqual(result,("test",state))

        with self.assertRaises(OptionError):
            result = parse_key(None)

        with self.assertRaises(OptionError):
            result = parse_key({1:1,2:3,3:"cat"})


    def test_synonym_config_entry(self):
        synonyms = {
            "bd":"borderwidth",
            "bg":"background",
            "fg":"foreground",
        }
        for synonym,target in synonyms.items():
            # implicitly follow the link to the target
            with MagicMock() as tgt:
                tgt.name = target
                syn = Synonym(synonym,{target:tgt})
                result = syn.config_entry()
                for state in self.states:
                    result = syn.config_entry(state)
                self.assertEqual(
                    [c.args for c in tgt.method_calls],
                    [(c,) for c in (None,*self.states)]
                )

            # explicitly follow the link to the target
            with MagicMock() as tgt:
                tgt.name = target
                syn = Synonym(synonym,{target:tgt})
                result = syn.config_entry(follow_link=True)
                for state in self.states:
                    result = syn.config_entry(state,follow_link=True)
                self.assertEqual(
                    [c.args for c in tgt.method_calls],
                    [(c,) for c in (None,*self.states)]
                )

            # show the link without following it
            with MagicMock() as tgt:
                tgt.name = target
                syn = Synonym(synonym,{target:tgt})
                result = syn.config_entry(follow_link=False)
                self.assertEqual(result,(synonym,"-"+target))
                for state in self.states:
                    result = syn.config_entry(state,follow_link=False)
                    self.assertEqual(result,(state+synonym,"-"+state+target))

    def test_synonym_config_entries(self):
        synonyms = {
            "bd":"borderwidth",
            "bg":"background",
            "fg":"foreground",
        }
        for synonym,target in synonyms.items():
            with MagicMock() as tgt:
                tgt.name = target
                syn = Synonym(synonym,{target:tgt})
                expected = set(
                    (state+synonym, "-"+state+target)
                    for state in ("",*self.states)
                )
                self.assertEqual( set(syn.config_entries()), expected )

    def test_synonym_update(self):
        # test that update chains to target option
        with MagicMock() as tgt:
            tgt.name = "foreground"
            syn = Synonym("fg",{"foreground":tgt})
            syn.update("green")
            self.assertEqual(tgt.update.call_count,1)
            self.assertEqual(tgt.update.call_args.args,("green",None))

        with MagicMock() as tgt:
            tgt.name = "background"
            syn = Synonym("bg",{"background":tgt})
            syn.update("purple", "info")
            self.assertEqual(tgt.update.call_count,1)
            self.assertEqual(tgt.update.call_args.args,("purple","info"))

    def test_synonym_value(self):
        with MagicMock() as tgt:
            tgt.name="borderwidth"
            syn = Synonym("bd",{"borderwidth":tgt})
            v = syn.value()
            vx = [syn.value(s) for s in self.states]
            self.assertEqual(
                [c.args for c in tgt.method_calls],
                [(s,) for s in (None,*self.states)]
            )


    def test_synoynm_exceptions(self):
        with MagicMock() as tgt:
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
        defaults = deepcopy(self.font_defaults["bold"])
        common = defaults.pop(None,None)
        fo = FontOption("bold",**defaults)
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
        defaults = deepcopy(self.font_defaults["bold"])
        common = defaults.pop(None,None)
        fo = FontOption("bold",**defaults)
        expected = {
            ("infobold","infoBold","InfoBold","cow","cow"),
            ("warningbold","warningBold","WarningBold","pig","pig"),
            ("errorbold","errorBold","ErrorBold",False,False),
        }
        actual = fo.config_entries()
        self.assertEqual( set(actual), expected)

    def test_font_option_update(self):
        defaults = deepcopy(self.font_defaults["bold"])
        common = defaults.pop(None,None)
        fo = FontOption("bold",common,**defaults)

        fo.update("mini","info")
        expected = {
            ("infobold","infoBold","InfoBold","cow","mini"),
            ("warningbold","warningBold","WarningBold","pig","pig"),
            ("errorbold","errorBold","ErrorBold",False,False),
        }
        actual = fo.config_entries()
        self.assertEqual( set(actual), expected)

        fo.update("breadbox","warning")
        expected = {
            ("infobold","infoBold","InfoBold","cow","mini"),
            ("warningbold","warningBold","WarningBold","pig","breadbox"),
            ("errorbold","errorBold","ErrorBold",False,False),
        }
        actual = fo.config_entries()
        self.assertEqual( set(actual), expected)

        fo.update("giant","info")
        expected = {
            ("infobold","infoBold","InfoBold","cow","giant"),
            ("warningbold","warningBold","WarningBold","pig","breadbox"),
            ("errorbold","errorBold","ErrorBold",False,False),
        }
        actual = fo.config_entries()
        self.assertEqual( set(actual), expected)

    def test_font_option_exceptions(self):
        with self.assertRaises(OptionError):
            fo = FontOption("oops")

        fo = FontOption("italic",**self.font_defaults)
        with self.assertRaises(OptionError):
            result = fo.config_entry("nope")

        with self.assertRaises(OptionError):
            fo.update("oops")


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
            default = self.option_defaults[option][None]
            rc[3] = default
            rc[4] = default
        except KeyError:
            pass
        return tuple(rc)

    def expected_config_state(self,option,state):
        rc = list(tk.Label().configure()[option])
        try:
            defaults = self.option_defaults[option]
        except:
            pass
        else:
            rc[3] = defaults.get(None,rc[3])
            rc[4] = defaults.get(state,defaults.get(None,rc[4]))

        return (
            state + rc[0],
            state + rc[1][0].upper() + rc[1][1:],
            state.title() + rc[2],
            rc[3],
            rc[4],
        )

    def test_option_defaults(self):
        for option in ("underline","width","font"):
            defaults = deepcopy(self.option_defaults.get(option,{}))
            common = defaults.pop(None,None)
            opt = Option(option,common,**defaults)
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

        opt.update("green","info")
        tmpl = rc["infobackground"]
        rc["infobackground"] = (*tmpl[:-1],"green")
        actual = {
            c[0]:(c[0],c[1],c[2],str(c[3]),c[4])
            for c in opt.config_entries()
        }
        self.assertEqual(actual,rc)

        opt.update("purple","warning")
        tmpl = rc["warningbackground"]
        rc["warningbackground"] = (*tmpl[:-1],"purple")
        actual = {
            c[0]:(c[0],c[1],c[2],str(c[3]),c[4])
            for c in opt.config_entries()
        }
        self.assertEqual(actual,rc)


    def test_option_invalid_arguments(self):
        with self.assertRaises(OptionError):
            opt = Option("squishy")
        with self.assertRaises(OptionError):
            opt = Option("bd")
        with self.assertRaises(OptionError):
            opt = Option("background")
            result = opt.config_entry("crawl")
        with self.assertRaises(OptionError):
            opt = Option("background")
            opt.update("red","fly")


class TestOptions (unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.states = ("info","warning","error")

        cls.base_options = {
            *Option.recognized_options(),
            *FontOption.recognized_options(),
            *Synonym.recognized_synonyms(),
        }

        cls.all_options = set()
        cls.all_options.update([
            state+option
            for state in cls.states
            for option in FontOption.recognized_options()
        ])
        cls.all_options.update([
            state+option
            for state in ("",*cls.states)
            for option in Option.recognized_options()
        ])
        cls.all_options.update([
            state+synonym
            for state in ("",*cls.states)
            for synonym in Synonym.recognized_synonyms()
        ])


    def test_default_init(self):

        # verify all options are set
        mock_init_calls = set()
        def mock_init(s,n,*args,**kwargs):
            mock_init_calls.add(n)
            s.name = n

        with (
            patch.object(Option,"__init__",mock_init),
            patch.object(FontOption,"__init__",mock_init),
            patch.object(Synonym,"__init__",mock_init),
            patch.object(Options,"configure") as mock_configure,
        ):
            options = Options()
            self.assertEqual(mock_init_calls, self.base_options)

        #verify that the builtins are set correctly
        options = Options()
        for state,defaults in Options._defaults.items():
            for option,value in defaults.items():
                self.assertEqual(
                    options.cget((state or "")+option),
                    value,
                )


    def test_init_with_kwargs(self):
        options = Options(
            infobg="green",
            warningbold=True,
            relief="ridge",
            infobd=5,
        )
        self.assertEqual(options.cget("infobg"),"green")
        self.assertEqual(options.cget("warningbold"),True)
        self.assertEqual(options.cget("relief"),"ridge")
        self.assertEqual(options.cget("infobd"),5)

    def test_init_exceptions(self):
        with self.assertRaises(OptionError):
            options = Options(
                junk=5,
            )

    def test_configure_query_all(self):
        options = Options()
        result = options.configure()
        self.assertEqual(result.keys(), self.all_options)
        for key,config in result.items():
            self.assertEqual(key,config[0])
            option = re.sub(r"^(info|warning|error)","",key)
            if option in Synonym.recognized_synonyms():
                self.assertEqual(len(config),2)
            else:
                self.assertEqual(len(config),5)

    def test_configure_query_option(self):
        options = Options()
        syn = "|".join(Synonym.recognized_synonyms())
        syn_re = re.compile(rf"^(info|warning|error)?({syn})$")
        for option in self.all_options:
            result = options.configure(option)
            self.assertEqual(len(result),5)
            m = syn_re.search(option)
            if m:
                state = m.group(1) or ""
                target = Synonym._synonym_map[m.group(2)]
                name = state + target
            else:
                name = option
            self.assertEqual(result[0],name)

    def test_configure_set_options(self):
        options = Options()
        options.configure(
            background="pink",
            errorrelief="groove",
            infobd=12,
        )
        self.assertEqual(options.cget("background"),"pink")
        self.assertEqual(options.cget("bg"),"pink")
        self.assertEqual(options.cget("errorrelief"),"groove")
        self.assertEqual(options.cget("infobd"),12)
        self.assertEqual(options.cget("infoborderwidth"),12)

    def test_configure_query_exceptions(self):
        options = Options()
        with self.assertRaises(OptionError):
            result = options.configure("junk")
        with self.assertRaises(OptionError):
            result = options.configure("infotext")
        with self.assertRaises(OptionError):
            result = options.configure(junk=5)


    def test_cget(self):
        options = Options()
        for option in self.all_options:
            result = options.cget(option)
            assert any([
                result is None,
                type(result) is str,
                isinstance(result,Number),
                isinstance(result,tk.font.Font),
                isinstance(result,tk._tkinter.Tcl_Obj),
            ]), (
                f"Unexpected result type: {type(result)} for {option}"
            )

    def test_option_cascade(self):
        options = Options(
            bg = "black",
            infobg = None,
            warningbg = None,
            errorbg = None,
        )
        self.assertEqual(options.cget("bg"),"black")
        self.assertEqual(options.cget("background"),"black")
        self.assertEqual(options.cget("infobg"),"black")
        self.assertEqual(options.cget("infobackground"),"black")
        self.assertEqual(options.cget("warningbg"),"black")
        self.assertEqual(options.cget("warningbackground"),"black")
        self.assertEqual(options.cget("errorbg"),"black")
        self.assertEqual(options.cget("errorbackground"),"black")

    def test_font_method(self):
        options = Options(
            infoitalic=True,
            infobold=False,
            warningitalic=True,
            warningbold=True,
            erroritalic=False,
            errorbold=True,
        )
        base = tk.font.nametofont(options.font()).actual()
        font = options.font("info").actual()
        self.assertEqual(font['slant'],"italic")
        for prop in ('family','weight','size'):
            self.assertEqual(font[prop], base[prop])

        font = options.font("warning").actual()
        self.assertEqual(font['slant'],"italic")
        self.assertEqual(font['weight'],"bold")
        for prop in ('family','size'):
            self.assertTrue(font[prop], base[prop])

        font = options.font("error").actual()
        self.assertEqual(font['weight'],"bold")
        for prop in ('family','size','slant'):
            self.assertTrue(font[prop], base[prop])

        test_font = 'systemLabelFont'
        options = Options(
            infofont=test_font,
            infoitalic=True,
        )
        base = tk.font.nametofont(test_font).actual()
        font = options.font("info").actual()
        self.assertEqual(font['slant'],"italic")
        for prop in ('family','weight','size'):
            self.assertEqual(font[prop], base[prop])

        for invalid_font in (5, options, MagicMock()):
            options = Options(warningfont=invalid_font, warningbold=True)
            with self.assertRaises(OptionError):
                font = options.font("warning")

    def test_kwargs(self):
        options = Options(infoitalic=True)

        expected_options = Option.recognized_options()
        config = options.kwargs()
        self.assertEqual( set(config.keys()), expected_options)
        for k,v in config.items():
            self.assertEqual(v,options.cget(k))

        for state in self.states:
            config = options.kwargs(state)
            self.assertEqual( set(config.keys()), expected_options)
            for k,v in config.items():
                if k == "font":
                    vfont = v
                    if not isinstance(vfont,Font):
                        vfont = tk.font.nametofont(v)
                    ofont = options.cget(state+k)
                    if not isinstance(ofont,Font):
                        ofont = tk.font.nametofont(ofont)
                    self.assertEqual(vfont.actual(), ofont.actual())
                else:
                    self.assertEqual(v,options.cget(state+k))


class TestStatusLabel(unittest.TestCase):
    def setUp(self):
        self.mw = tk.Tk()

    def tearDown(self):
        self.mw.destroy()

    def test_default_init(self):
        with (
            patch.object(Options,"__new__") as mock_new,
            patch.object(Options,"__init__") as mock_init,
        ):
            sl = StatusLabel(self.mw)
            self.assertEqual(sl.state,None)
            self.assertEqual(sl.text,"")
            self.assertEqual(mock_new.call_count,1)
            self.assertEqual(mock_new.call_args_list[0].kwargs,{})

    def test_item_accessors(self):
        with patch.object(StatusLabel,"__getitem__") as mock_get:
            sl = StatusLabel(self.mw)
            bg = sl["background"]
            self.assertEqual(mock_get.call_count,1)
            self.assertEqual(
                mock_get.call_args_list[0].args,
                ("background",)
            )

        with patch.object(StatusLabel,"__setitem__") as mock_set:
            sl = StatusLabel(self.mw)
            sl["background"] = "green"
            self.assertEqual(mock_set.call_count,1)
            self.assertEqual(
                mock_set.call_args_list[0].args,
                ("background","green")
            )

    def test_state_calls(self):
        sl = StatusLabel(self.mw)
        self.assertEqual(sl.state,None)
        self.assertEqual(sl.text,"")
        
        info_msg = "This is just FYI"
        sl.info(info_msg)
        self.assertEqual(sl.state,"info")
        self.assertEqual(sl.text,"")
        self.assertEqual(sl.cget("text"),info_msg)

        warning = "I got a bad feeling about this"
        sl.warning(warning)
        self.assertEqual(sl.state,"warning")
        self.assertEqual(sl.text,"")
        self.assertEqual(sl.cget("text"),warning)

        error = "Well... now you've done it"
        sl.error(error)
        self.assertEqual(sl.state,"error")
        self.assertEqual(sl.text,"")
        self.assertEqual(sl.cget("text"),error)

        ok = "The new normal"
        sl.clear(ok)
        self.assertIsNone(sl.state)
        self.assertEqual(sl.text,ok)
        self.assertEqual(sl.cget("text"),ok)




