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

import dearpygui.dearpygui as dear


class mmvEditorMenuBarUI:
    def __init__(self, Editor):
        self.Editor = Editor
        self.isLoading = False
    
    def SetLoadingIndicator(self, state: bool):
        dear.configure_item

    def Render(self):
        with dear.menu_bar() as MenuBar:
            if self.Editor.Context.BUILTIN_WINDOW_DECORATORS:
                dear.add_clicked_handler(dear.add_text("⬤", color=(255,0,0)), callback=lambda s,d:self.Editor.Exit())
                dear.add_clicked_handler(dear.add_text("⬤", color=(255,255,0)), callback=lambda s,d:dear.minimize_viewport())
                dear.add_clicked_handler(dear.add_text("⬤", color=(0,255,0)), callback=lambda s,d:dear.maximize_viewport())
            with dear.menu(label="File"):
                dear.add_menu_item(label="New")
                dear.add_menu_item(label="Open")
                dear.add_menu_item(label="Open Recent")
                dear.add_menu_item(label="Save")
                dear.add_menu_item(label="Save As")
                dear.add_separator()
                dear.add_menu_item(label="Exit", callback=lambda s,d: self.Editor.Exit())
            with dear.menu(label="Edit"):
                dear.add_menu_item(label="Undo", callback=lambda s,d: self.Editor.EventBus.Undo())
                dear.add_menu_item(label="Redo", callback=lambda s,d: self.Editor.EventBus.Redo())
            with dear.menu(label="View"):
                dear.add_menu_item(label="Something")
            with dear.menu(label="Preferences"):
                dear.add_slider_float(label="User Interface FX Volume", default_value=40, min_value=0,max_value=100, callback=lambda s,d,a,b,c,f:print(d,s,a,b,c,f))
                dear.add_checkbox(label="Builtin Window Decorators [Needs Restart]", callback=lambda d,s: self.ToggleBuiltinWindowDecorator(), default_value=self.Editor.Context.BUILTIN_WINDOW_DECORATORS)
                dear.add_checkbox(label="Start Maximized", callback=lambda d,s: self.ToggleStartMaximized(), default_value=self.Editor.Context.START_MAXIMIZED)
                dear.add_separator()
                dear.add_menu_item(label="Advanced")
            
            dear.add_menu_item(label="Downloads", callback=lambda s,d:self.ExternalsManagerUI())

            with dear.menu(label="Help"):
                dear.add_menu_item(label="Telegram Channel", callback=lambda s,d:webbrowser.open("https://t.me/modular_music_visualizer"))
                dear.add_menu_item(label="GitHub Issues", callback=lambda s,d:webbrowser.open("https://github.com/Tremeschin/modular-music-visualizer/issues"))

            with dear.menu(label="Developer"):
                dear.add_menu_item(label="Toggle Loading Indicator", callback=lambda s,d:self.Editor.ToggleLoadingIndicator())
                dear.add_menu_item(label="DearPyGui Style Editor", callback=lambda s,d:dear.show_tool(dear.mvTool_Style))
                dear.add_menu_item(label="DearPyGui Metrics", callback=lambda:dear.show_tool(dear.mvTool_Metrics))
                dear.add_menu_item(label="DearPyGui Documentation", callback=lambda:dear.show_tool(dear.mvTool_Doc))
                dear.add_menu_item(label="DearPyGui Debug", callback=lambda:dear.show_tool(dear.mvTool_Debug))
                dear.add_menu_item(label="DearPyGui Style Editor", callback=lambda:dear.show_tool(dear.mvTool_Style))
                dear.add_menu_item(label="DearPyGui Font Manager", callback=lambda:dear.show_tool(dear.mvTool_Font))
                dear.add_menu_item(label="DearPyGui Item Registry", callback=lambda:dear.show_tool(dear.mvTool_ItemRegistry))

            dear.add_menu_item(label="About", callback=lambda s,d:self.About())
            # dear.add_text("Modular Music Visualizer Editor", color=(150,150,150))
    
    def ToggleBuiltinWindowDecorator(self):
        self.Editor.ContextSafeSetVar.ToggleBool("BUILTIN_WINDOW_DECORATORS")
        # dear.configure_viewport(self.Editor.Viewport, caption=self.Editor.Context.BUILTIN_WINDOW_DECORATORS)
        # dear.setup_dearpygui(viewport=self.Editor.Viewport)
        # dear.show_viewport(self.Editor.Viewport)

    def ToggleStartMaximized(self):
        self.Editor.ContextSafeSetVar.ToggleBool("START_MAXIMIZED")

    def About(self):
        logging.info(f"[mmvEditorMenuBarUI.About] Show About window")
        with self.Editor.CenteredWindow(self.Editor.Context, width=200, height=200) as AboutWindow:
            self.Editor.AddImageWidget(path=self.Editor.LogoImage, size=190)
            dear.add_text(f"Modular Music Visualizer", color = (0,255,0))
            dear.add_text(f"Version {self.Editor.PackageInterface.Version}", color=(150,150,150))
            dear.add_separator()
            dear.add_button(label="Website", callback=lambda s,d:webbrowser.open("http://mmvproject.gitlab.io/website"))
            dear.add_button(label="GitHub Page", callback=lambda s,d:webbrowser.open("https://github.com/Tremeschin/modular-music-visualizer"))
            dear.add_separator()
            dear.add_button(label="About DearPyGui", callback=lambda:dear.show_tool(dear.mvTool_About))
 
    # # Ui to manage externals

    def ExternalsManagerUI(self):
        logging.info(f"[mmvEditorMenuBarUI.ExternalsManagerUI] Show About window")

        def DownloadSomething(TargetExternal, _ForceNotFound=False):

            with self.Editor.CenteredWindow(self.Editor.Context, width=600, height=200, no_close=True) as DownloadWindow:
                dear.add_text(f"Downloading [{TargetExternal}]")
                dear.add_same_line();
                dear.add_loading_indicator(**self.Editor.LoadingIndicatorConfigLoadingDict)
                ProgressBar = dear.add_progress_bar(width=600)
                CurrentInfo = dear.add_text(f"Requesting Download Info..")

            def KeepUpdatingProgressBar(Status):
                dear.configure_item(ProgressBar,
                    label=Status.Name,
                    default_value=Status.Completed
                )
                dear.configure_item(CurrentInfo, default_value=Status.Info)

            self.Editor.PackageInterface.Externals.DownloadInstallExternal(
                TargetExternal=TargetExternal,
                Callback=KeepUpdatingProgressBar,
                _ForceNotFound=_ForceNotFound,
            )

            dear.delete_item(DownloadWindow)
            self.Editor.PackageInterface.FindExternals()
            self.ExternalsManagerUI()

        with self.Editor.CenteredWindow(self.Editor.Context, width=200, height=200) as ExternalsWindow:
            dear.add_text(f"Externals Manager", color = (0,255,0))

            dear.add_text("FFmpeg: ")
            dear.add_same_line()
            HaveFFmpeg = not self.Editor.PackageInterface.FFmpegBinary is None
            
            if HaveFFmpeg:
                dear.add_text("Yes", color=(0,255,0))
                Action = "Reinstall"
            else:
                dear.add_text("No, required for exporting videos", color=(255,0,0))
                Action = "Download"

            dear.add_same_line()
            dear.add_button(label=Action, callback=
                lambda s,d: DownloadSomething(
                    self.Editor.PackageInterface.Externals.AvailableExternals.FFmpeg,
                    _ForceNotFound=HaveFFmpeg
                )
            )


