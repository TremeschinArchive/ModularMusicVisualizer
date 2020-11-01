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
    
    def init(self, **kwargs) -> None:
        self.width = kwargs["width"]
        self.height = kwargs["height"]
        
        self.glfw_context()
        self.gl_context = skia.GrContext.MakeGL()
        self.info = skia.ImageInfo.MakeN32Premul(self.width, self.height)
        self.surface = skia.Surface.MakeRenderTarget(self.gl_context, skia.Budgeted.kNo, self.info)
        assert self.surface is not None

        # Use CPU for rasterizing, faster transportation of images but slow rendering
        # self.surface = skia.Surface.MakeRasterN32Premul(self.width, self.height)

        with self.surface as canvas:
            self.canvas = canvas
        
        if self.REALTIME:
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

