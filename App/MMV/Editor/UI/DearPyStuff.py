
"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

===============================================================================

Purpose: Create Main UI

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
import logging
from pathlib import Path

import dearpygui.logger as DearLogger
import dearpygui.dearpygui as Dear
import yaml
from dotmap import DotMap
from MMV.Common.BudgetVsync import BudgetVsyncClient
from MMV.Common.DearPyGuiUtils import *
from MMV.Common.Polyglot import Polyglot
from MMV.Common.Utils import *
from MMV.Editor.UI.Dialogs.About import AboutUI
from MMV.Editor.UI.Dialogs.ExternalsManager import ExternalsManagerDialog
from MMV.Editor.UI.Dialogs.LanguageSelect import LanguageSelectUI
from MMV.Editor.UI.Tabs.NodeEditor.AddNodeUI import AddNodeUI
from MMV.Editor.UI.Dialogs.PleaseRestart import PleaseRestartUI

Speak = Polyglot.Speak

class mmvDearPyStuff:
    def __init__(self, Editor):
        self.Editor = Editor
        self.PackageInterface = self.Editor.PackageInterface
        self.Scene = self.Editor.Scene
        self.Context = self.Editor.Context

        self.LoadedFonts = DotMap(_dynamic=False)
        self.AddNodeUI = AddNodeUI(self.Editor)

        self.DefaultFont = "DejaVuSans-Bold.ttf"
        self.DefaultResourcesLogoImage = self.PackageInterface.ImageDir/"mmvLogoWhite.png"
        # self.DefaultResourcesIcon = self.PackageInterface.ImageDir/"mmvLogoWhite.ico"

        with Dear.texture_registry() as self.TextureRegistry: ...

    # # Loops, Layout
    def GetThemeStuff(self):
        self.SpecificThemeConfig = self.ThemeYaml[self.Context.DotMap.GLOBAL_THEME]
        for Key, Value in self.SpecificThemeConfig.items():
            if Key.startswith("mmv"):
                self.ThemeYaml[Key] = Value

    def UpdateLanguageButtonText(self):
        Dear.configure_item(self.DPG_LANGUAGE_BUTTON, label=Speak("Language")+": "+self.Context.DotMap.LANGUAGE.NativeName)

    # Bottom left status text
    def SetStatusText(self, Message):
        if self.DPG_STATUS_TEXT is not None:
            Dear.configure_item(self.DPG_STATUS_TEXT, default_value=Message)

    # def MainWindowResized(self, _, Data):
    #     Dear.configure_viewport(self.Viewport, width=Data[0], height=Data[1])

    # Handler when window was resized
    def ViewportResized(self, _, Data, __ignore=0, *a,**b):
        self.Context.DotMap.WINDOW_SIZE = Data[0], Data[1]
        # Dear.configure_item(self.DPG_MAIN_WINDOW, max_size=self.Context.DotMap.WINDOW_SIZE)

    # Create DearPyGui items
    def InitMainWindow(self):
        dpfx = "[mmvDearPyStuff.InitMainWindow]"

        # # Logger

        self.DearPyGuiLogger = DearLogger.mvLogger()
        Dear.configure_item(self.DearPyGuiLogger.window_id, show=False)

        # # Custom StreamHandler logging class for redirecting logging messages
        # also to DearPyGui logger
        class UpdateUINotificationDPGTextHandler(logging.StreamHandler):
            def __init__(self, DearPyGuiLogger): self.DearPyGuiLogger = DearPyGuiLogger
            def write(self, message): self.DearPyGuiLogger.log(message)
            def flush(self, *args, **kwargs): ...

        # # Add the handler
        logging.getLogger().addHandler(logging.StreamHandler(
            stream=UpdateUINotificationDPGTextHandler(DearPyGuiLogger=self.DearPyGuiLogger)))

        # Add node files we have, but don't render it
        self.Scene.AddNodeFilesDataDirRecursive(render=False)

        # Load theme YAML, set values
        with Dear.theme(default_theme=True) as self.DPG_THEME:
            self.ThemeYaml = DotMap( yaml.load(Path(self.PackageInterface.DataDir/"Theme.yaml").read_text(), Loader = yaml.FullLoader) )
            self.Editor.ThemeYaml = self.ThemeYaml
            self.GetThemeStuff()
            
            ApplyThemeStuff = {**self.ThemeYaml.Global, **self.SpecificThemeConfig}

            for Key, Value in ApplyThemeStuff.items():
                # DearPyGui uses mv as a prefix
                if Key.startswith("mv"):
                    logging.info(f"{dpfx} Customize Theme [{Key}] => [{Value}]")
                    if isinstance(Value, list):
                        if len(Value) == 1: Value = Value*3
                    DearSetThemeString(Key=Key, Value=Value, Parent=self.DPG_THEME)

        # Change trace text color
        Dear.add_theme_color(Dear.mvThemeCol_Text, self.ThemeYaml.mmvSectionText, parent=self.DearPyGuiLogger.trace_theme)

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
                        0x25B6, # ▶ Play
                        0x23F8, # ⏸ Pause
                        0x23F9, # ⏹ Stop
                    ], parent=ThisFont)

                    DearAddFontRangeHints(ThisFont)
                    self.LoadedFonts[Lang.Font] = ThisFont

        # Handler
        with Dear.handler_registry() as self.DPG_HANDLER_REGISTRY: ...
            # Dear.add_mouse_drag_handler(0, callback=self._MouseWentDrag)

        # Creating main window
        with Dear.window(
            width=int(self.Context.DotMap.WINDOW_SIZE[0]),
            height=int(self.Context.DotMap.WINDOW_SIZE[1]),
            on_close=self.Editor.Exit, no_scrollbar=True
        ) as self.DPG_MAIN_WINDOW:
            Dear.set_primary_window(self.DPG_MAIN_WINDOW, True)
            # Dear.add_resize_handler(self.DPG_MAIN_WINDOW, callback=self.MainWindowResized)
            Dear.configure_item(self.DPG_MAIN_WINDOW, menubar=True)
            Dear.configure_item(self.DPG_MAIN_WINDOW, no_resize=True)
            Dear.configure_item(self.DPG_MAIN_WINDOW, no_resize=True)

            with Dear.menu_bar() as MenuBar:
                if self.Editor.Context.DotMap.BUILTIN_WINDOW_DECORATORS:
                    Dear.add_clicked_handler(Dear.add_text("⬤", color=(255,0,0)), callback=lambda s,d:self.Editor.Exit())
                    Dear.add_clicked_handler(Dear.add_text("⬤", color=(255,255,0)), callback=lambda s,d:Dear.minimize_viewport())
                    Dear.add_clicked_handler(Dear.add_text("⬤", color=(0,255,0)), callback=lambda s,d:Dear.maximize_viewport())
                with Dear.menu(label=(Speak("File"))):
                    Dear.add_menu_item(label=Speak("New"))
                    Dear.add_menu_item(label=Speak("Open"))
                    Dear.add_menu_item(label=Speak("Open Recent"))
                    Dear.add_menu_item(label=Speak("Save"))
                    Dear.add_menu_item(label=Speak("Save As"))
                    Dear.add_separator()
                    Dear.add_menu_item(label=Speak("Exit"), callback=lambda s,d: self.Editor.Exit())
                with Dear.menu(label=Speak("Edit")):
                    Dear.add_menu_item(label=Speak("Undo"), callback=lambda s,d: self.Editor.EventBus.Undo())
                    Dear.add_menu_item(label=Speak("Redo"), callback=lambda s,d: self.Editor.EventBus.Redo())
                with Dear.menu(label=Speak("View")):
                    Dear.add_menu_item(label="Something")
                with Dear.menu(label=Speak("Preferences")):
                    Dear.add_slider_float(label=Speak("User Interface FX Volume"), default_value=40, min_value=0,max_value=100, callback=lambda s,d,a,b,c,f:print(d,s,a,b,c,f))
                    Dear.add_separator()
                    Dear.add_text("Stuff that Needs Restart", color=(self.ThemeYaml.mmvSectionText))
                    Dear.add_checkbox(label=Speak("Builtin Window Decorators"), callback=lambda d,s: self.ToggleBuiltinWindowDecorator(), default_value=self.Editor.Context.DotMap.BUILTIN_WINDOW_DECORATORS)
                    Dear.add_checkbox(label=Speak("Start Maximized"), callback=lambda d,s: self.ToggleStartMaximized(), default_value=self.Editor.Context.DotMap.START_MAXIMIZED)

                    # Change Theme
                    def ChangeTheme(Editor, Value):
                        self.Editor.Context.ForceSet("GLOBAL_THEME", Value)
                        PleaseRestartUI(Editor, "Change Theme")
                    Dear.add_combo(label=Speak("Interface Global Theme"), items=["Dark","Light"], width=100, default_value=self.Editor.Context.DotMap.GLOBAL_THEME,
                        callback=lambda id,Value: ChangeTheme(self.Editor, Value))

                Dear.add_menu_item(label=Speak("Downloads"), callback=lambda s,d:ExternalsManagerDialog(self.Editor))

                with Dear.menu(label=Speak("Help")):
                    Dear.add_menu_item(label=Speak("Telegram Channel"), callback=lambda s,d:webbrowser.open("https://t.me/modular_music_visualizer"))
                    Dear.add_menu_item(label=Speak("GitHub Issues"),    callback=lambda s,d:webbrowser.open("https://github.com/Tremeschin/modular-music-visualizer/issues"))

                if self.Editor.PackageInterface.ConfigYAML.Developer:
                    with Dear.menu(label=Speak("Developer")):
                        Dear.add_menu_item(label=Speak("Toggle Loading Indicator"), callback=lambda s,d:self.Editor.DearPyStuff.ToggleLoadingIndicator())
                        Dear.add_menu_item(label=Speak("DearPyGui Style Editor"),   callback=lambda s,d:Dear.show_tool(Dear.mvTool_Style))
                        Dear.add_menu_item(label=Speak("DearPyGui Metrics"),        callback=lambda:Dear.show_tool(Dear.mvTool_Metrics))
                        Dear.add_menu_item(label=Speak("DearPyGui Documentation"),  callback=lambda:Dear.show_tool(Dear.mvTool_Doc))
                        Dear.add_menu_item(label=Speak("DearPyGui Debug"),          callback=lambda:Dear.show_tool(Dear.mvTool_Debug))
                        Dear.add_menu_item(label=Speak("DearPyGui Font Manager"),   callback=lambda:Dear.show_tool(Dear.mvTool_Font))
                        Dear.add_menu_item(label=Speak("DearPyGui Item Registry"),  callback=lambda:Dear.show_tool(Dear.mvTool_ItemRegistry))

                Dear.add_menu_item(label=Speak("About"), callback=lambda s,d:AboutUI(self.Editor))

            with Dear.child(border = False, height = -28):
                with Dear.tab_bar() as self.DPG_MAIN_TAB_BAR:
                    with Dear.tab(label=Speak("Node Editor")) as self.DPG_NODE_EDITOR_TAB:

                        with Dear.table(header_row=False, no_clip=True, precise_widths=True):
                            Dear.add_table_column(width_fixed=False)

                            with Dear.table(header_row=False, no_clip=True, precise_widths=True):
                                Dear.add_table_column()
                                
                                # Dear.add_button(label="▶", callback=lambda d,s: self.SombreroMain.window.CreateWindow())
                                Dear.add_button(label="▶")
                                Dear.add_same_line()
                                Dear.add_button(label="⏸")
                                Dear.add_same_line()
                                Dear.add_button(label="⏹")

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
                    with Dear.tab(label=Speak("Sombrero Demo")) as self.DPG_SOMBRERO_DEMO_TAB:
                        Dear.add_button(label="Default Scene", callback=lambda d,s:self.Editor.Scene.LoadDemoScenePreNodes("Default"))
                        Dear.add_button(label="Alpha Composite Scene", callback=lambda d,s:self.Editor.Scene.LoadDemoScenePreNodes("AlphaComposite"))
                        Dear.add_button(label="Blueprint Scene", callback=lambda d,s:self.Editor.Scene.LoadDemoScenePreNodes("Blueprint"))
            
            Dear.add_separator()
            self.DPG_LOADING_INDICATOR_GLOBAL = Dear.add_loading_indicator(**self.ThemeYaml.LoadingIndicator.Idle)
            self.Editor.DearPyStuff.ToggleLoadingIndicator()
            
            Dear.add_same_line()
            Dear.add_text(f"MMV v{self.PackageInterface.VersionNumber}  ", color = (230,70,75))
            with Dear.tooltip(parent=Dear.last_item()): Dear.add_text(Speak("Version"))
            
            Dear.add_same_line()
            self.DPG_LANGUAGE_BUTTON = Dear.add_button(label=f"", callback=lambda d,s: LanguageSelectUI(self.Editor))
            with Dear.tooltip(parent=Dear.last_item()): Dear.add_text(Speak("Change Language"))
            self.UpdateLanguageButtonText()
            
            Dear.add_same_line()
            Dear.add_text(f" | ", color = (80,80,80))
            
            Dear.add_same_line()
            self.DPG_CURRENT_PRESET_TEXT = Dear.add_text(f"\"{self.Scene.PresetName}\"")
            
            Dear.add_same_line()
            Dear.add_text(f" | ", color = (80,80,80))

            Dear.add_same_line()
            Dear.add_button(label="●", callback=lambda d,sy:
                Dear.configure_item(
                    self.DearPyGuiLogger.window_id,
                    show=not Dear.get_item_configuration(self.DearPyGuiLogger.window_id)["show"]))
            with Dear.tooltip(parent=Dear.last_item()): Dear.add_text(Speak("Open Logger"))

            Dear.add_same_line()
            self.DPG_STATUS_TEXT = Dear.add_text("", color=(140,140,140))
            self.SetStatusText(Speak("Finished Loading"))

    def ToggleBuiltinWindowDecorator(self):
        self.Editor.Context.ToggleBool("BUILTIN_WINDOW_DECORATORS")
        # Dear.configure_viewport(self.Editor.Viewport, caption=self.Editor.Context.DotMap.BUILTIN_WINDOW_DECORATORS)
        # Dear.setup_dearpygui(viewport=self.Editor.Viewport)
        # Dear.show_viewport(self.Editor.Viewport)

    def ToggleStartMaximized(self):
        self.Editor.Context.ToggleBool("START_MAXIMIZED")

    # Toggle the loading indicator on the main screen to show we are doing something
    def ToggleLoadingIndicator(self, force=False):
        Utils.ToggleAttrSafe(self.__dict__, "_ToggleLoadingIndicator")
        if not hasattr(self, "DPG_LOADING_INDICATOR_GLOBAL"): return
        Dear.configure_item(self.DPG_LOADING_INDICATOR_GLOBAL,
            **[self.ThemeYaml.LoadingIndicator.Idle.toDict(), self.ThemeYaml.LoadingIndicator.Loading.toDict()][int(self._ToggleLoadingIndicator)])

    def SetupViewport(self):
        self.Viewport = Dear.create_viewport(
            title=Speak("ModularMusicVisualizer Editor"),
            caption=not self.Context.DotMap.BUILTIN_WINDOW_DECORATORS,
            resizable=True, border=False, vsync=False)
        # for F in [Dear.set_viewport_small_icon, Dear.set_viewport_large_icon]: F(self.DefaultResourcesIcon)
        Dear.set_viewport_resize_callback(self.ViewportResized)
        Dear.setup_dearpygui(viewport=self.Viewport)
        Dear.show_viewport(self.Viewport)
        if self.Context.DotMap.START_MAXIMIZED: Dear.maximize_viewport()

        # Action to render DearPyGui
        self.Editor.BudgetVsyncDearRender = BudgetVsyncClient(60, Dear.render_dearpygui_frame)
        self.Editor.BudgetVsyncManager.AddVsyncTarget(self.Editor.BudgetVsyncDearRender)
        
