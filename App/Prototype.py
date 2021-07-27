"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Prototyping stuff

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
class Digestible:
    def __init__(self, locals):
        AssignLocals(locals)
        self.Digest("Hash", NewHash())

    def Digest(self, attr, default):
        if self.OldSelf is not None:
            default = self.OldSelf.__dict__.get(attr, default)
        self.__setattr__(attr, default)

def NewHash(): return str(uuid.uuid4()).replace("-","").upper()

def AssignLocals(data):
    for k,v in data.items():
        if k != "self": data["self"].__setattr__(k,v)

# These are a couple "standards" or rather Don't Repeat Yourself abstractions for Node classes.
class BaseNode(Digestible):

    # Print info about ourselves (all self.* vars)
    def Info(self):
        print(f"\n::Info About [{self}]")
        for key, value in self.__dict__.items():
            if not key.startswith("__"):
                print(f"  [{key}]: [{value}]")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# PROTOTYPE

from pathlib import Path

from MMV.Common.PackUnpack import PackUnpack


class MMVScene(Digestible):
    def __init__(self, OldSelf=None):
        super().__init__(locals())
        self.Digest("Connections", {})
        self.Digest("Nodes", {})

    def AddNode(self, Object):
        self.Nodes[Object.Hash] = Object

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class SomeNode(BaseNode):
    def __init__(self, OldSelf=None):
        super().__init__(locals())
        self.Digest("X", 0)
        self.Digest("Y", 0)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
savefile = Path("./session.MMV.pickle.zlib")

if savefile.exists():
    Scene = MMVScene(OldSelf = PackUnpack.Unpack(savefile))
else:
    Scene = MMVScene()

    S = SomeNode()
    # S.Info()
    # S = SomeNode(S); S.Info()
    Scene.AddNode(S)

for node in Scene.Nodes.values():
    print("Node", node)
    node.Info()

PackUnpack.Pack(Scene, savefile)
