"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

===============================================================================

Purpose: Restart UI dialog

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

def PleaseRestartUI(Editor, Reason=""):
    with DearCenteredWindow(Editor.Context, label=Speak(Reason), width=500, height=200, min_size=[500,0]) as RestartWindow:
        A=Dear.add_text(f"\n" + Speak("We need to restart for this setting to take effect, proceed?") + "\n\n")
        B=Dear.add_button(label=Speak("Ok (Restart)"), callback=Editor.Restart)
        Dear.add_same_line()
        Dear.add_text("    ")
        Dear.add_same_line()
        C=Dear.add_button(label=Speak("No (Continue)"), callback=lambda d,s,UserData: Dear.delete_item(RestartWindow))
        for Item in [A,B,C]:
            Dear.set_item_font(Item, Editor.LoadedFonts[UserData.Font])


