"""
===============================================================================

Purpose: Test file for PySKT

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

from modules.end_user_utilities import Requirements, ArgParser
from mmv.pyskt.pyskt_backend import SkiaNoWindowBackend
from mmv.experiments.sample_sorter import SampleSorter
from mmv.pygradienter.pyg_main import PyGradienter
from modules.make_release import MakeRelease
from mmv.mmv_configure import MMVEndUser
import sys
import os


class Experiments:
    def __init__(self, argv):

        self.THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.processing = MMVEndUser()

        # Parse shell arguments
        self.args = ArgParser(argv)

        experiment = self.args.kflags["experiment"]

        if experiment == "sample_sorter":
            sorter = SampleSorter(
                mmv = self.processing.mmv_main,
                path = "/some/path",
            )

        elif experiment == "pygradienter":

            width = 500
            height = 500

            skia = SkiaNoWindowBackend()
            skia.init(
                width = width,
                height = height,
            )

            # Get a pygradienter object
            pygradienter = PyGradienter(
                mmv = self.processing.mmv_main,
                skia = skia,
                width = width,
                height = height,
                n_images = 50,
                output_dir = self.THIS_FILE_DIR + "/pyg",
                mode = "particle"
            )

            pygradienter.run()

        elif experiment == "release":
            self.processing.download_check_ffmpeg(making_release = True)
            mk = MakeRelease(
                mmv = self.processing.mmv_main,
                project_root = self.THIS_FILE_DIR,
                mmv_folder = self.THIS_FILE_DIR + "/mmv",
                **self.args.kflags,
            )
            mk.create()


if __name__ == "__main__":
    experiments = Experiments(sys.argv)