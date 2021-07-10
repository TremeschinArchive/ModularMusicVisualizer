"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

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
import importlib.util
import itertools
import logging
import subprocess
import threading
import webbrowser
from pathlib import Path

import dearpygui.dearpygui as Dear
import numpy as np
import yaml
from dotmap import DotMap
from mmv.Common.PackUnpack import PackUnpack
from mmv.Common.Utils import Utils
from mmv.Editor.EditorUtils import (AssignLocals, CenteredWindow,
                                    EnterContainerStack, ExtendedDotMap,
                                    NewHash, PayloadTypes, ToggleAttrSafe,
                                    WatchdogTemplate)
from mmv.Editor.Localization import Polyglot
from mmv.Editor.Scene import mmvEditorScene
from mmv.Editor.UI.AddNodeUI import mmvEditorAddNodeUI
from mmv.Editor.UI.MenuBarUI import mmvEditorMenuBarUI
from PIL import Image, JpegImagePlugin, PngImagePlugin
from watchdog.observers import Observer

Speak = Polyglot.Speak

class mmvEditor:
    def __init__(self, PackageInterface):
        Polyglot.Speak.Init(PackageInterface.DataDir/"Languages.yaml")

        self.LoadedFonts = DotMap(_dynamic=False)
        self.DefaultFont = "DejaVuSans-Bold.ttf"

        # Stuff we can access
        self.EnterContainerStack = EnterContainerStack
        self.PayloadTypes = PayloadTypes
        self.CenteredWindow = CenteredWindow
        self.AssignLocals = Utils.AssignLocals
        self.ToggleAttrSafe = ToggleAttrSafe
        self.NewHash = NewHash
        self.ExtendedDotMap = ExtendedDotMap

        # "True" init
        self.PackageInterface = PackageInterface
        self.DefaultResourcesLogoImage = self.PackageInterface.ImageDir/"mmvLogoWhite.png"
        # self.DefaultResourcesIcon = self.PackageInterface.ImageDir/"mmvLogoWhite.ico"
        self.LoadLastConfig()
        self.MenuBarUI = mmvEditorMenuBarUI(self)
        self.AddNodeUI = mmvEditorAddNodeUI(self)
        self.Scene = mmvEditorScene(self)

        # Watch for Nodes directory changes
        self.WatchdogNodeDir = Observer()
        T = WatchdogTemplate()
        T.on_modified = lambda *args: self.Scene.AddNodeFilesDataDirRecursive()
        self.WatchdogNodeDir.schedule(T, self.PackageInterface.NodesDir, recursive=True)
        self.WatchdogNodeDir.start()

        # Interactive
        self.MouseDown = False
        self.ViewportX = 0
        self.ViewportY = 0

    # Attempt to load last Context configuration if it existed
    def LoadLastConfig(self, ForceDefaults=False):
        self.USER_CONFIG_FILE = self.PackageInterface.RuntimeDir/"UserEditorConfig.pickle.zlib"
        if self.USER_CONFIG_FILE.exists():
            self.Context = ExtendedDotMap(
                OldSelf=PackUnpack.Unpack(self.USER_CONFIG_FILE),
                SetCallback=self.SaveCurrentConfig )
            logging.info(f"[mmvEditor.LoadLastConfig] Unpacked last config: [{self.Context}]")
        else: ForceDefaults = True
        
        # Create brand new Context DotMap
        if ForceDefaults: 
            logging.info(f"[mmvEditor.LoadLastConfig] Reset to default config")
            self.Context = ExtendedDotMap(SetCallback=self.SaveCurrentConfig)

        self.Context.Digest("FIRST_TIME", True)
        self.Context.Digest("WINDOW_SIZE", [1280, 720])
        self.Context.Digest("BUILTIN_WINDOW_DECORATORS", True)
        self.Context.Digest("START_MAXIMIZED", False)
        self.Context.Digest("UI_SOUNDS", True)
        self.Context.Digest("UI_VOLUME", 40)
        self.Context.Digest("UI_FONT_SIZE", 16)
        self.Context.Digest("DEBUG_SHOW_IDS", True)
        self.Context.Digest("LANGUAGE", Polyglot.Languages.English)
        Polyglot.Speak.Language(self.Context.DotMap.LANGUAGE)

    # Play some sound from a file (usually UI FX, info, notification)
    def PlaySound(self, file):
        if self.Context.DotMap.UI_SOUNDS:
            subprocess.Popen([
                self.PackageInterface.FFplayBinary, "-loglevel", "panic",
                "-hide_banner", "-volume", f"{self.Context.DotMap.UI_VOLUME}", 
                "-nodisp", "-autoexit", Path(file).resolve()], stdout=subprocess.DEVNULL)

    # Adds a image on current DPG stack, returns the raw numpy array of its content and the
    # assigned DearPyGui id
    def AddDynamicTexture(self, path, size=100) -> np.ndarray:
        
        self.ToggleLoadingIndicator()
        img = Image.open(path).convert("RGBA")
        original_image_data = np.array(img)
        width, height = img.size
        ratio = width / height
        img = img.resize((int(size*ratio), int(size)), resample=Image.LANCZOS)
        width, height = img.size
        data = np.array(img).reshape(-1)
        tex = Dear.add_dynamic_texture(width, height, list(data/256), parent=self.TextureRegistry)
        self.ToggleLoadingIndicator()
        return tex

    # Dynamically import a file from a given Path
    def ImportFileFromPath(self, path):
        logging.info(f"[mmvEditor.ImportFileFromPath] Import file [{path}]")
        spec = importlib.util.spec_from_file_location(f"DynamicImport[{path}]", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def SetStatusText(self, Message):
        if self.DPG_STATUS_TEXT is not None:
            Dear.configure_item(self.DPG_STATUS_TEXT, default_value=Message)

    def _log_sender_data(self, sender, app_data, user_data=None):
        logging.info(f"[mmvEditor Event Log] Sender: [{sender}] | App Data: [{app_data}] | User Data: [{user_data}]")

    # Init the main Window but Async
    def InitMainWindowAsync(self):
        self.MainThread = threading.Thread(target=self.InitMainWindow, daemon=True).start()

    # Wrapper for calling Dear.add_theme_color or Dear.add_theme_style inputting a string
    def SetDearPyGuiThemeString(self, key, value):
        target = Dear.__dict__[key]
        if not isinstance(value, list): value = [value]
        category = 2 if "Node" in key else 0
        if "Col_" in key: Dear.add_theme_color(target, value, category=category)
        if "StyleVar_" in key: Dear.add_theme_style(target, *value, category=category)

    def AddAllFontRangeHints(self, Font):
        # Add all font ranges one would need, overkill? yes
        for FontRangeHint in [
            Dear.mvFontRangeHint_Japanese,
            # Dear.mvFontRangeHint_Korean,
            # Dear.mvFontRangeHint_Chinese_Full,
            # Dear.mvFontRangeHint_Chinese_Simplified_Common,
            Dear.mvFontRangeHint_Cyrillic,  # Russian
            # Dear.mvFontRangeHint_Thai,
            # Dear.mvFontRangeHint_Vietnamese,
        ]:
            Dear.add_font_range_hint(FontRangeHint, parent=Font)

    # # Loops, Layout

    # Create DearPyGui items
    def InitMainWindow(self):
        dpfx = "[mmvEditor.InitMainWindow]"

        # Add node files we have, but don't render it
        self.Scene.AddNodeFilesDataDirRecursive(render=False)
  
        # Load theme YAML, set values
        with Dear.theme(default_theme=True) as self.DPG_THEME:
            self.ThemeYaml = DotMap( yaml.load(Path(self.PackageInterface.DataDir/"Theme.yaml").read_text(), Loader = yaml.FullLoader) )
            for key, value in self.ThemeYaml.Global.items():
                logging.info(f"{dpfx} Customize Theme [{key}] => [{value}]")
                self.SetDearPyGuiThemeString(key, value)

        # Load font, add circles unicode
        with Dear.font_registry() as self.DPG_FONT_REGISTRY:
            logging.info(f"{dpfx} Loading Interface font")

            for Lang in Polyglot.ICanSpeak:
                if not Lang.Font in self.LoadedFonts.keys():

                    ThisFont = Dear.add_font(
                        self.PackageInterface.FontsDir/Lang.Font,
                        self.Context.DotMap.UI_FONT_SIZE,
                        default_font=Lang.Font == self.Context.DotMap.LANGUAGE.Font)
                    
                    Dear.add_font_chars([
                        0x2B24, # ⬤ Large Black Circle
                        0x25CF, # ●  Black Circle
                    ], parent=ThisFont)

                    self.AddAllFontRangeHints(ThisFont)
                    self.LoadedFonts[Lang.Font] = ThisFont

        # Handler
        with Dear.handler_registry() as self.DPG_HANDLER_REGISTRY: ...
            # Dear.add_mouse_drag_handler(0, callback=self._MouseWentDrag)

        # Creating main window
        with Dear.window(
            width=int(self.Context.DotMap.WINDOW_SIZE[0]),
            height=int(self.Context.DotMap.WINDOW_SIZE[1]),
            on_close=self.Exit, no_scrollbar=True
        ) as self.DPG_MAIN_WINDOW:
            Dear.set_primary_window(self.DPG_MAIN_WINDOW, True)
            # Dear.add_resize_handler(self.DPG_MAIN_WINDOW, callback=self.MainWindowResized)
            Dear.configure_item(self.DPG_MAIN_WINDOW, menubar=True)
            Dear.configure_item(self.DPG_MAIN_WINDOW, no_resize=True)
            Dear.configure_item(self.DPG_MAIN_WINDOW, no_resize=True)

            # # Render stuff
            self.MenuBarUI.Render()

            with Dear.child(border = False, height = -28):
                with Dear.tab_bar() as self.DPG_MAIN_TAB_BAR:
                    with Dear.tab(label=Speak("Node Editor")) as self.DPG_NODE_EDITOR_TAB:

                        with Dear.table(header_row=False, no_clip=True, precise_widths=True):
                            Dear.add_table_column(width_fixed=False)

                            with Dear.table(header_row=False, no_clip=True, precise_widths=True):
                                Dear.add_table_column()
                                
                                Dear.add_button(label="A")
                                Dear.add_same_line()
                                Dear.add_button(label="B")
                                Dear.add_same_line()
                                Dear.add_button(label="C")
                                Dear.add_same_line()
                                Dear.add_button(label="D")
                                Dear.add_same_line()
                                Dear.add_button(label="E")
                                Dear.add_same_line()
                                Dear.add_button(label="F")
                                Dear.add_same_line()

                                Dear.add_table_next_column()
                                with Dear.table(header_row=False, no_clip=True, precise_widths=True):
                                    Dear.add_table_column(width_fixed=True)
                                    Dear.add_table_column()
                                    Dear.add_table_column(width_fixed=True)
                                    
                                    self.AddNodeUI.Here()
                                    self.AddNodeUI.Render()

                                    Dear.add_table_next_column()
                                    with Dear.child(border = False, height = -14):
                                        with Dear.node_editor(
                                            callback=self.Scene.NodeAttributeLinked,
                                            delink_callback=self.Scene.NodeDelinked
                                        ) as self.DPG_NODE_EDITOR: ...

                                    Dear.add_table_next_column()
                                    Dear.add_text(Speak("Hello I'll be toolbar"))
                                    Dear.add_table_next_column()
                            # # Footer
                            Dear.add_table_next_column()
                            Dear.add_same_line()

                    with Dear.tab(label=Speak("Live Config")) as self.DPG_LIVE_CONFIG_TAB: ...
                    with Dear.tab(label=Speak("Render Video")) as self.DPG_EXPORT_TAB: ...
                    with Dear.tab(label=Speak("Performance")) as self.DPG_PERFORMANCE_TAB: ...
            
            Dear.add_separator()
            self.DPG_LOADING_INDICATOR_GLOBAL = Dear.add_loading_indicator(**self.ThemeYaml.LoadingIndicator.Idle)
            self.ToggleLoadingIndicator()
            Dear.add_same_line()
            Dear.add_text(f"MMV v{self.PackageInterface.VersionNumber}  ", color = (230,70,75))
            Dear.add_same_line()
            self.DPG_LANGUAGE_BUTTON = Dear.add_button(label=f"", callback=lambda d,s: self.MenuBarUI.LanguageSelectUI())
            self.UpdateLanguageButtonText()
            Dear.add_same_line()
            Dear.add_text(f" | ", color = (80,80,80))
            Dear.add_same_line()
            self.DPG_CURRENT_PRESET_TEXT = Dear.add_text(f"\"{self.Scene.PresetName}\"")
            Dear.add_same_line()
            Dear.add_text(f" | ", color = (80,80,80))
            Dear.add_same_line()
            self.DPG_STATUS_TEXT = Dear.add_text("", color=(140,140,140))
            self.SetStatusText(Speak("Finished Loading"))

        # # # Custom StreamHandler logging class for updating the DPG text to show latest
        # # notifications on the UI for the user
        # class UpdateUINotificationDPGTextHandler(logging.StreamHandler):
        #     def __init__(self, mmv_editor): self.mmv_editor = mmv_editor
        #     def write(self, message): Dear.configure_item(self.mmv_editor.DPG_STATUS_TEXT, default_value=f"{message}")
        #     def flush(self, *args, **kwargs): ...

        # # Add the handler
        # logging.getLogger().addHandler(logging.StreamHandler(
        #     stream=UpdateUINotificationDPGTextHandler(mmv_editor=self)))
    
        # Main Loop thread
        threading.Thread(target=self.MainLoop).start()

    def UpdateLanguageButtonText(self):
        Dear.configure_item(self.DPG_LANGUAGE_BUTTON, label=Speak("Language") + ": " + self.Context.DotMap.LANGUAGE.NativeName)

    # Toggle the loading indicator on the main screen to show we are doing something
    def ToggleLoadingIndicator(self, force=False):
        self.ToggleAttrSafe(self.__dict__, "_ToggleLoadingIndicator")
        if not hasattr(self, "DPG_LOADING_INDICATOR_GLOBAL"): return
        Dear.configure_item(self.DPG_LOADING_INDICATOR_GLOBAL,
            **[self.ThemeYaml.LoadingIndicator.Idle.toDict(), self.ThemeYaml.LoadingIndicator.Loading.toDict()][int(self._ToggleLoadingIndicator)])

    # Handler when window was resized
    def ViewportResized(self, _, Data, __ignore=0, *a,**b):
        self.Context.DotMap.WINDOW_SIZE = Data[0], Data[1]
        # Dear.configure_item(self.DPG_MAIN_WINDOW, max_size=self.Context.DotMap.WINDOW_SIZE)

    # def MainWindowResized(self, _, Data):
    #     Dear.configure_viewport(self.Viewport, width=Data[0], height=Data[1])

    def MainLoop(self):
        logging.info(f"[mmvEditor.MainLoop] Enter MainLoop, start MMV")
        self._Stop = False
        self.Viewport = Dear.create_viewport(
            title=Speak("ModularMusicVisualizer Editor"),
            caption=not self.Context.DotMap.BUILTIN_WINDOW_DECORATORS,
            resizable=True, border=False)
        # for F in [Dear.set_viewport_small_icon, Dear.set_viewport_large_icon]: F(self.DefaultResourcesIcon)
        Dear.set_viewport_resize_callback(self.ViewportResized)
        Dear.setup_dearpygui(viewport=self.Viewport)
        Dear.show_viewport(self.Viewport)
        with Dear.texture_registry() as self.TextureRegistry: ...
        if self.Context.DotMap.START_MAXIMIZED: Dear.maximize_viewport()
        try:
            for iteration in itertools.count(1):
                if (self._Stop) or (not Dear.is_dearpygui_running()): break
                self.Next(iteration)
                Dear.render_dearpygui_frame()
        except KeyboardInterrupt: pass
        self.__True_Exit()

    def Next(self, iteration):
        if iteration == 3:
            self.FirstTimeWarning()

    def Exit(self,*a,**b): self._Stop = True

    def SaveCurrentConfig(self): self.Context.Pack(self.USER_CONFIG_FILE)

    def __True_Exit(self):
        self.Exit()
        logging.info(f"[mmvEditor.AddNodeFile] Exiting [Modular Music Visualizer Editor] *Safely*")
        self.SaveCurrentConfig()
        Dear.cleanup_dearpygui()



    # First time opening MMV warning
    # def __FirstTimeWarningOK(self, _): self.Context.ForceSet("FIRST_TIME", False); Dear.delete_item(_)
    def FirstTimeWarning(self):
        if self.Context.DotMap.FIRST_TIME:
            self.Context.ForceSet("FIRST_TIME", False)
            self.MenuBarUI.LanguageSelectUI()

            # self.__FirstTimeWarningOK()
            # with self.CenteredWindow(self.Context, width=400, height=100) as _:
            #     Dear.add_text((
            #         Speak("Hello first time user!!") + "\n\n" +
            #         Speak("Modular Music Visualizer is Free Software,") + "\n" +
            #         Speak("distributed under the GPLv3 License.") + "\n\n"
            #     ))
            #     Dear.add_button(label=Speak("Close"), callback=lambda d,s: self.__FirstTimeWarningOK(_))