"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

===============================================================================

Purpose: Node Editor testing

===============================================================================

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

===============================================================================
"""
import hashlib
import itertools
import logging
import os
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

import dearpygui.dearpygui as Dear
import dearpygui.themes as DearThemes
import numpy as np
import yaml
from dotmap import DotMap
from MMV.Common.BudgetVsync import BudgetVsyncClient, BudgetVsyncManager
from MMV.Common.DearPyGuiUtils import *
from MMV.Common.PackUnpack import PackUnpack
from MMV.Common.Polyglot import Polyglot
from MMV.Common.Utils import *
from MMV.Common.Utils import Utils
from MMV.Editor.Scene import mmvEditorScene
from MMV.Editor.UI.DearPyStuff import mmvDearPyStuff
from MMV.Editor.UI.Dialogs.LanguageSelect import LanguageSelectUI
from MMV.Sombrero import SombreroMain
from PIL import Image, JpegImagePlugin, PngImagePlugin
from watchdog.observers import Observer

Speak = Polyglot.Speak


class mmvEditor:
    def __init__(self, PackageInterface):

        # Setup Polyglot for translations
        PolyglotMissing = PackageInterface.RuntimeDir/"PolyglotMissing.txt"
        Polyglot.Speak.Init(
            Utils.LoadYaml(PackageInterface.DataDir/"Languages.yaml"),
            PathSaveUnknown=PolyglotMissing)

        # Reset file if exists
        if PolyglotMissing.exists(): PolyglotMissing.write_text("")
        self._Stop = False
        self._mmvRestart_ = False

        # "True" init
        self.PackageInterface = PackageInterface
        self.LoadLastConfig(ForceDefaults=("ResetConfig" in sys.argv))
        self.Scene = mmvEditorScene(self)
        self.DearPyStuff = mmvDearPyStuff(self)

        # Watch for Nodes directory changes
        self.WatchdogNodeDir = Observer()
        T = Utils.WatchdogTemplate()
        T.on_modified = lambda *args: self.Scene.AddNodeFilesDataDirRecursive()
        self.WatchdogNodeDir.schedule(T, self.PackageInterface.NodesDir, recursive=True)
        self.WatchdogNodeDir.start()

        # Shaders
        self.SombreroMain = SombreroMain(MasterShader=True, PackageInterface=self.PackageInterface)

        # Vsync
        self.BudgetVsyncManager = BudgetVsyncManager()

    def InitMainWindow(self): self.DearPyStuff.InitMainWindow()

    # Attempt to load last Context configuration if it existed
    def LoadLastConfig(self, ForceDefaults=False):
        self.USER_CONFIG_FILE = self.PackageInterface.RuntimeDir/"UserConfigEditorContext.pickle.zlib"
        if self.USER_CONFIG_FILE.exists():
            self.Context = ExtendedDotMap(OldSelf=PackUnpack.Unpack(self.USER_CONFIG_FILE), SetCallback=self.SaveCurrentConfig)
            logging.info(f"[mmvEditor.LoadLastConfig] Unpacked last config: [{self.Context}]")
        else: ForceDefaults = True
        
        # Create brand new Context DotMap
        if ForceDefaults: 
            logging.info(f"[mmvEditor.LoadLastConfig] Reset to default config")
            self.Context = ExtendedDotMap(SetCallback=self.SaveCurrentConfig)

        # Set variables (Digest), means that if we had this key before then we
        # set it to what it was, do not default it to the defaults
        self.Context.Digest("GLOBAL_THEME", "Dark")
        self.Context.Digest("FIRST_TIME", True)
        self.Context.Digest("WINDOW_SIZE", [1280, 720])
        self.Context.Digest("BUILTIN_WINDOW_DECORATORS", True)
        self.Context.Digest("START_MAXIMIZED", False)
        self.Context.Digest("UI_SOUNDS", True)
        self.Context.Digest("UI_VOLUME", 40)
        self.Context.Digest("UI_FONT_SIZE", 16)
        self.Context.Digest("DEBUG_SHOW_IDS", True)
        self.Context.Digest("LANGUAGE", Polyglot.Languages.English)
        self.Context.Digest("CENTERED_WINDOWS_VERTICAL_DISTANCE", 200)
        Polyglot.Speak.Language(self.Context.DotMap.LANGUAGE)

        # Global Theme
        {"Dark":  EmptyCallable,
         "Light": DearThemes.create_theme_imgui_light,
        }.get(self.Context.DotMap.GLOBAL_THEME)(default_theme=True)

    # Play some sound from a file (usually UI FX, info, notification)
    def PlaySound(self, file):
        if self.Context.DotMap.UI_SOUNDS:
            subprocess.Popen([
                self.PackageInterface.FFplayBinary, "-loglevel", "panic",
                "-hide_banner", "-volume", f"{self.Context.DotMap.UI_VOLUME}", 
                "-nodisp", "-autoexit", Path(file).resolve()], stdout=subprocess.DEVNULL)

    def MainLoop(self):
        logging.info(f"[mmvEditor.MainLoop] Enter MainLoop, start MMV")
        
        # Init Sombrero
        self.SombreroMain.window.CreateWindow()
        self.SombreroVsyncClient = BudgetVsyncClient(
            60, self.SombreroMain.Next,
            SomeContextToEnter=self.SombreroMain.window.window.ctx)
        self.BudgetVsyncManager.AddVsyncTargetIfDNE(self.SombreroVsyncClient)
        self.Scene.LoadDemoScenePreNodes("Default Scene")

        # DearPyGui
        self.DearPyStuff.SetupViewport()

        # Some GL stuff must be called from the main thread
        self.MainThreadCalls = []
        
        try:
            while True:
                if (self._Stop) or (not Dear.is_dearpygui_running()): break
                
                # Next "Vsynced" action
                ActionDone = self.BudgetVsyncManager.DoNextAction()

                # If we rendered DPg then call ours Next
                if ActionDone == self.BudgetVsyncDearRender:
                    self.Next(ActionDone._Iteration)
                
                # Calls we must do from main thread, mostly GL stuff on Windows
                # Keep popping items and calling them
                while self.MainThreadCalls:
                    self.MainThreadCalls.pop(0)()

        except KeyboardInterrupt: pass
        self.__True_Exit()

    def Next(self, iteration):
        if iteration == 3:
            self.FirstTimeWarning()

    def Exit(self,*a,**b): self._Stop = True
    def Restart(self,*a,**b):
        self._mmvRestart_ = True
        self.Exit()

    def __True_Exit(self):
        logging.info(f"[mmvEditor.AddNodeFile] Exiting [Modular Music Visualizer Editor] *Safely*")
        self.Exit()
        self.SaveCurrentConfig()
        self.SombreroMain.window.window.close()
        Dear.cleanup_dearpygui()

    def SaveCurrentConfig(self): self.Context.Pack(self.USER_CONFIG_FILE)

    # First time opening MMV warning
    def FirstTimeWarning(self):
        if self.Context.DotMap.FIRST_TIME:
            self.Context.ForceSet("FIRST_TIME", False)
            LanguageSelectUI(self)
