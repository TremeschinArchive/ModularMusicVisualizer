"""
===============================================================================

Purpose: Main file initializer and core loop of a Pyskt for window

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

from mmv.pyskt.pyskt_processing import PysktProcessing
from mmv.pyskt.pyskt_draw_utils import SkiaDrawUtils
from mmv.pyskt.pyskt_context import PysktContext
from mmv.pyskt.pyskt_colors import PysktColors
from mmv.pyskt.pyskt_events import PysktEvents
from OpenGL import GL
import threading
import random
import skia
import glfw
import time


# The main code here I got from
# https://github.com/kyamagu/skia-python/issues/105

"""
kwargs:

{
    "context_window_name": "PySKT Window", window name
    "context_show_debug": False, log fps to console
    "context_wait_events": True, don't draw window at each update, only if mouse moved or key pressed
}
"""
class PysktMain:
    def __init__(self, mmv_main, *args, **kwargs):
        self.mmv_main = mmv_main
        self.pyskt_context = PysktContext(self, *args, **kwargs)
        self.pyskt_processing = PysktProcessing(self)
        self.draw_utils = SkiaDrawUtils(self)
        self.colors = PysktColors(self)
        self.events = PysktEvents(self)
        self.previous_mouse_pos = [0, 0]
        self.mouse_moved = False
        
        # Where stuff is rendered from and activated

        self.components = []

        # # # Make main window

        # Init GLFW        
        if not glfw.init():
            raise RuntimeError('glfw.init() failed')

        # GLFW config
        glfw.window_hint(glfw.STENCIL_BITS, 0)
        glfw.window_hint(glfw.DEPTH_BITS, 0)
        # glfw.window_hint(glfw.DECORATED, False)
        glfw.window_hint(glfw.DOUBLEBUFFER, False)

        # Create window
        self.window = glfw.create_window(
            self.pyskt_context.width,
            self.pyskt_context.height,
            kwargs.get("context_window_name", "PySKT Window"),
            None, None,
        )

        # Make context, init surface
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        context = skia.GrContext.MakeGL()

        # Set render to a display compatible
        backend_render_target = skia.GrBackendRenderTarget(
            self.pyskt_context.width,
            self.pyskt_context.height,
            0,  # sample count
            0,  # stencil bits
            skia.GrGLFramebufferInfo(0, GL.GL_RGBA8)
        )

        # Create draw surface
        self.surface = skia.Surface.MakeFromBackendRenderTarget(
            context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB()
        )
        assert self.surface, 'Failed to create a surface'
        self.canvas = self.surface.getCanvas()
        
    # For animations, thread wait events
    def events_loop(self):
        glfw.wait_events()
    
    def check_mouse_moved(self):
        if not self.mouse_pos == self.previous_mouse_pos:
            self.mouse_moved = True
            self.previous_mouse_pos = self.mouse_pos
        else:
            self.mouse_moved = False
    # Run main loop of pyskt window
    def run(self):

        # Calculate fps?
        if self.pyskt_context.show_debug:
            frame_times = [0]*120
            frame = 0
            last_time_completed = time.time()

        # Link events to parsers
        glfw.set_window_size_callback(self.window, self.events.on_window_resize)
        glfw.set_mouse_button_callback(self.window, self.events.mouse_callback)
        glfw.set_scroll_callback(self.window, self.events.mouse_callback)
        glfw.set_key_callback(self.window, self.events.keyboard_callback)

        glfw.set_drop_callback(self.window, self.events.on_file_drop)

        scroll_text_x = self.pyskt_context.width // 2
        scroll_text_y = self.pyskt_context.height // 2
        wants_to_go = [scroll_text_x, scroll_text_y]

        threading.Thread(target=self.events_loop).start()
        
        # Loop until the user closes the window
        while not glfw.window_should_close(self.window):

            # Wait events if said to
            # if self.pyskt_context.wait_events:
            
            # Clear canvas
            self.canvas.clear(self.colors.background)

            # Get mouse position
            self.mouse_pos = glfw.get_cursor_pos(self.window)
            self.check_mouse_moved()

            if self.events.left_click:
                wants_to_go[0] -= self.events.scroll * 50
            else:
                wants_to_go[1] -= self.events.scroll * 50
            
            # We have now to recursively search through the components dictionary

            scroll_text_x = scroll_text_x + (wants_to_go[0] - scroll_text_x) * 0.3
            scroll_text_y = scroll_text_y + (wants_to_go[1] - scroll_text_y) * 0.3

            self.draw_utils.anchored_text(
                canvas = self.canvas,
                text = "A Really long and centered text",
                x = scroll_text_x,
                y = scroll_text_y,
                anchor_x = 0.5,
                anchor_y = 0.5,
            )


            # Hover testing
            for _ in range(20):
                random.seed(_)

                xywh_rect = [random.randint(0, 1000), random.randint(0, 1000), random.randint(0, 400), random.randint(0, 400)]
                
                # Rectangle border
                # rect = self.pyskt_processing.rectangle_x_y_w_h_to_coordinates(*xywh_rect)

                info = self.pyskt_processing.point_against_rectangle(self.mouse_pos, xywh_rect)

                if info["is_inside"]:
                    paint = skia.Paint(
                        AntiAlias = True,
                        Color = skia.Color4f(1, 0, 1, 1),
                        Style = skia.Paint.kFill_Style,
                        StrokeWidth = 2,
                    )
                else:
                    c = 1 - (info["distance"]/1080)
                    paint = skia.Paint(
                        AntiAlias = True,
                        Color = skia.Color4f(c, c, c, 1),
                        Style = skia.Paint.kFill_Style,
                        StrokeWidth = 2,
                    )

                # Draw the border
                self.canvas.drawRect(
                    skia.Rect(*self.pyskt_processing.rectangle_x_y_w_h_to_skia_rect(*xywh_rect)),
                    paint
                )

            # # #

            # Show fps
            if self.pyskt_context.show_debug:
                frame_times[frame % 120] = time.time() - last_time_completed
                absolute_frame_times = [x for x in frame_times if not x == 0]
                fps = 1/(sum(absolute_frame_times)/len(absolute_frame_times))

                last_time_completed = time.time()
                frame += 1

                self.draw_utils.anchored_text(
                    canvas = self.canvas, 
                    text = [f"{fps=:.1f}", f"mouse_pos={self.mouse_pos}"],
                    x = 0, y = 0,
                    anchor_x = 0,
                    anchor_y = 0,
                    # kwargs
                    font = skia.Font(skia.Typeface('Arial'), 12),
                )

            # If any event doesn't return to "None" state
            self.events.reset_non_ending_states()

            # Flush buffer
            self.surface.flushAndSubmit()

            # Swap front and back buffers
            glfw.swap_buffers(self.window)

            # Poll for and process events
            glfw.poll_events()

        # End glfw
        glfw.terminate()
