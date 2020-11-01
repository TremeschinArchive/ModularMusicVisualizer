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

from mmv.pyskt.skia_no_window_backend import SkiaNoWindowBackend
import mmv
import os

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

processing = mmv.mmv()


experiment = "pygradienter"

if experiment == "pyskt":
    sk = processing.pyskt_test(
        context_width = 1280,
        context_height = 720,
        context_show_debug = True,
        context_wait_events = True,
    )
    sk.run()

elif experiment == "sample_sorter":
    sorter = processing.sample_sorter(
        path = "/some/path",
    )

elif experiment == "gui":
    # gui = processing.gui()
    pass

elif experiment == "pygradienter":

    width = 500
    height = 500

    skia = SkiaNoWindowBackend()
    skia.init(
        width = width,
        height = height,
    )

    # Get a pygradienter object
    pygradienter = processing.pygradienter(
        skia = skia,
        width = width,
        height = height,
        n_images = 50,
        output_dir = THIS_FILE_DIR + "/pyg",
        mode = "particle"
    )

    pygradienter.run()



