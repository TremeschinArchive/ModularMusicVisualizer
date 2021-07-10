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
import copy
import hashlib
import logging
from pathlib import Path

import dearpygui.dearpygui as Dear
import yaml
from dotmap import DotMap
from MMV.Common.PackUnpack import PackUnpack
from MMV.Common.Polyglot import Polyglot
from MMV.Editor.BaseNode import BaseNode

Speak = Polyglot.Speak


class mmvEditorScene:
    def __init__(self, Editor):
        self.Editor = Editor
        self.Links = self.Editor.ExtendedDotMap()
        self.Nodes = []
        self.PresetName = Speak("New Project")
        self.ClearAvailableNodes()

    def ClearAvailableNodes(self):
        self.AvailableNodes = DotMap(_dynamic=True)

    def FindNode(self, DPG_ID):
        dpfx = "[mmvEditorScene.FindNode]"
        logging.info(f"{dpfx} Finding node with ID: [{DPG_ID}]")
        for Node in self.Nodes:
            logging.info(f"{dpfx} :: Search [{Node.DPG_NODE_ID}] [{Node=}]")
            if Node.DPG_NODE_ID == DPG_ID:
                logging.info(f"{dpfx} Found [{Node}]")
                return Node
        return None

    # Add some Node file to the Editor
    def AddNodeFile(self, path):
        path = Path(path).resolve(); assert path.exists
        node = self.Editor.ImportFileFromPath(path).GetNode(BaseNode)
        node.Config()
        node.SourceFileHash = hashlib.sha256(Path(path).read_text().encode()).hexdigest()
        logging.info(f"[mmvEditor.AddNodeFile] Add node [{node.Name}] category [{node.Category}] from [{path}]")
        self.AvailableNodes[node.Category][node.Name] = node
    
    # Re-read the node files from NodeDir, add (replace) them.
    # Also resets the NodeUI items and redisplays the ones we have
    def AddNodeFilesDataDirRecursive(self, render=True):
        logging.info("[mmvEditor.AddNodeFilesDataDirRecursive] Reloading..")
        self.Editor.ToggleLoadingIndicator()
        self.ClearAvailableNodes()
        for candidate in self.Editor.PackageInterface.NodesDir.rglob("**/*.py"): self.AddNodeFile(candidate)
        if render: self.AddNodeUI.Reset(); self.AddNodeUI.Render()
        self.Editor.ToggleLoadingIndicator()

    # user_data is "pointer" to some Node class
    def AddNodeToScene(self, sender, app_data, node, *a, **k):
        self.Editor._log_sender_data(sender, app_data, node)
        node.Init(InheritedNode=node, Editor=self.Editor)
        node.Render(parent=self.Editor.DPG_NODE_EDITOR)
        self.Nodes.append(node)

    # Some Node was linked
    def NodeAttributeLinked(self, sender, app_data):
        dpfx = f"[mmvEditorScene.NodeAttributeLinked]"
        N1, N2 = app_data
        Dear.add_node_link(N1, N2, parent=sender)
        logging.info(f"{dpfx} Link [{N1=}, {N2=}]")
        N1, N2 = self.FindNode(N1), self.FindNode(N2)
        self.Links.SetDNE(N1, [])
        self.Links.DotMap[N1] += [N2]
        logging.info(f"{dpfx} Links: {self.Links.DotMap}")
        self.Editor.PlaySound(self.Editor.PackageInterface.DataDir/"Sound"/"connect.ogg")
        self.NodeLinksDebug()

    # Some Node was delinked
    def NodeDelinked(self, sender, app_data):
        self.Editor._log_sender_data(sender, app_data)
        Dear.delete_item(app_data)
        self.NodeLinksDebug()

    # [Debug] Show Node connections
    def NodeLinksDebug(self):
        dpfx = "[mmvEditorScene.NodeLinksDebug]"
        logging.info(f"{dpfx} Connections:")
        C = copy.deepcopy(self.Links.DotMap); del C.Hash; C = C.toDict()
        for line in yaml.dump(C, default_flow_style=False, width=50, indent=2).split("\n"):
            if line: logging.info(f"{dpfx} {line}")
