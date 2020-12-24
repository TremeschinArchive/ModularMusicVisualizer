"""
===============================================================================

Purpose: Wrapper for creating a Skia GL context don't draw on screen

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

import contextlib
import threading
import uuid
import skia
import glfw
import time


class SkiaNoWindowBackend:
    def __init__(self) -> None:
        self.REALTIME = False
    
    """
    kwargs: {
        "width": int
        "height": int
        "render_backend": str
            Use or not a GPU accelerated 
    }
    """
    def init(self, **kwargs) -> None:
        
        debug_prefix = "[SkiaNoWindowBackend.init]"

        self.width = kwargs["width"]
        self.height = kwargs["height"]

        # Assume to render on CPU if not said GPU, GPU is less "compatible"
        self.render_backend = kwargs.get("render_backend", "cpu")

        print(debug_prefix, f"Render backend is [{self.render_backend}]")
        
        # GPU for rasterization, faster rendering but slower images transfers
        if self.render_backend == "gpu":
            self.glfw_context()
            self.gl_context = skia.GrDirectContext.MakeGL()
            self.info = skia.ImageInfo.MakeN32Premul(self.width, self.height)
            self.surface = skia.Surface.MakeRenderTarget(self.gl_context, skia.Budgeted.kNo, self.info)

        # Use CPU for rasterizing, faster transportation of images but slow rendering
        elif self.render_backend == "cpu":
            self.surface = skia.Surface.MakeRasterN32Premul(self.width, self.height)
        
        else:
            raise RuntimeError(f"Wrong | Not found render backend: [{self.render_backend}]")

        # Make sure the surface was created
        assert self.surface is not None

        # Get the canvas to draw on
        with self.surface as canvas:
            self.canvas = canvas
        
        if self.REALTIME:
            print(debug_prefix, f"Is REALTIME, threading self.keep_updating")
            threading.Thread(target=self.keep_updating).start()

    @contextlib.contextmanager
    def glfw_context(self) -> None:
        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        rt = glfw.TRUE if self.REALTIME else glfw.FALSE
        glfw.window_hint(glfw.VISIBLE, rt)
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        self.window = glfw.create_window(self.width, self.height, str(uuid.uuid4()), None, None)
        glfw.make_context_current(self.window)

    def keep_updating(self):
        while not glfw.window_should_close(self.window):
            # Swap front and back buffers
            glfw.swap_buffers(self.window)

            # Poll for and process events
            glfw.poll_events()

    def terminate_glfw(self) -> None:
        glfw.terminate()
    
    def reset_canvas(self) -> None:
        self.canvas.clear(skia.ColorTRANSPARENT)

    def canvas_array(self) -> None:
        return self.surface.toarray()

