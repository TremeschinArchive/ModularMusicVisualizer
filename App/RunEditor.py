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
import os
# Add current directory to PATH so we find the "MMV" package
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time

import dearpygui.dearpygui as Dear
import MMV


def RunEditor():
    PackageInterface = MMV.mmvPackageInterface()
    Editor = PackageInterface.GetEditor()
    Editor.InitMainWindow()
    Editor.MainLoop()
    return Editor

def Main():
    while True:
        if RunEditor()._mmvRestart_: continue
        else: break

if __name__ == "__main__":
    Main()