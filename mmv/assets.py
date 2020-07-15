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

from mmv.utils import Utils
import subprocess
import os


class Assets():
    def __init__(self, context):

        debug_prefix = "[Canvas.__init__]"

        self.context = context
        self.utils = Utils()

        self.ROOT = self.utils.get_root()

    # Generate a pygradienter image of a given profile and move it to the assets folder
    def pygradienter(self, profile, width, height, n=1, delete_existing_files=False):

        # Define where stuff is
        pygradient_src_dir = self.ROOT + os.path.sep + "pygradienter" + os.path.sep + "src"  + os.path.sep
        move_to_assets_subdir = self.context.assets + os.path.sep + "pygradienter" + os.path.sep + profile

        if delete_existing_files:
            self.utils.rmdir(move_to_assets_subdir)

        # Make the assets subdirectory
        self.utils.mkdir_dne(move_to_assets_subdir)

        # Call pygradienter to generate the image
        subprocess.call(
            [
                "python",
                pygradient_src_dir + "pygradienter.py", 
                "-p", profile,
                "-x", str(width),
                "-y", str(height),
                "-n", str(n),
                "-q"
            ]
        )

        # Copy every file from src to dst
        self.utils.copy_files_recursive(
            pygradient_src_dir + "data" + os.path.sep + profile + os.path.sep + str(width) + "x" + str(height),
            move_to_assets_subdir
        )
