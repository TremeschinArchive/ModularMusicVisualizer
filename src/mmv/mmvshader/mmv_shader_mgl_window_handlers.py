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
from moderngl_window import resources
from datetime import datetime
from pathlib import Path
import multiprocessing
import moderngl_window
from PIL import Image
import numpy as np
import logging
import imgui
import math


class MMVShaderMGLWindowHandlers:
    INTENSITY_RESPONSIVENESS = 0.2
    ROTATION_RESPONSIVENESS = 0.2
    ZOOM_RESPONSIVENESS = 0.2
    DRAG_RESPONSIVENESS = 0.3
    DRAG_MOMENTUM = 0.6
    
    def __init__(self, mmv_shader_mgl):
        self.mmv_shader_mgl = mmv_shader_mgl
        
        # Mouse related controls
        self.target_drag = np.array([0.0, 0.0])
        self.target_intensity = 1
        self.target_rotation = 0
        self.target_zoom = 1

        # Multiplier on top of multiplier, configurable real time
        self.drag_momentum = np.array([0.0, 0.0])
        self.drag = np.array([0.0, 0.0])
        self.intensity = 1
        self.rotation = 0
        self.zoom = 1

        # Keys
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.alt_pressed = False

        # Mouse
        self.mouse_buttons_pressed = []
        self.mouse_exclusivity = False

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
            self.window.fbo.viewport = (0, 0, self.mmv_shader_mgl.width, self.mmv_shader_mgl.height)
            # self.window.set_default_viewport()

        # Set the icon
        if icon is not None:
            # Absolute path
            icon = Path(icon).resolve()
            resources.register_dir(icon.parent)
            self.window.set_icon(icon_path = icon.name)
        
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

            # Release Dynamic Shaders and update their target render
            if self.mmv_shader_mgl.textures[index].get("dynamic", False):
                target = self.mmv_shader_mgl.textures[index]["shader_as_texture"]
                target.texture.release()
                target.fbo.release()
                target._create_assing_texture_fbo_render_buffer(verbose = False)

        # Master shader has window and imgui
        if self.mmv_shader_mgl.master_shader:
            if not self.headless:
                self.imgui.resize(self.mmv_shader_mgl.width, self.mmv_shader_mgl.height)

            # Window viewport
            self.window.fbo.viewport = (0, 0, self.mmv_shader_mgl.width, self.mmv_shader_mgl.height)

    # Release everything
    def drop_textures(self):
        for index in self.mmv_shader_mgl.textures.keys():
            if "shader_as_texture" in self.mmv_shader_mgl.textures[index].keys():
                target = self.mmv_shader_mgl.textures[index]["shader_as_texture"]
                print(target.texture, target.fbo, target.vao)
                target.program.release()
                target.texture.release()
                target.fbo.release()
                target.vao.release()
            else:
                self.mmv_shader_mgl.textures[index]["texture"].release()

    # Close the window
    def close(self, *args, **kwargs):
        logging.info(f"[MMVShaderMGLWindowHandlers.close] Window should close")
        self.window_should_close = True

    # Swap the window buffers, be careful if vsync is False and you have a heavy
    # shader, it will consume all of your GPU computation and will most likely freeze
    # the video
    def update_window(self):
        self.window.swap_buffers()

        # Interpolate stuff
        self.intensity += (self.target_intensity - self.intensity) * MMVShaderMGLWindowHandlers.INTENSITY_RESPONSIVENESS
        self.rotation += (self.target_rotation - self.rotation) * MMVShaderMGLWindowHandlers.ROTATION_RESPONSIVENESS
        self.zoom += (self.target_zoom - self.zoom) * MMVShaderMGLWindowHandlers.ZOOM_RESPONSIVENESS
        self.drag += (self.target_drag - self.drag) * MMVShaderMGLWindowHandlers.DRAG_RESPONSIVENESS
        self.drag_momentum *= MMVShaderMGLWindowHandlers.DRAG_MOMENTUM

        # Drag momentum
        if not 1 in self.mouse_buttons_pressed:
            self.target_drag += self.drag_momentum

    # # Interactive events

    def key_event(self, key, action, modifiers):
        debug_prefix = "[MMVShaderMGLWindowHandlers.key_event]"
        self.imgui.key_event(key, action, modifiers)
        logging.info(f"{debug_prefix} Key [{key}] Action [{action}] Modifier [{modifiers}]")

        # Shift and control
        if key == 340: self.shift_pressed = bool(action)
        if key == 341: self.ctrl_pressed = bool(action)
        if key == 342: self.alt_pressed = bool(action)

        # "c" key pressed, reset target rotation
        if (key == 67) and (action == 1):
            logging.info(f"{debug_prefix} \"c\" key pressed [Set target rotation to 0]")
            self.target_rotation = 0

        # "e" key pressed, toggle mouse exclusive mode
        if (key == 69) and (action == 1):
            logging.info(f"{debug_prefix} \"e\" key pressed [Toggle mouse exclusive]")
            self.mouse_exclusivity = not self.mouse_exclusivity
            self.window.mouse_exclusivity = self.mouse_exclusivity

        # "f" key pressed, toggle fullscreen mode
        if (key == 70) and (action == 1):
            logging.info(f"{debug_prefix} \"f\" key pressed [Toggle fullscreen]")
            self.window.fullscreen = not self.window.fullscreen

        # "h" key pressed, toggle mouse visible
        if (key == 72) and (action == 1):
            logging.info(f"{debug_prefix} \"h\" key pressed [Toggle mouse hidden]")
            self.window.cursor = not self.window.cursor

        # "p" key pressed, screenshot
        if (key == 80) and (action == 1):
            m = self.mmv_shader_mgl # Lazy

            # Where to save
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            saveto = m.screenshots_dir / f"{now}.jpg"

            logging.info(f"{debug_prefix} \"r\" key pressed, taking screenshot, saving to [{saveto}]")

            # Get data ib the scree's size viewport
            size = (m.width, m.height)
            data = self.window.fbo.read( viewport = (0, 0, size[0], size[1]) )

            logging.info(f"{debug_prefix} [Resolution: {size}] [WxHx3: {size[0] * size[1] * 3}] [len(data): {len(data)}]")

            # Multiprocess save image to file so we don't lock
            def save_image_to_file(size, data, path):
                img = Image.frombytes('RGB', size, data, 'raw').transpose(Image.FLIP_TOP_BOTTOM)
                img.save(path, quality = 95)
            
            # Start the process
            multiprocessing.Process(target = save_image_to_file, args = (size, data, saveto)).start()

        # "q" key pressed, quit
        if (key == 81) and (action == 1):
            logging.info(f"{debug_prefix} \"r\" key pressed, quitting")
            self.window_should_close = True

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

        # "v" key pressed, reset target intensity
        if (key == 86) and (action == 1):
            logging.info(f"{debug_prefix} \"v\" key pressed [Set target intensity to 1]")
            self.target_intensity = 1

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

        # Drag if on mouse exclusivity
        if self.mouse_exclusivity:
            self.__apply_rotated_drag(dx = dx, dy = dy, howmuch = 0.5, inverse = True)

    # Apply drag with the target rotation (because dx and dy are relative to the window itself not the rendered contents)
    def __apply_rotated_drag(self, dx, dy, howmuch = 1, inverse = False):

        # Inverse drag? Feels more natural when mouse exclusivity is on
        inverse = -1 if inverse else 1

        # Add to the mmv_drag pipeline item the dx and dy multiplied by the square of the current zoom
        square_current_zoom = (self.mmv_shader_mgl.pipeline["mmv_zoom"] ** 2)

        # dx and dy on zoom and SSAA
        dx = (dx * square_current_zoom) * self.mmv_shader_mgl.ssaa
        dy = (dy * square_current_zoom) * self.mmv_shader_mgl.ssaa

        # Cosine and sine
        c = math.cos(math.radians(self.rotation))
        s = math.sin(math.radians(self.rotation))

        # mat2 rotation times the dx, dy vector
        drag_rotated = np.array([
            (dx * c) + (dy * -s),
            (dx * s) + (dy * c)
        ]) * howmuch * inverse

        # Add to target drag the dx, dy relative to current zoom and SSAA level
        self.target_drag += drag_rotated
        self.drag_momentum += drag_rotated
        
    # Mouse drag, add to pipeline drag
    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)

        if 1 in self.mouse_buttons_pressed:
            if self.shift_pressed:
                self.target_zoom += (dy / 1000) * self.target_zoom
            elif self.alt_pressed:
                self.target_rotation += dy / 20
            else:
                self.__apply_rotated_drag(dx = dx, dy = dy)

    # Change SSAA
    def change_ssaa(self, value):
        debug_prefix = "[MMVShaderMGLWindowHandlers.change_ssaa]"
        self.mmv_shader_mgl.ssaa = value
        self.mmv_shader_mgl._read_shaders_from_paths_again()
        logging.info(f"{debug_prefix} Changed SSAA to [{value}]")

    # Zoom in or out (usually)
    def mouse_scroll_event(self, x_offset, y_offset):
        debug_prefix = "[MMVShaderMGLWindowHandlers.mouse_scroll_event]"

        if self.shift_pressed:
            self.target_intensity += y_offset / 10
            logging.info(f"{debug_prefix} Mouse scroll with shift Target Intensity: [{self.target_intensity}]")
        elif self.ctrl_pressed:
            change_to = self.mmv_shader_mgl.ssaa + ((y_offset / 20) * self.mmv_shader_mgl.ssaa)
            logging.info(f"{debug_prefix} Mouse scroll with shift change SSAA to: [{change_to}]")
            self.change_ssaa(change_to)
        elif self.alt_pressed:
            self.target_rotation -= y_offset * 5
            logging.info(f"{debug_prefix} Mouse scroll with alt change target rotation to: [{self.target_rotation}]")
        else:
            logging.info(f"{debug_prefix} Mouse scroll without shift and ctrl Target Zoom: [{self.target_zoom}]")
            self.target_zoom -= (y_offset * 0.05) * self.target_zoom

        self.imgui.mouse_scroll_event(x_offset, y_offset)

    def mouse_press_event(self, x, y, button):
        debug_prefix = "[MMVShaderMGLWindowHandlers.mouse_press_event]"
        logging.info(f"{debug_prefix} Mouse press (x, y): [{x}, {y}] Button [{button}]")
        self.imgui.mouse_press_event(x, y, button)
        if not button in self.mouse_buttons_pressed: self.mouse_buttons_pressed.append(button)
        if not self.mouse_exclusivity: self.window.mouse_exclusivity = True

    def mouse_release_event(self, x, y, button):
        debug_prefix = "[MMVShaderMGLWindowHandlers.mouse_release_event]"
        logging.info(f"{debug_prefix} Mouse release (x, y): [{x}, {y}] Button [{button}]")
        self.imgui.mouse_release_event(x, y, button)
        if button in self.mouse_buttons_pressed: self.mouse_buttons_pressed.remove(button)
        if not self.mouse_exclusivity: self.window.mouse_exclusivity = False

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
