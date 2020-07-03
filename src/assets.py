"""
===============================================================================

Purpose: Generate the CGI assets

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

from utils import Utils
import subprocess
import os


class Assets():
    def __init__(self, context):

        debug_prefix = "[Canvas.__init__]"

        self.context = context
        self.utils = Utils()

        self.ROOT = self.utils.get_root()

    def pygradienter(self, profile, width, height, n=1):
        subprocess.call(
            [
                "python",
                self.ROOT + os.path.sep + "pygradienter" + os.path.sep + "src" + os.path.sep + "pygradienter.py", 
                "-p", profile,
                "-x", width,
                "-y", height,
                "-n", n
            ]
        )

a = Assets(None)
a.pygradienter("particles", 400, 400, 1)