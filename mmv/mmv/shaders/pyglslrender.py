"""
===============================================================================

Purpose: Render fragment shaders using glslviewer to videos or images,
python wrapper with extra stuff

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
import ffmpeg
import shutil
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

        "mode": image, video
            video:
                "video_fps": float, 60
                    Frames Per Second for rendering the video
                "video_start": float, 0, seconds
                "video_end": float, seconds
                    Time for starting to render the shader and stopping

            image:
        
        "extra_paths": list, str
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
        self.extra_paths = kwargs.get("extra_paths", [])

        # Image or video mode
        self.mode = kwargs["mode"]

        # Render a video out of a shader with desired duration
        if self.mode == "video":

            # Custom glslviewer until they implement this feature I asked (?)
            glslviewer_binary = "glslviewertremxrendervideo"
            
            # # Video settings
            
            self.video_start = kwargs["video_start"]
            self.video_end = kwargs["video_end"]

            self.video_fps = kwargs["video_fps"]
        
        # Render a image out of the shader
        elif self.mode == "image":

            # Get the default glslviewer
            glslviewer_binary = "glslViewer"

        else:
            raise RuntimeError(f"Invalid mode [{self.mode}]")
        
        # Linux doesn't put uppercase on binaries
        if os.name == "posix":
            glslviewer_binary = glslviewer_binary.lower()

        # # Locate the glslviewer binary it

        # Force extra_paths being a list if it exists
        if not isinstance(self.extra_paths, list):
            self.extra_paths = [self.extra_paths]

        # Find it
        search_path = os.environ["PATH"] + os.pathsep + os.pathsep.join(self.extra_paths)
        self.glslviewer = shutil.which(glslviewer_binary, path = search_path)

        # Error checking
        assert os.path.exists(self.fragment_shader), f"{debug_prefix} [ERROR] Fragment shader with path [{self.fragment_shader}] doesn't exist"
        assert self.glslviewer != None, f"{debug_prefix} [ERROR] glslviewer binary [{glslviewer_binary}] not found"
    
    # Construct the command for calling with subprocess
    def __build_command(self):
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

        # Mode is video, use sequence command then exit
        if self.mode == "video":
            self.command += [
                "-E", f"sequence,{self.video_start},{self.video_end},{self.video_fps}"
            ]

        # Mode is image, use screenshot command and save to output
        elif self.mode == "image":
            self.command += [
                "-E", f"screenshot,{self.output}"
            ]

    # Abstract function for rendering
    # async_render True  calls subprocess.Popen, attributes self.subprocess to that
    # async_render False calls subprocess.run
    def render(self, async_render: bool = False):
        debug_prefix = "[PyGLSLRender.render]"

        self.async_render = async_render

        # Build the command for running
        self.__build_command()

        # Warn the user with the almighty evil combination of mode=video and async rendering
        if self.mode == "video" and async_render:
            print(debug_prefix, "[WARNING] CAUTION: MODE=VIDEO AND ASYNC_RENDER=TRUE, THIS CAN HANG THE SYSTEM ON LOTS OF SIMULTANEOUS VIDEOS BEING RENDERED")

        # Call the internal function for rendering
        if self.mode == "video":
            self.__render_video()
        elif self.mode == "image":
            self.__render_image()
        
    # Wait until the subprocess finished (useful for syncing after multiple simultaneous renders)
    def wait(self):
        if self.async_render:
            self.subprocess.wait()

    # Render a video out of the configured settings
    def __render_video(self):
        debug_prefix = "[PyGLSLRender.__render_image]"

        print(debug_prefix, f"Rendering video {self.command}")

        # Start FFmpeg subprocess
        self.ffmpeg_subprocess = (
            ffmpeg
            .input('pipe:', format = "rawvideo", pix_fmt = "rgb24", r = self.video_fps, s = f"{self.width}x{self.height}")
            .output(self.output, pix_fmt = "yuv420p", vcodec = "libx264", r = self.video_fps, crf = 14, vf = "vflip", loglevel = "quiet")
            .overwrite_output()
            .run_async(pipe_stdin = True)
        )

        # Run in async or not mode
        if self.async_render:
            self.subprocess = subprocess.Popen(self.command, stdout = self.ffmpeg_subprocess.stdin, stderr = subprocess.STDOUT)
        else:
            subprocess.run(self.command, stdout = self.ffmpeg_subprocess.stdin, stderr = subprocess.STDOUT)

    # Render a image out of the configured settings
    def __render_image(self):
        print(f"[PyGLSLRender.__render_image] Rendering image {self.command}")

        # Run in async or not mode
        if self.async_render:
            self.subprocess = subprocess.Popen(self.command, stdout = subprocess.DEVNULL, stderr = subprocess.STDOUT)
        else:
            subprocess.run(self.command, stdout = subprocess.DEVNULL, stderr = subprocess.STDOUT)

        
