"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Store current scene, open, save, recently used

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

import dearpygui.dearpygui as dear
from dotmap import DotMap

from mmv.Common.PackUnpack import PackUnpack


class mmvEditorScene:
    def __init__(self, Editor):
        self.Editor = Editor
        self.Links = {}
        self.Nodes = []
        self.PresetName = "NewPreset"
        self.ClearAvailableNodes()
        
    def ClearAvailableNodes(self):
        self.AvailableNodes = DotMap(_dynamic=True)
