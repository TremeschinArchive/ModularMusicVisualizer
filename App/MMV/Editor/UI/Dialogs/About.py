"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

===============================================================================

Purpose: 

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

import dearpygui.dearpygui as Dear
from MMV.Common.DearPyGuiUtils import *
from MMV.Common.Polyglot import Polyglot

Speak = Polyglot.Speak

def AboutUI(Editor):
    logging.info(f"[mmvEditorMenuBarUI.About] Show About window")
    with DearCenteredWindow(Editor.Context, width=200, height=200) as AboutWindow:
        Dear.add_image( DearAddDynamicTexture(FilePath=Editor.DearPyStuff.DefaultResourcesLogoImage, TextureRegistry=Editor.DearPyStuff.TextureRegistry, size=190) )
        Dear.add_text(f"{Speak('Modular Music Visualizer')}", color = (Editor.ThemeYaml.mmvSectionText))
        Dear.add_text(f"{Speak('Version')} {Editor.PackageInterface.Version}", color=(150,150,150))
        Dear.add_separator()
        Dear.add_button(label=Speak("Website"), callback=lambda s,d:webbrowser.open("http://mmvproject.gitlab.io/website"))
        Dear.add_button(label=Speak("GitHub Page"), callback=lambda s,d:webbrowser.open("https://github.com/Tremeschin/modular-music-visualizer"))
        Dear.add_separator()
        Dear.add_button(label=Speak("About DearPyGui"), callback=lambda:Dear.show_tool(Dear.mvTool_About))
