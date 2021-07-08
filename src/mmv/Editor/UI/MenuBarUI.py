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
import logging
import webbrowser

import dearpygui.dearpygui as Dear


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
            with Dear.menu(label="File"):
                Dear.add_menu_item(label="New")
                Dear.add_menu_item(label="Open")
                Dear.add_menu_item(label="Open Recent")
                Dear.add_menu_item(label="Save")
                Dear.add_menu_item(label="Save As")
                Dear.add_separator()
                Dear.add_menu_item(label="Exit", callback=lambda s,d: self.Editor.Exit())
            with Dear.menu(label="Edit"):
                Dear.add_menu_item(label="Undo", callback=lambda s,d: self.Editor.EventBus.Undo())
                Dear.add_menu_item(label="Redo", callback=lambda s,d: self.Editor.EventBus.Redo())
            with Dear.menu(label="View"):
                Dear.add_menu_item(label="Something")
            with Dear.menu(label="Preferences"):
                Dear.add_slider_float(label="User Interface FX Volume", default_value=40, min_value=0,max_value=100, callback=lambda s,d,a,b,c,f:print(d,s,a,b,c,f))
                Dear.add_checkbox(label="Builtin Window Decorators [Needs Restart]", callback=lambda d,s: self.ToggleBuiltinWindowDecorator(), default_value=self.Editor.Context.DotMap.BUILTIN_WINDOW_DECORATORS)
                Dear.add_checkbox(label="Start Maximized", callback=lambda d,s: self.ToggleStartMaximized(), default_value=self.Editor.Context.DotMap.START_MAXIMIZED)
                Dear.add_separator()
                Dear.add_menu_item(label="Advanced")
            
            Dear.add_menu_item(label="Downloads", callback=lambda s,d:self.ExternalsManagerUI())

            with Dear.menu(label="Help"):
                Dear.add_menu_item(label="Telegram Channel", callback=lambda s,d:webbrowser.open("https://t.me/modular_music_visualizer"))
                Dear.add_menu_item(label="GitHub Issues", callback=lambda s,d:webbrowser.open("https://github.com/Tremeschin/modular-music-visualizer/issues"))

            with Dear.menu(label="Developer"):
                Dear.add_menu_item(label="Toggle Loading Indicator", callback=lambda s,d:self.Editor.ToggleLoadingIndicator())
                Dear.add_menu_item(label="DearPyGui Style Editor", callback=lambda s,d:Dear.show_tool(Dear.mvTool_Style))
                Dear.add_menu_item(label="DearPyGui Metrics", callback=lambda:Dear.show_tool(Dear.mvTool_Metrics))
                Dear.add_menu_item(label="DearPyGui Documentation", callback=lambda:Dear.show_tool(Dear.mvTool_Doc))
                Dear.add_menu_item(label="DearPyGui Debug", callback=lambda:Dear.show_tool(Dear.mvTool_Debug))
                Dear.add_menu_item(label="DearPyGui Style Editor", callback=lambda:Dear.show_tool(Dear.mvTool_Style))
                Dear.add_menu_item(label="DearPyGui Font Manager", callback=lambda:Dear.show_tool(Dear.mvTool_Font))
                Dear.add_menu_item(label="DearPyGui Item Registry", callback=lambda:Dear.show_tool(Dear.mvTool_ItemRegistry))

            Dear.add_menu_item(label="About", callback=lambda s,d:self.About())
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
            self.Editor.AddImageWidget(path=self.Editor.DefaultResourcesLogoImage, size=190)
            Dear.add_text(f"Modular Music Visualizer", color = (0,255,0))
            Dear.add_text(f"Version {self.Editor.PackageInterface.Version}", color=(150,150,150))
            Dear.add_separator()
            Dear.add_button(label="Website", callback=lambda s,d:webbrowser.open("http://mmvproject.gitlab.io/website"))
            Dear.add_button(label="GitHub Page", callback=lambda s,d:webbrowser.open("https://github.com/Tremeschin/modular-music-visualizer"))
            Dear.add_separator()
            Dear.add_button(label="About DearPyGui", callback=lambda:Dear.show_tool(Dear.mvTool_About))
 
    # # Ui to manage externals

    def ExternalsManagerUI(self):
        logging.info(f"[mmvEditorMenuBarUI.ExternalsManagerUI] Show About window")

        def DownloadSomething(TargetExternal, _ForceNotFound=False):
            self.Editor.ToggleLoadingIndicator()

            with self.Editor.CenteredWindow(self.Editor.Context, width=600, height=200, no_close=True) as DownloadWindow:
                Dear.add_text(f"Downloading [{TargetExternal}]")
                Dear.add_same_line();
                Dear.add_loading_indicator(**self.Editor.LoadingIndicatorConfigLoadingDict)
                ProgressBar = Dear.add_progress_bar(width=600)
                CurrentInfo = Dear.add_text(f"Requesting Download Info..")

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
            Dear.add_text(f"Externals Manager", color = (0,255,0))

            Dear.add_text("FFmpeg: ")
            Dear.add_same_line()
            HaveFFmpeg = not self.Editor.PackageInterface.FFmpegBinary is None
            
            if HaveFFmpeg:
                Dear.add_text("Yes", color=(0,255,0))
                Action = "Reinstall"
            else:
                Dear.add_text("No, required for exporting videos", color=(255,0,0))
                Action = "Download"

            Dear.add_same_line()
            Dear.add_button(label=Action, callback=
                lambda s,d: DownloadSomething(
                    self.Editor.PackageInterface.Externals.AvailableExternals.FFmpeg,
                    _ForceNotFound=HaveFFmpeg
                )
            )


