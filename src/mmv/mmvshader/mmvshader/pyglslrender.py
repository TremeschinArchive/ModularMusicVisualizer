"""
===============================================================================

Purpose: Render fragment shaders using glslviewer to videos or images,
python wrapper with extra stuff.

Currently needs patched glslviewer tremx binary for rendering videos

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

import subprocess
import threading
import ffmpeg
import shutil
import psutil
import math
import time
import os


class PyGLSLRender:

    """
    kwargs: {
        "width": int
        "height": int

        "fragment_shader": str, path
        "fxaa": bool, True
            Use FXAA?

        "output": str
            Save video/image to this file
        
        "extra_paths_find_glslviewer": list, str
            Extra paths for searching glslviewer binaries

    }
    """
    def __init__(self, mmv, **kwargs):
        self.mmv = mmv
        debug_prefix = "[PyGLSLRender.__init__]"

        # Generic, works for video + image
        self.output = kwargs["output"]

        self.height = int(kwargs["height"])
        self.width = int(kwargs["width"])

        self.fxaa = kwargs.get("fxaa", True)

        # The target shader for rendering
        self.fragment_shader = kwargs["fragment_shader"]
        self.extra_paths_find_glslviewer = kwargs.get("extra_paths_find_glslviewer", [])

        # Get the default glslviewer
        glslviewer_binary = "glslViewer"

        # Take screenshot after this amount of time
        self.wait = float(kwargs.get("wait", 0))

        # Linux doesn't put uppercase on binaries
        if os.name == "posix":
            glslviewer_binary = glslviewer_binary.lower()

        # # Locate the glslviewer binary it

        # Force extra_paths_find_glslviewer being a list if it exists
        if not isinstance(self.extra_paths_find_glslviewer, list):
            self.extra_paths_find_glslviewer = [self.extra_paths_find_glslviewer]

        # Find it
        self.glslviewer = shutil.which(
            cmd = glslviewer_binary,
            path = os.environ["PATH"] + os.pathsep + os.pathsep.join(self.extra_paths_find_glslviewer)
        )

        # Error checking
        assert os.path.exists(self.fragment_shader), f"{debug_prefix} [ERROR] Fragment shader with path [{self.fragment_shader}] doesn't exist"
        assert self.glslviewer != None, f"{debug_prefix} [ERROR] glslviewer binary [{glslviewer_binary}] not found"
    
        # # Default vars / control

        self.running = False
        self.finished = False

    # Recommended max workers for multiprocessing at a given resolution
    def set_recommended_max_workers(self, resolution = (1280, 720)):

        pixels_per_image = (resolution[0] * resolution[1])

        half_cpu = (psutil.cpu_count(logical = False) // 2)

        # pixels_per_image = (1280*720)*4 = recommended = half_cpu / 2
        # pixels_per_image =  1280*720    = recommended = half_cpu
        # pixels_per_image = (1280*720)/4 = recommended = half_cpu * 2

        res_difference = 1 / (pixels_per_image / (1280*720))
        recommended = half_cpu * res_difference

        # Minimum 1 worker otherwise recommended rounded upwards
        self.RECOMMENDED_MAX_WORKERS = max(1, math.ceil(recommended))
        print(self.RECOMMENDED_MAX_WORKERS, res_difference, resolution)

    # Construct the command for calling with subprocess
    def __build_command(self):

        # Basic command for either video and image, certain resolution on headless mode
        self.command = [
            self.glslviewer,
            self.fragment_shader,
            "-w", str(self.width),
            "-h", str(self.height),
            "--headless",
        ]

        # Enable fxaa?
        if self.fxaa:
            self.command += ["--fxaa"]

        # Run and quit after running next argument

        # Instructions to run before quitting
        instruction = ""

        # If we should wait some time before screenshotting
        if self.wait > 0:
            self.command += ["-e", f"wait,{self.wait}"]

        # Final instruction
        instruction += f"screenshot,{self.output}"

        # Add final instruction to command
        self.command += ["-E", instruction]

    # Abstract function for rendering
    # async_render True  calls subprocess.Popen, attributes self.subprocess to that
    # async_render False calls subprocess.run
    def render(self):
        debug_prefix = "[PyGLSLRender.render]"

        self.async_render = async_render
        self.running = True

        # Build the command for running
        self.__build_command()

        # Warn the user with the almighty evil combination of mode=video and async rendering
        if self.mode == "video" and async_render:
            print(debug_prefix, "[WARNING] CAUTION: MODE=VIDEO AND ASYNC_RENDER=TRUE, THIS CAN HANG THE SYSTEM ON LOTS OF SIMULTANEOUS VIDEOS BEING RENDERED")

        # Call the internal function for rendering
        subprocess.run(self.command, stdout = subprocess.DEVNULL, stderr = subprocess.STDOUT)
