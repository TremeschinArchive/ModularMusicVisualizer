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
from mmvshader.mmv_shader_utils import MMVUtils
import shutil
import math
import sys
import os


class MMVShaderMain:
    def __init__(self):
        debug_prefix = "[MMVShaderMain.__init__]"
        print(debug_prefix, "Hello World!!")

        # Greeter message
        misc = Miscellaneous()
        misc.greeter_message()
        
        # Where this file is located, please refer using this on the whole package
        if getattr(sys, 'frozen', True):    
            self.DIR = os.path.dirname(os.path.abspath(__file__))
            print(debug_prefix, "Running from source code")
        else:
            self.DIR = os.path.dirname(os.path.abspath(sys.executable))
            print(debug_prefix, "Running from release (sys.executable..?)")

        print(debug_prefix, f"MMV Located at [{self.DIR}]")

        # # Os we're operating

        self.os = {
            "posix": "linux",
            "nt": "windows",
            "darwin": "macos"
        }.get(os.name)

        # # Create classes

        print(debug_prefix, "Creating MMVUtils")
        self.utils = MMVUtils()

        print(debug_prefix, "Creating Context")
        self.context = Context(self)

        print(debug_prefix, "Creating MMVShaderMPV")
        self.mpv = MMVShaderMPV(self)

        print(debug_prefix, "Creating MMVShaderMaker")
        self.shader_maker = MMVShaderMaker(self)



class Miscellaneous:
    def __init__(self) -> None:
        self.version = "0.0.0-R&D"

    def greeter_message(self) -> None:

        self.terminal_width = shutil.get_terminal_size()[0]

        bias = " "*(math.floor(self.terminal_width/2) - 14)

        message = \
f"""{"-"*self.terminal_width}
{bias} __  __   __  __  __     __
{bias}|  \\/  | |  \\/  | \\ \\   / /
{bias}| |\\/| | | |\\/| |  \\ \\ / / 
{bias}| |  | | | |  | |   \\ V /  
{bias}|_|  |_| |_|  |_|    \\_/   
{bias}
{bias[:-8]}Modular Music Visualizer GLSL Edition ltd.                       
{bias}{(21-len("Version")-len(self.version))*" "}Version {self.version}
{"-"*self.terminal_width}
"""
        print(message)

    def thanks_message(self):
        # # Print thanks message :)

        message = \
f"""
 [+-------------------------------------------------------------------------------------------+]
  |                                                                                           |
  |              :: Thanks for using the Modular Music Visualizer project !! ::               |
  |              ==============================================================               |
  |                                                                                           |
  |  Here's a few official links for MMV:                                                     |
  |                                                                                           |
  |    - Telegram group:          [          https://t.me/modular_music_visualizer         ]  |
  |    - GitHub Repository:       [ https://github.com/Tremeschin/modular-music-visualizer ]  |
  |    - GitLab Repository:       [ https://gitlab.com/Tremeschin/modular-music-visualizer ]  |
  |                                                                                           |
  |  > Always check for the copyright info on the material you are using (audios, images)     |
  |  before distributing the content generated with MMV, I take absolutely no responsibility  |
  |  for any UGC (user generated content) violations. See LICENSE file as well.               |
  |                                                                                           |
  |  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  |
  |                                                                                           |
  |             Don't forget sharing your releases made with MMV on the discussion groups :)  |
  |                 Feel free asking for help or giving new ideas for the project as well !!  |
  |                                                                                           |
 [+-------------------------------------------------------------------------------------------+]
"""
        print(message)
