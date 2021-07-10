"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Menu bar refactor for main editor window

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
import copy
import logging
import webbrowser

import dearpygui.dearpygui as Dear
from MMV.Common.Polyglot import Polyglot

Speak = Polyglot.Speak

class mmvEditorMenuBarUI:
    def __init__(self, Editor):
        self.Editor = Editor
        self.isLoading = False
    
    def SetLoadingIndicator(self, state: bool):
        Dear.configure_item

    def Render(self):
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
                Dear.add_text("Stuff that Needs Restart", color=(0,255,0))
                Dear.add_checkbox(label=Speak("Builtin Window Decorators"), callback=lambda d,s: self.ToggleBuiltinWindowDecorator(), default_value=self.Editor.Context.DotMap.BUILTIN_WINDOW_DECORATORS)
                Dear.add_checkbox(label=Speak("Start Maximized"), callback=lambda d,s: self.ToggleStartMaximized(), default_value=self.Editor.Context.DotMap.START_MAXIMIZED)
                Dear.add_combo(label=Speak("Interface Global Theme"), items=["Dark","Light"], width=100, default_value=self.Editor.Context.DotMap.GLOBAL_THEME, callback=lambda id,value:self.Editor.Context.ForceSet("GLOBAL_THEME", value))

            Dear.add_menu_item(label=Speak("Downloads"), callback=lambda s,d:self.ExternalsManagerUI())

            with Dear.menu(label=Speak("Help")):
                Dear.add_menu_item(label=Speak("Telegram Channel"), callback=lambda s,d:webbrowser.open("https://t.me/modular_music_visualizer"))
                Dear.add_menu_item(label=Speak("GitHub Issues"),    callback=lambda s,d:webbrowser.open("https://github.com/Tremeschin/modular-music-visualizer/issues"))

            with Dear.menu(label=Speak("Developer")):
                Dear.add_menu_item(label=Speak("Toggle Loading Indicator"), callback=lambda s,d:self.Editor.ToggleLoadingIndicator())
                Dear.add_menu_item(label=Speak("DearPyGui Style Editor"),   callback=lambda s,d:Dear.show_tool(Dear.mvTool_Style))
                Dear.add_menu_item(label=Speak("DearPyGui Metrics"),        callback=lambda:Dear.show_tool(Dear.mvTool_Metrics))
                Dear.add_menu_item(label=Speak("DearPyGui Documentation"),  callback=lambda:Dear.show_tool(Dear.mvTool_Doc))
                Dear.add_menu_item(label=Speak("DearPyGui Debug"),          callback=lambda:Dear.show_tool(Dear.mvTool_Debug))
                Dear.add_menu_item(label=Speak("DearPyGui Font Manager"),   callback=lambda:Dear.show_tool(Dear.mvTool_Font))
                Dear.add_menu_item(label=Speak("DearPyGui Item Registry"),  callback=lambda:Dear.show_tool(Dear.mvTool_ItemRegistry))

            Dear.add_menu_item(label=Speak("About"), callback=lambda s,d:self.About())
            # Dear.add_text("Modular Music Visualizer Editor", color=(150,150,150))
    
    def ToggleBuiltinWindowDecorator(self):
        self.Editor.Context.ToggleBool("BUILTIN_WINDOW_DECORATORS")
        # Dear.configure_viewport(self.Editor.Viewport, caption=self.Editor.Context.DotMap.BUILTIN_WINDOW_DECORATORS)
        # Dear.setup_dearpygui(viewport=self.Editor.Viewport)
        # Dear.show_viewport(self.Editor.Viewport)

    def ToggleStartMaximized(self):
        self.Editor.Context.ToggleBool("START_MAXIMIZED")

    def About(self):
        logging.info(f"[mmvEditorMenuBarUI.About] Show About window")
        with self.Editor.CenteredWindow(self.Editor.Context, width=200, height=200) as AboutWindow:
            Dear.add_image( self.Editor.AddDynamicTexture(path=self.Editor.DefaultResourcesLogoImage, size=190) )
            Dear.add_text(f"{Speak('Modular Music Visualizer')}", color = (0,255,0))
            Dear.add_text(f"{Speak('Version')} {self.Editor.PackageInterface.Version}", color=(150,150,150))
            Dear.add_separator()
            Dear.add_button(label=Speak("Website"), callback=lambda s,d:webbrowser.open("http://mmvproject.gitlab.io/website"))
            Dear.add_button(label=Speak("GitHub Page"), callback=lambda s,d:webbrowser.open("https://github.com/Tremeschin/modular-music-visualizer"))
            Dear.add_separator()
            Dear.add_button(label=Speak("About DearPyGui"), callback=lambda:Dear.show_tool(Dear.mvTool_About))
 
    def LanguageSelectUI(self):
        dpfx = "[mmvEditorMenuBarUI.LanguageSelectUI]"
        logging.info(f"{dpfx} Show Language Select")

        def ConfigureLanguage(UserData, LanguageSelectWindow):
            Dear.delete_item(LanguageSelectWindow)
            if UserData.EnName == self.Editor.Context.DotMap.LANGUAGE.EnName:
                logging.info(f"{dpfx} Already using language [{UserData}]")
                return
            logging.info(f"{dpfx} Configuring language [{UserData}]")
            self.Editor.Context.ForceSet("LANGUAGE", UserData)
            Polyglot.Speak.Language(UserData)
            self.Editor.UpdateLanguageButtonText()
            self.Editor.Context.ForceSet("UI_FONT", UserData.Font)

            with self.Editor.CenteredWindow(self.Editor.Context, width=500, height=200, min_size=[500,0]) as RestartWindow:
                A=Dear.add_text(Speak("We need to restart for language settings to take effect, proceed?"))
                B=Dear.add_button(label=Speak("Ok (Close)"), callback=self.Editor.Exit)
                C=Dear.add_button(label=Speak("No (Continue)"), callback=lambda d,s,UserData: Dear.delete_item(RestartWindow))
                for Item in [A,B,C]:
                    Dear.set_item_font(Item, self.Editor.LoadedFonts[UserData.Font])


        with self.Editor.CenteredWindow(self.Editor.Context, width=300, height=200, min_size=[300,0], max_size=[10000,400]) as LanguageSelectWindow:
            Dear.add_text(Speak("Select Language [Needs Restart]"))
            Dear.add_separator()
            for Key, Value in Polyglot.Languages.__dict__.items():
                if not "__" in Key:
                    ThisLanguage = copy.deepcopy( Polyglot.Languages.__dict__[Key] )

                    # Add Flag button and text on the right
                    Flag = self.Editor.AddDynamicTexture(self.Editor.PackageInterface.IconDir/"Flags"/f"{ThisLanguage.CountryFlag}.png", size=55)

                    # Different Background to show that we are selected
                    if ThisLanguage.EnName == self.Editor.Context.DotMap.LANGUAGE.EnName:
                        ImageButtonExtra = {}
                    else:
                        ImageButtonExtra = dict(tint_color=[220]*3)
                    Dear.add_image_button(
                        texture_id=Flag,
                        user_data=ThisLanguage,
                        **ImageButtonExtra,
                        callback=lambda d,s,UserData: ConfigureLanguage(UserData, LanguageSelectWindow))
                    Dear.add_same_line()
                    with Dear.group():
                        NativeLangName = Dear.add_text(("● "*(ImageButtonExtra=={})) + ThisLanguage.NativeName, color=(0,255,0))

                        # Percentage of completion of the language
                        Total = 0
                        Have = 0
                        for Key, Values in Polyglot.Speak.Data.items():
                            if (ThisLanguage.LanguageCode in Values) or (ThisLanguage.LanguageCode == "en-us"):
                                Have += 1
                            Total += 1
                        Percentage = Have / Total
                        Dear.add_text(f"[{Percentage*100:.2f} %]", color=(120,120,120))
                    Dear.set_item_font(NativeLangName, self.Editor.LoadedFonts[ThisLanguage.Font])
                    Dear.add_separator()

    # # Ui to manage externals

    def ExternalsManagerUI(self):
        logging.info(f"[mmvEditorMenuBarUI.ExternalsManagerUI] Show Externals window")

        def DownloadSomething(TargetExternal, _ForceNotFound=False):
            self.Editor.ToggleLoadingIndicator()

            with self.Editor.CenteredWindow(self.Editor.Context, width=600, height=200, no_close=True) as DownloadWindow:
                Dear.add_text(Speak("Downloading") + f" [{TargetExternal}]")
                Dear.add_same_line();
                Dear.add_loading_indicator(**self.Editor.ThemeYaml.LoadingIndicator.Loading.toDict())
                ProgressBar = Dear.add_progress_bar(width=600)
                CurrentInfo = Dear.add_text(Speak("Requesting Download Info") + "..")

            def KeepUpdatingProgressBar(Status):
                Dear.configure_item(ProgressBar,
                    label=Status.Name,
                    default_value=Status.Completed
                )
                Dear.configure_item(CurrentInfo, default_value=Status.Info)

            self.Editor.PackageInterface.Externals.DownloadInstallExternal(
                TargetExternal=TargetExternal,
                Callback=KeepUpdatingProgressBar,
                _ForceNotFound=_ForceNotFound,
            )

            Dear.delete_item(DownloadWindow)
            self.Editor.PackageInterface.FindExternals()
            self.ExternalsManagerUI()
            self.Editor.ToggleLoadingIndicator()

        with self.Editor.CenteredWindow(self.Editor.Context, width=200, height=200) as ExternalsWindow:
            Dear.add_text(Speak("Externals Manager"), color = (0,255,0))

            Dear.add_text("FFmpeg: ")
            Dear.add_same_line()
            HaveFFmpeg = not self.Editor.PackageInterface.FFmpegBinary is None
            
            if HaveFFmpeg:
                Dear.add_text(Speak("Yes"), color=(0,255,0))
                Action = Speak("Reinstall")
            else:
                Dear.add_text("No, required for rendering videos", color=(255,0,0))
                Action = Speak("Download")

            Dear.add_same_line()
            Dear.add_button(label=Action, callback=
                lambda s,d: DownloadSomething(
                    self.Editor.PackageInterface.Externals.AvailableExternals.FFmpeg,
                    _ForceNotFound=HaveFFmpeg
                )
            )


