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

from OpenGL import GL
import numpy as np
import contextlib
import threading
import uuid
import skia
import glfw
import time


class SkiaNoWindowBackend:
    """
    kwargs: {
        "width": int
        "height": int
        "render_backend": str, ["gpu", "cpu"]
            Use or not a GPU accelerated 
        "show_preview_window": bool, False
            Visualize the window in real time?
    }
    """
    def init(self, **kwargs) -> None:
        debug_prefix = "[SkiaNoWindowBackend.init]"

        self.width = kwargs["width"]
        self.height = kwargs["height"]

        # Assume to render on CPU if not said GPU, GPU is less "compatible"
        self.render_backend = kwargs.get("render_backend", "cpu")
        self.show_preview_window = kwargs.get("show_preview_window", True)

        print(debug_prefix, f"Render backend is [{self.render_backend}]")
        
        # GPU for rasterization, faster rendering but slower images transfers
        if self.render_backend == "gpu":
            self.glfw_context()
            self.gl_context = skia.GrDirectContext.MakeGL()

            if self.show_preview_window:
                backend_render_target = skia.GrBackendRenderTarget(
                    self.width,
                    self.height,
                    0,  # sampleCnt
                    0,  # stencilBits
                    skia.GrGLFramebufferInfo(0, GL.GL_RGBA8)
                )
                self.info = skia.ImageInfo.MakeN32Premul(self.width, self.height)
                self.surface = skia.Surface.MakeFromBackendRenderTarget(
                    self.gl_context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
                    skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
            else:
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
        
    @contextlib.contextmanager
    def glfw_context(self) -> None:
        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        rt = glfw.TRUE if self.show_preview_window else glfw.FALSE
        glfw.window_hint(glfw.VISIBLE, rt)
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        # glfw.window_hint(glfw.DOUBLEBUFFER, glfw.FALSE)
        self.window = glfw.create_window(self.width, self.height, "Modular Music Visualizer Realtime Preview", None, None)
        glfw.make_context_current(self.window)
        # glfw.swap_interval(0)

    def update(self):
        self.surface.flushAndSubmit()
        # Swap front and back buffers
        glfw.swap_buffers(self.window)
        # Poll for and process events
        glfw.poll_events()

    def terminate_glfw(self) -> None:
        glfw.terminate()
    
    def reset_canvas(self) -> None:
        self.canvas.clear(skia.ColorTRANSPARENT)

    def canvas_array(self) -> None:
        # Nah not any faster
        # self.surface.flushAndSubmit()
        # image = self.surface.makeImageSnapshot()
        # return np.array(image.makeRasterImage())

        return self.surface.toarray(
            colorType = skia.kRGBA_8888_ColorType
        )

