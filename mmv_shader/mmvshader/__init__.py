"""
===============================================================================

Purpose: Utility to wrap around mpv and add processing shaders, target
resolutions, input / output

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

from mmvshader.mmv_shader_maker import MMVShaderMaker
from mmvshader.mmv_shader_mpv import MMVShaderMPV
from mmvshader.mmv_shader_context import Context
from mmvshader.mmv_utils import MMVUtils
import sys
import os


class MMVShaderMain:
    def __init__(self):
        debug_prefix = "[MMVShaderMain.__init__]"
        print(debug_prefix, "Hello World!!")
        
        # Where this file is located, please refer using this on the whole package
        if getattr(sys, 'frozen', True):    
            self.DIR = os.path.dirname(os.path.abspath(__file__))
            print(debug_prefix, "Running from source code")
        else:
            self.DIR = os.path.dirname(os.path.abspath(sys.executable))
            print(debug_prefix, "Running from release (sys.executable..?)")

        print(debug_prefix, f"MMV Located at [{self.DIR}]")

        # # Create classes

        print(debug_prefix, "Creating MMVUtils")
        self.utils = MMVUtils()

        print(debug_prefix, "Creating Context")
        self.context = Context(self)

        print(debug_prefix, "Creating MMVShaderMPV")
        self.mpv = MMVShaderMPV(self)

        print(debug_prefix, "Creating MMVShaderMaker")
        self.maker = MMVShaderMaker(self)
