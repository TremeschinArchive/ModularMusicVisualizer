"""
===============================================================================

Purpose: Wrapper for creating a Skia GL context

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
import uuid
import skia
import glfw
import time


class SkiaWrapper:
    def __init__(self, context) -> None:
        self.context = context

    @contextlib.contextmanager
    def glfw_context(self) -> None:
        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        self.window = glfw.create_window(self.context.width, self.context.height, str(uuid.uuid4()), None, None)
        glfw.make_context_current(self.window)
    
    def init(self) -> None:
        self.glfw_context()
        self.gl_context = skia.GrContext.MakeGL()
        self.info = skia.ImageInfo.MakeN32Premul(self.context.width, self.context.height)
        self.surface = skia.Surface.MakeRenderTarget(self.gl_context, skia.Budgeted.kNo, self.info)
        assert self.surface is not None

        with self.surface as canvas:
            self.canvas = canvas

    def terminate_glfw(self) -> None:
        glfw.terminate()
    
    def reset_canvas(self) -> None:
        self.canvas.clear(skia.ColorTRANSPARENT)

    def canvas_array(self) -> None:
        return self.surface.toarray()
