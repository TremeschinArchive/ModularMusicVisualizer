"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Window utilities, functions for MMVShaderMGL

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
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from moderngl_window.conf import settings
import moderngl_window
import numpy as np
import logging
import imgui


class MMVShaderMGLWindowHandlers:
    def __init__(self, mmv_shader_mgl):
        self.mmv_shader_mgl = mmv_shader_mgl
        
        # Mouse related controls
        self.target_zoom = 1
        self.target_drag = np.array([0.0, 0.0])

        # Multiplier on top of multiplier, configurable real time
        self.target_intensity = 1
        self.intensity = 1

        # Keys
        self.shift_pressed = False
        self.ctrl_pressed = False

    # Which "mode" to render, window loader class, msaa, ssaa, vsync, force res?
    def mode(self, window_class, msaa = 1, vsync = True, strict = False, icon = None):
        debug_prefix = "[MMVShaderMGLWindowHandlers.mode]"
        logging.info(f"{debug_prefix} \"i\" Set window mode [window_class={window_class}] [msaa={msaa}] [vsync={vsync}] [strict={strict}] [icon={icon}]")

        # Get function arguments
        self.headless = window_class == "headless"
        self.strict = strict
        self.vsync = vsync
        self.msaa = msaa

        # Headless we disable vsync because we're rendering only..?
        # And also force aspect ratio just in case (strict option)
        if self.headless:
            self.strict = True
            self.vsync = False

        # Assign the function arguments
        settings.WINDOW["class"] = f"moderngl_window.context.{window_class}.Window"
        settings.WINDOW["aspect_ratio"] = self.mmv_shader_mgl.width / self.mmv_shader_mgl.height
        settings.WINDOW["vsync"] = self.vsync
        settings.WINDOW["title"] = "MMVShaderMGL Window"
        settings.WINDOW["size"] = (self.mmv_shader_mgl.width, self.mmv_shader_mgl.height)

        # Create the window
        self.window = moderngl_window.create_window_from_settings()

        # Make sure we render strictly into the resolution we asked
        if strict:
            # self.window.set_default_viewport()
            self.window.fbo.viewport = (0, 0, self.mmv_shader_mgl.width, self.mmv_shader_mgl.height)

        # Set the icon
        if icon is not None:
            self.window.set_icon(icon_path = icon)
        
        # The context we'll use is the one from the window
        self.gl_context = self.window.ctx
        self.mmv_shader_mgl.gl_context = self.gl_context
        self.window_should_close = False

        # Functions of the window if not headless
        if not self.headless:
            self.window.resize_func = self.window_resize
            self.window.key_event_func = self.key_event
            self.window.mouse_position_event_func = self.mouse_position_event
            self.window.mouse_drag_event_func = self.mouse_drag_event
            self.window.mouse_scroll_event_func = self.mouse_scroll_event
            self.window.mouse_press_event_func = self.mouse_press_event
            self.window.mouse_release_event_func = self.mouse_release_event
            self.window.unicode_char_entered_func = self.unicode_char_entered
            self.window.close_func = self.close
            imgui.create_context()
            self.imgui = ModernglWindowRenderer(self.window)

    # [NOT HEADLESS] Window was resized, update the width and height so we render with the new config
    def window_resize(self, width, height):
        if hasattr(self, "strict"):
            if self.strict:
                return

        # Set width and height
        self.mmv_shader_mgl.width = int(width)
        self.mmv_shader_mgl.height = int(height)

        # Recursively call this function on every shader on textures dictionary
        for index in self.mmv_shader_mgl.textures.keys():
            if self.mmv_shader_mgl.textures[index]["loader"] == "shader":
                self.mmv_shader_mgl.textures[index]["shader_as_texture"].window_handlers.window_resize(
                    width = self.mmv_shader_mgl.width, height = self.mmv_shader_mgl.height
                )

        # Search for dynamic shaders and update them
        for index in self.mmv_shader_mgl.textures.keys():
            if self.mmv_shader_mgl.textures[index].get("dynamic", False):
                # Release OpenGL stuff
                self.mmv_shader_mgl.textures[index]["shader_as_texture"].render_buffer.release()
                self.mmv_shader_mgl.textures[index]["shader_as_texture"].texture.release()
                self.mmv_shader_mgl.textures[index]["shader_as_texture"].fbo.release()
                self.mmv_shader_mgl.textures[index]["shader_as_texture"].vao.release()

                # Create new ones in place
                self.mmv_shader_mgl.textures[index]["shader_as_texture"]._create_vao()
                self.mmv_shader_mgl.textures[index]["shader_as_texture"]._create_assing_texture_fbo_render_buffer()

                # Assign texture
                self.mmv_shader_mgl.textures[index]["texture"] = self.mmv_shader_mgl.textures[index]["shader_as_texture"].texture

        # Master shader has window and imgui
        if self.mmv_shader_mgl.master_shader:
            if not self.headless:
                self.imgui.resize(self.mmv_shader_mgl.width, self.mmv_shader_mgl.height)

            # Window viewport
            self.window.fbo.viewport = (0, 0, self.mmv_shader_mgl.width, self.mmv_shader_mgl.height)

    def drop_textures(self):
        # Search for dynamic shaders and update them
        for index in self.mmv_shader_mgl.textures.keys():
            if "shader_as_texture" in self.mmv_shader_mgl.textures[index].keys():
                self.mmv_shader_mgl.textures[index]["shader_as_texture"].render_buffer.release()
                self.mmv_shader_mgl.textures[index]["shader_as_texture"].texture.release()
                self.mmv_shader_mgl.textures[index]["shader_as_texture"].fbo.release()
                self.mmv_shader_mgl.textures[index]["shader_as_texture"].vao.release()
            else:
                self.mmv_shader_mgl.textures[index]["texture"].release()

    # Close the window
    def close(self, *args, **kwargs):
        logging.info(f"[MMVShaderMGLPreprocessor.close] Window should close")
        self.window_should_close = True

    # Swap the window buffers, be careful if vsync is False and you have a heavy
    # shader, it will consume all of your GPU computation and will most likely freeze
    # the video
    def update_window(self):
        self.window.swap_buffers()
        self.intensity = self.intensity + (self.target_intensity - self.intensity) * 0.2

    # # Imgui functions

    def key_event(self, key, action, modifiers):
        debug_prefix = "[MMVShaderMGLPreprocessor.key_event]"
        self.imgui.key_event(key, action, modifiers)

        # Shift and control
        if key == 340: self.shift_pressed = bool(action)
        if key == 341: self.ctrl_pressed = bool(action)

        # "i" key pressed, reset target intensity
        if (key == 73) and (action == 1):
            logging.info(f"{debug_prefix} \"i\" key pressed [Set target intensity to 1]")
            self.target_intensity = 1

        # "r" key pressed, reload shaders
        if (key == 82) and (action == 1):
            logging.info(f"{debug_prefix} \"r\" key pressed [Reloading shaders]")
            self.mmv_shader_mgl._read_shaders_from_paths_again()

        # "s" key pressed, don't pipe pipeline
        if (key == 83) and (action == 1):
            logging.info(f"{debug_prefix} \"s\" key pressed [Freezing time and pipelines but resolution, zoom]")
            self.mmv_shader_mgl.freezed_pipeline = not self.mmv_shader_mgl.freezed_pipeline
            for index in self.mmv_shader_mgl.textures.keys():
                if self.mmv_shader_mgl.textures[index]["loader"] == "shader":
                    self.mmv_shader_mgl.textures[index]["shader_as_texture"].freezed_pipeline = self.mmv_shader_mgl.freezed_pipeline

        # "t" key pressed, reset time to zero
        if (key == 84) and (action == 1):
            logging.info(f"{debug_prefix} \"t\" key pressed [Set time to 0]")
            self.mmv_shader_mgl.pipeline["mmv_frame"] = 0
            self.mmv_shader_mgl.pipeline["mmv_time"] = 0

        # "z" key pressed, reset zoom
        if (key == 90) and (action == 1):
            logging.info(f"{debug_prefix} \"z\" key pressed [Set target zoom to 1]")
            self.target_zoom = 1

        # "x" key, reset drag
        if (key == 88) and (action == 1):
            logging.info(f"{debug_prefix} \"z\" key pressed [Set target drag to [0, 0]]")
            self.target_drag = np.array([0.0, 0.0])

    # Mouse position changed
    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)
        self.mmv_shader_mgl.pipeline["mmv_mouse"] = [x, y]

    # Mouse drag, add to pipeline drag
    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)

        # Add to the mmv_drag pipeline item the dx and dy multiplied by the square of the current zoom
        square_current_zoom = (self.mmv_shader_mgl.pipeline["mmv_zoom"] ** 2)
        
        # Add to target drag the dx, dy relative to current zoom and SSAA level
        self.target_drag += np.array([
            (dx * square_current_zoom) * self.mmv_shader_mgl.ssaa,
            (dy * square_current_zoom) * self.mmv_shader_mgl.ssaa,
        ])

    # Change SSAA
    def change_ssaa(self, value):
        debug_prefix = "[MMVShaderMGLPreprocessor.change_ssaa]"
        self.mmv_shader_mgl.ssaa = value
        self.mmv_shader_mgl._read_shaders_from_paths_again()
        logging.info(f"{debug_prefix} Changed SSAA to [{value}]")

    # Zoom in or out (usually)
    def mouse_scroll_event(self, x_offset, y_offset):
        debug_prefix = "[MMVShaderMGLPreprocessor.mouse_scroll_event]"

        if self.shift_pressed:
            self.target_intensity += y_offset / 10
            logging.info(f"{debug_prefix} Mouse scroll with shift Target Intensity: [{self.target_intensity}]")
        elif self.ctrl_pressed:
            change_to = self.mmv_shader_mgl.ssaa + ((y_offset / 20) * self.mmv_shader_mgl.ssaa)
            logging.info(f"{debug_prefix} Mouse scroll with shift change SSAA to: [{change_to}]")
            self.change_ssaa(change_to)
        else:
            logging.info(f"{debug_prefix} Mouse scroll without shift and ctrl Target Zoom: [{self.target_zoom}]")
            self.target_zoom -= (y_offset * 0.05) * self.target_zoom

        self.imgui.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)
    
    # Render the user interface
    def render_ui(self):

        # Test window
        imgui.new_frame()
        imgui.begin("Custom window", True)
        imgui.text("Bar")
        imgui.text_colored("Eggs", 0.2, 1., 0.)
        imgui.end()

        # Render
        imgui.render()
        self.imgui.render(imgui.get_draw_data())
