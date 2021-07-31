"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

===============================================================================

Purpose: UI for FFmpeg config for Sombrero to render video

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
import dearpygui.dearpygui as Dear
from MMV.Common.DearPyGuiUtils import *
from MMV.Common.Polyglot import Polyglot
from MMV.Common.Utils import Utils

Speak = Polyglot.Speak

class RenderVideoUI:
    def __init__(self, Editor):
        self.Editor = Editor
    
    def ChoseFile(self, AssignTo, Title, Extensions):
        with Dear.file_dialog(
                label=Speak(Title), modal=True,
                callback=lambda sender,data:
                    Dear.configure_item(AssignTo, default_value=data["file_path_name"])):
            Dear.add_file_extension(Extensions, color=self.Editor.DearPyStuff.ThemeYaml.mmvSectionText)

    def ToggleEnabled(self, DPG_Items):
        DPG_Items = Utils.ForceList(DPG_Items)
        for Item in DPG_Items:
            Dear.configure_item(Item, enabled=not Dear.get_item_configuration(Item)["enabled"])

    def Render(self):
        with Dear.table(header_row=False, resizable=True):
            Dear.add_table_column()

            with Dear.table(header_row=True, resizable=True, row_background=True, borders_outerV=True, borders_outerH=True):
                Dear.add_table_column(label=Speak("Basic"))
                Dear.add_table_column(label=Speak("Advanced"))
       
                self.DPG_InputAudioFile = Dear.add_input_text(label="", hint=Speak("Path to Audio File"))
                Dear.add_same_line()
                self.DPG_ChoseAudioButton = Dear.add_button(label=Speak("Chose Audio"),
                    callback=lambda: self.ChoseFile(
                        AssignTo=self.DPG_InputAudioFile,
                        Title=Speak("Select Audio File"),
                        Extensions=Speak("Audio Files")+"{.mp3,.ogg,.wav,.flac,.opus,.tiff,.m4a,.aac}")
                )

                Dear.add_same_line()
                Dear.add_checkbox(
                    label=Speak("Audio"),
                    callback=lambda: self.ToggleEnabled([self.DPG_InputAudioFile, self.DPG_ChoseAudioButton]))

                # # #

                self.DPG_InputFrameRate = Dear.add_input_float(
                    label=Speak("Framerate (FPS)"), default_value=60,
                    step=1, min_value=1, max_value=240, format="%.2f")


            Dear.add_table_next_column()


            with Dear.table(header_row=True, resizable=True, row_background=True, borders_outerV=True, borders_outerH=True):
                Dear.add_table_column(label=Speak("Actions"))
                Dear.add_button(label=Speak("Render Video"))

