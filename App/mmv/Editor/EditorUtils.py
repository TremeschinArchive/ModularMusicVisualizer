"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Code refactoring, some weirdo flex utils classes and functions...

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
import uuid
from contextlib import contextmanager

import dearpygui.dearpygui as Dear
from dotmap import DotMap
from watchdog.events import PatternMatchingEventHandler

from mmv.Common.PackUnpack import PackUnpack


# Enter a DPG container Stack using "with", it pushes then pops after exiting
class EnterContainerStack:
    def __init__(self, DearID): Dear.push_container_stack(DearID)
    def __enter__(self): ...
    def __exit__(self, *args, **kwargs): Dear.pop_container_stack()


# Toggle one bool from __dict__ safely, creates if doesn't exist
def ToggleAttrSafe(InternalDict, Key, Default=True):
    InternalDict[Key] = not InternalDict.get(Key, Default)


@contextmanager
def CenteredWindow(Context, **k):
    try:
        # Default values
        for item, value in [
            ("modal",True), ("no_move",True),
            ("autosize",True), ("label",""),
        ]:
            k[item] = k.get(item, value)

        # Add centered window
        window = Dear.add_window(**k)
        Dear.push_container_stack(window)
        Dear.set_item_pos(
            item=window,
            pos=[
                ( Context.DotMap.WINDOW_SIZE[0] - k.get("width", 0) - k.get("offx",0) ) / 2,
                ( Context.DotMap.WINDOW_SIZE[1] - k.get("height",0) - k.get("offy",0) ) / 2,
            ])
        yield window
    finally: Dear.pop_container_stack()


class PayloadTypes:
    Image  = "Image"
    Shader = "Shader"
    Number = "Number"


# Create one Watchdog template with some functions that does nothing
def WatchdogTemplate():
    T = PatternMatchingEventHandler(["*"], None, False, True)
    T.on_created  = lambda *a,**b: None
    T.on_deleted  = lambda *a,**b: None
    T.on_modified = lambda *a,**b: None
    T.on_moved    = lambda *a,**b: None
    return T


# Get one _pretty_ identifier, uppercase without dashes uuid4
def NewHash(): return str(uuid.uuid4()).replace("-","").upper()


# Very Weird'n'Lazy Overkill Way of assigning all locals() that aren't
# attributes as self.* variables.
def AssignLocals(data):
    for k,v in data.items():
        if k != "self": data["self"].__setattr__(k,v)


# Toggle one bool from __dict__ safely, creates if doesn't exist
def ToggleAttrSafe(InternalDict, Key, Default=True):
    InternalDict[Key] = not InternalDict.get(Key, Default)

class EmptyCallable:
    def __init__(self): ...
    def __call__(self): ...

# # ExtendedDotMap
class ExtendedDotMap:
    def __init__(self, OldSelf=None, SetCallback=EmptyCallable()):
        AssignLocals(locals())
        self.DotMap = DotMap(_dynamic=False)
        self.Digest("Hash", NewHash())

    # If we have one OldSelf, attempt to get its attribute to current DotMap
    def Digest(self, Name, Default):
        if self.OldSelf is not None:
            Value = self.OldSelf.get(Name, Default)
        else: Value = Default
        logging.info(f"[ExtendedDotMap.Digest] {Name=} => {Default=} | {Value=}")
        self.DotMap[Name] = Value

    # Set one attribute 
    def ForceSet(self, Key, Value):
        logging.info(f"[ExtendedDotMap.ForceSet] {Key} => {Value}")
        self.DotMap[Key] = Value
        self.SetCallback()

    # Get one attribute if it exists, if it doesn't set to default
    def SetDNE(self, Key, Default):
        logging.info(f"[ExtendedDotMap.SetDNE] {Key} => {Default}")
        self.DotMap[Key] = self.DotMap.get(Key, Default)
        self.SetCallback()

    # Toggle one boolean on this DotMap safely
    def ToggleBool(self, Key, Default=False):
        self.ForceSet(Key, not self.DotMap.get(Key, not Default))

    # Pack this DotMap to a file so we load it later on
    def Pack(self, path): PackUnpack.Pack(self.DotMap, path)

