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
from mmv.common.cmn_persistent_dictionary import PersistentDictionary
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from moderngl_window.conf import settings
from moderngl_window import resources
import mmv.common.cmn_any_logger
from datetime import datetime
from pathlib import Path
import multiprocessing
import moderngl_window
from PIL import Image
import numpy as np
import moderngl
import logging
import imgui
import math
import uuid
import time
import gc


# Handler for messages that expire or doesn't
class OnScreenTextMessages:
    def __init__(self): self.contents = {}
    
    # Add some message to the messages list
    def add(self, message: str, expire: float, has_counter = True) -> None:
        logging.info(f"[OnScreenTextMessages] Add message: [{message}] [expire: {expire}]")
        self.contents[str(uuid.uuid4())] = {
            "message": message,
            "expire": time.time() + expire,
            "has_counter": has_counter}

        # Sort items chronologically
        self.contents = {k: v for k, v in sorted(self.contents.items(), key = lambda x: x[1]["expire"])}
    
    # Delete expired messages
    def next(self):
        expired_keys = []
        for key, item in self.contents.items():
            if time.time() > item["expire"]: expired_keys.append(key)
        for key in expired_keys: del self.contents[key]

    # Generator that yields messages to be shown
    def get_contents(self):
        self.next()

        # Process message, yield it
        for item in self.contents.values():
            message = ""
            if item["has_counter"]:
                message += f"[{item['expire'] - time.time():.1f}s] | "
            message += item["message"]
            yield message


class SombreroWindow:
    LINUX_GNOME_PIXEL_SAVER_EXTENSION_WORKAROUND = False

    # Defaults
    ACTION_MESSAGE_TIMEOUT = 2

    # Multipliers
    INTENSITY_RESPONSIVENESS = 0.2
    ROTATION_RESPONSIVENESS = 0.2
    ZOOM_RESPONSIVENESS = 0.2
    DRAG_RESPONSIVENESS = 0.3
    DRAG_MOMENTUM = 0.6

    DEVELOPER = True
    
    def __init__(self, sombrero):
        self.sombrero = sombrero
        
        # Mouse related controls
        self.target_drag = np.array([0.0, 0.0])
        self.target_intensity = 1
        self.target_rotation = 0
        self.target_zoom = 1
        self.is_dragging_mode = False
        self.is_dragging = False

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

        # Gui
        self.debug_mode = False
        
        # Actions
        self.do_playback = True

        self.messages = OnScreenTextMessages()

    # Which "mode" to render, window loader class, msaa, ssaa, vsync, force res?
    def configure(self, window_class = "glfw", msaa = 8, vsync = False, strict = False, icon = None):
        debug_prefix = "[SombreroWindow.configure]"

        logging.info(f"{debug_prefix} \"i\" Set window mode [window_class={window_class}] [msaa={msaa}] [vsync={vsync}] [strict={strict}] [icon={icon}]")

        # Get function arguments
        self.headless = window_class == "headless"
        self.strict = strict
        self.vsync = vsync
        self.msaa = msaa

        # Headless we disable vsync because we're rendering only..?
        # And also force aspect ratio just in case (strict option)
        if self.headless:
            self.show_gui = False
            self.strict = True
            self.vsync = False

            # Fixed aspect ratio
            settings.WINDOW["aspect_ratio"] = self.sombrero.width / self.sombrero.height
        else:
            # Aspect ratio can change (Imgui integration "fix")
            settings.WINDOW["aspect_ratio"] = None
            self.show_gui = True

        # Assign the function arguments
        settings.WINDOW["class"] = f"moderngl_window.context.{window_class}.Window"
        settings.WINDOW["vsync"] = self.vsync
        settings.WINDOW["title"] = "Sombrero Real Time"

        # Don't set target width, height otherwise this will always crash
        if (self.headless) or (not SombreroWindow.LINUX_GNOME_PIXEL_SAVER_EXTENSION_WORKAROUND):
            settings.WINDOW["size"] = (self.sombrero.width, self.sombrero.height)

        # Create the window
        self.window = moderngl_window.create_window_from_settings()

        # Make sure we render strictly into the resolution we asked
        if strict:
            self.window.fbo.viewport = (0, 0, self.sombrero.width, self.sombrero.height)

        # Set the icon, FIXME: TODO: Proper resources directory?
        if icon is not None:
            icon = Path(icon).resolve()
            resources.register_dir(icon.parent)
            self.window.set_icon(icon_path = icon.name)
        
        # The context we'll use is the one from the window
        self.gl_context = self.window.ctx
        self.sombrero.gl_context = self.gl_context
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
            self.imgui_io = imgui.get_io()
            self.imgui_io.ini_saving_rate = 1

        # self.window_resize(width = self.window.viewport[2], height = self.window.viewport[3])
        
    # [NOT HEADLESS] Window was resized, update the width and height so we render with the new config
    def window_resize(self, width, height):
        if hasattr(self, "strict") and self.strict: return

        # We need to do some sort of change of basis between drag numbers when we change resolutions because
        # drag itself is absolute, not related 
        self.target_drag *= np.array([width, height]) / np.array([self.sombrero.width, self.sombrero.height])
        self.drag = self.target_drag.copy()

        # Set width and height
        self.sombrero.width = int(width)
        self.sombrero.height = int(height)

        # Recursively call this function on every shader on textures dictionary
        for index in self.sombrero.contents.keys():
            if self.sombrero.contents[index]["loader"] == "shader":
                self.sombrero.contents[index]["shader_as_texture"].window_handlers.window_resize(
                    width = self.sombrero.width, height = self.sombrero.height
                )

        # Search for dynamic shaders and update them
        for index in self.sombrero.contents.keys():

            # Release Dynamic Shaders and update their target render
            if self.sombrero.contents[index].get("dynamic", False):
                target = self.sombrero.contents[index]["shader_as_texture"]
                target.texture.release()
                target.fbo.release()
                target._create_assing_texture_fbo_render_buffer(verbose = False)

        # Master shader has window and imgui
        if self.sombrero.master_shader:
            if not self.headless:
                self.imgui.resize(self.sombrero.width, self.sombrero.height)

            # Window viewport
            self.window.fbo.viewport = (0, 0, self.sombrero.width, self.sombrero.height)

    # Release everything
    def drop_textures(self):
        self.messages.add("Dropped textures", SombreroWindow.ACTION_MESSAGE_TIMEOUT)
        for index in self.sombrero.contents.keys():
            if "shader_as_texture" in self.sombrero.contents[index].keys():
                target = self.sombrero.contents[index]["shader_as_texture"]
                target.fullscreen_buffer.release()
                target.program.release()
                target.texture.release()
                target.fbo.release()
                target.vao.release()
            else:
                self.sombrero.contents[index]["texture"].release()

        # Delete items
        for index in list(self.sombrero.contents.keys()):
            del self.sombrero.contents[index]
            gc.collect()

    # Close the window
    def close(self, *args, **kwargs):
        logging.info(f"[SombreroWindow.close] Window should close")
        self.imgui_io.want_save_ini_setting = True
        self.window_should_close = True

    # Swap the window buffers, be careful if vsync is False and you have a heavy
    # shader, it will consume all of your GPU computation and will most likely freeze
    # the video
    def update_window(self):
        self.window.swap_buffers()

        # Interpolate stuff
        self.intensity += (self.target_intensity - self.intensity) * SombreroWindow.INTENSITY_RESPONSIVENESS
        self.rotation += (self.target_rotation - self.rotation) * SombreroWindow.ROTATION_RESPONSIVENESS
        self.zoom += (self.target_zoom - self.zoom) * SombreroWindow.ZOOM_RESPONSIVENESS
        self.drag += (self.target_drag - self.drag) * SombreroWindow.DRAG_RESPONSIVENESS
        self.drag_momentum *= SombreroWindow.DRAG_MOMENTUM

        # Drag momentum
        if not 1 in self.mouse_buttons_pressed:
            self.target_drag += self.drag_momentum

        # If we're still iterating towards target drag then we're dragging
        self.is_dragging = not np.allclose(self.target_drag, self.drag, rtol = 0.01)

    # # Interactive events

    def key_event(self, key, action, modifiers):
        debug_prefix = "[SombreroWindow.key_event]"
        self.imgui.key_event(key, action, modifiers)
        logging.info(f"{debug_prefix} Key [{key}] Action [{action}] Modifier [{modifiers}]")

        # "tab" key pressed, toggle gui
        if (key == 258) and (action == 1):
            logging.info(f"{debug_prefix} \"tab\" key pressed [Toggle gui]")
            self.show_gui = not self.show_gui
            self.messages.add(f"Toggle GUI {self.show_gui}", SombreroWindow.ACTION_MESSAGE_TIMEOUT)
            self.window.mouse_exclusivity = False

        # Shift and control
        if key == 340: self.shift_pressed = bool(action)
        if key == 341: self.ctrl_pressed = bool(action)
        if key == 342: self.alt_pressed = bool(action)

        if self.imgui_io.want_capture_mouse: return

        # "space" key pressed, toggle playback
        if (key == 32) and (action == 1):
            self.messages.add(f"{debug_prefix} (space) Toggle playback", SombreroWindow.ACTION_MESSAGE_TIMEOUT)
            self.do_playback = not self.do_playback

        # "d" key pressed, debug mode
        if (key == 68) and (action == 1):
            self.messages.add(f"{debug_prefix} (d) Toggle debug", SombreroWindow.ACTION_MESSAGE_TIMEOUT)
            self.debug_mode = not self.debug_mode
            
        # "c" key pressed, reset target rotation
        if (key == 67) and (action == 1):
            self.messages.add(f"{debug_prefix} (c) Reset rotation", SombreroWindow.ACTION_MESSAGE_TIMEOUT)

            # Target rotation to the nearest 360° multiple (current minus negative remainder if you think hard enough)
            self.target_rotation = self.target_rotation - (math.remainder(self.target_rotation, 360))

        # "e" key pressed, toggle mouse exclusive mode
        if (key == 69) and (action == 1):
            self.mouse_exclusivity = not self.mouse_exclusivity
            self.window.mouse_exclusivity = self.mouse_exclusivity
            self.messages.add(f"{debug_prefix} (e) Toggle mouse exclusivity [{self.mouse_exclusivity}", SombreroWindow.ACTION_MESSAGE_TIMEOUT)

        # "f" key pressed, toggle fullscreen mode
        if (key == 70) and (action == 1):
            self.window.fullscreen = not self.window.fullscreen
            self.messages.add(f"{debug_prefix} (f) Toggle fullscreen [{self.window.fullscreen}]", SombreroWindow.ACTION_MESSAGE_TIMEOUT)

        # "h" key pressed, toggle mouse visible
        if (key == 72) and (action == 1):
            self.window.cursor = not self.window.cursor
            self.messages.add(f"{debug_prefix} (h) Toggle Hide Mouse [{self.window.cursor}]", SombreroWindow.ACTION_MESSAGE_TIMEOUT)

        # "p" key pressed, screenshot
        if (key == 80) and (action == 1):
            m = self.sombrero # Lazy

            # Where to save
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            saveto = m.mmv_interface.screenshots_dir / f"{now}.jpg"

            self.messages.add(f"{debug_prefix} (p) Screenshot save [{self.saveto}]", SombreroWindow.ACTION_MESSAGE_TIMEOUT * 4)

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
            logging.info(f"{debug_prefix} \"q\" key pressed, quitting")
            self.window_should_close = True

        # "r" key pressed, reload shaders
        if (key == 82) and (action == 1):
            self.sombrero._read_shaders_from_paths_again()
            self.messages.add(f"{debug_prefix} (r) Reloading shaders..", SombreroWindow.ACTION_MESSAGE_TIMEOUT)

        # "s" key pressed, don't pipe pipeline
        if (key == 83) and (action == 1):
            self.sombrero.freezed_pipeline = not self.sombrero.freezed_pipeline
            self.messages.add(f"{debug_prefix} (s) Freeze time [{self.sombrero.freezed_pipeline}]", SombreroWindow.ACTION_MESSAGE_TIMEOUT)
            for index in self.sombrero.contents.keys():
                if self.sombrero.contents[index]["loader"] == "shader":
                    self.sombrero.contents[index]["shader_as_texture"].freezed_pipeline = self.sombrero.freezed_pipeline

        # "t" key pressed, reset time to zero
        if (key == 84) and (action == 1):
            self.sombrero.pipeline["mFrame"] = 0
            self.sombrero.pipeline["mTime"] = 0
            self.messages.add(f"{debug_prefix} (t) Set time to zero", SombreroWindow.ACTION_MESSAGE_TIMEOUT)

        # "v" key pressed, reset target intensity
        if (key == 86) and (action == 1):
            self.messages.add(f"{debug_prefix} (v) Reset intensity to 1", SombreroWindow.ACTION_MESSAGE_TIMEOUT)
            self.target_intensity = 1

        # "z" key pressed, reset zoom
        if (key == 90) and (action == 1):
            self.messages.add(f"{debug_prefix} (z) Reset zoom to 1", SombreroWindow.ACTION_MESSAGE_TIMEOUT)
            self.target_zoom = 1

        # "x" key, reset drag
        if (key == 88) and (action == 1):
            self.messages.add(f"{debug_prefix} (x) Reset drag", SombreroWindow.ACTION_MESSAGE_TIMEOUT)
            self.target_drag = np.array([0.0, 0.0])

    # Mouse position changed
    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)
        self.sombrero.pipeline["mmv_mouse"] = [x, y]
        if self.imgui_io.want_capture_mouse: return

        # Drag if on mouse exclusivity
        if self.mouse_exclusivity:
            if self.shift_pressed:
                self.target_zoom += (dy / 1000) * self.target_zoom
            elif self.alt_pressed:
                self.target_rotation -= dy / 20
            else:
                self.__apply_rotated_drag(dx = dx, dy = dy, howmuch = 0.5, inverse = True)

    # Apply drag with the target rotation (because dx and dy are relative to the window itself not the rendered contents)
    def __apply_rotated_drag(self, dx, dy, howmuch = 1, inverse = False):

        # Inverse drag? Feels more natural when mouse exclusivity is on
        inverse = -1 if inverse else 1

        # Add to the mmv_drag pipeline item the dx and dy multiplied by the square of the current zoom
        square_current_zoom = (self.sombrero.pipeline["mZoom"] ** 2)

        # dx and dy on zoom and SSAA
        dx = (dx * square_current_zoom) * self.sombrero.ssaa
        dy = (dy * square_current_zoom) * self.sombrero.ssaa
        dx *= self.sombrero.width / self.sombrero.height

        # Cosine and sine
        c = math.cos(math.radians(-self.rotation))
        s = math.sin(math.radians(-self.rotation))

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
        if self.imgui_io.want_capture_mouse: return

        if 1 in self.mouse_buttons_pressed:
            self.is_dragging_mode = True

            if self.shift_pressed:
                self.target_zoom += (dy / 1000) * self.target_zoom
            elif self.alt_pressed:
                self.target_rotation += dy / 20
            else:
                self.__apply_rotated_drag(dx = dx, dy = dy, inverse = True)

    # Change SSAA
    def change_ssaa(self, value):
        debug_prefix = "[SombreroWindow.change_ssaa]"
        self.sombrero.ssaa = value
        self.sombrero._read_shaders_from_paths_again()
        logging.info(f"{debug_prefix} Changed SSAA to [{value}]")

    # Zoom in or out (usually)
    def mouse_scroll_event(self, x_offset, y_offset):
        debug_prefix = "[SombreroWindow.mouse_scroll_event]"
        if self.imgui_io.want_capture_mouse: return

        if self.shift_pressed:
            self.target_intensity += y_offset / 10
            logging.info(f"{debug_prefix} Mouse scroll with shift Target Intensity: [{self.target_intensity}]")
        elif self.ctrl_pressed and (not self.is_dragging_mode):
            change_to = self.sombrero.ssaa + ((y_offset / 20) * self.sombrero.ssaa)
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
        debug_prefix = "[SombreroWindow.mouse_press_event]"
        logging.info(f"{debug_prefix} Mouse press (x, y): [{x}, {y}] Button [{button}]")
        self.imgui.mouse_press_event(x, y, button)
        if self.imgui_io.want_capture_mouse: return
        if not button in self.mouse_buttons_pressed: self.mouse_buttons_pressed.append(button)
        if not self.mouse_exclusivity: self.window.mouse_exclusivity = True

    def mouse_release_event(self, x, y, button):
        debug_prefix = "[SombreroWindow.mouse_release_event]"
        logging.info(f"{debug_prefix} Mouse release (x, y): [{x}, {y}] Button [{button}]")
        self.imgui.mouse_release_event(x, y, button)
        self.is_dragging_mode = False
        if self.imgui_io.want_capture_mouse: return
        if button in self.mouse_buttons_pressed: self.mouse_buttons_pressed.remove(button)
        if not self.mouse_exclusivity: self.window.mouse_exclusivity = False

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)
    
    # Render the user interface
    def render_ui(self):
        imgui.new_frame()

        # # # Info Window

        imgui.set_next_window_position(0, 0, imgui.ONCE)
        imgui.set_next_window_bg_alpha(0.5)
        imgui.begin("Info Window", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE)

        # Render related

        imgui.text_colored("Render", 1, 0, 0)
        imgui.text(f"SSAA:       [{self.sombrero.ssaa:.3f}]")
        imgui.text(f"Resolution: [{int(self.sombrero.width)}, {int(self.sombrero.height)}] => [{int(self.sombrero.width*self.sombrero.ssaa)}, {int(self.sombrero.height*self.sombrero.ssaa)}]")

        # Coordinates, attributes

        imgui.text_colored("Coordinates, attributes", 1, 0, 0)
        imgui.text(f"(x, y):    [{self.drag[0]:.3f}, {self.drag[1]:.3f}] => [{self.target_drag[0]:.3f}, {self.target_drag[1]:.3f}]")
        imgui.text(f"Intensity: [{self.intensity:.2f}] => [{self.target_intensity:.2f}]")
        imgui.text(f"Zoom:      [{self.zoom:.5f}x] => [{self.target_zoom:.5f}x]")
        imgui.text(f"Rotation:  [{self.rotation:.3f}°] => [{self.target_rotation:.3f}°]")
        dock_y = imgui.get_window_height()
        imgui.end()

        # # # Messages box

        # Do have at least some message?
        messages = [m for m in self.messages.get_contents()]
        if len(messages) > 0: imgui.set_next_window_bg_alpha(0.2)
        else: imgui.set_next_window_bg_alpha(0)
        
        # Dock window
        imgui.set_next_window_position(0, dock_y)

        # Yes long line, but it's just setting stuff to no title bar, resize, moving
        imgui.begin("Messages", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_SAVED_SETTINGS | imgui.WINDOW_NO_INPUTS)

        # Add messages to the window
        for message in messages: imgui.text(message)
        imgui.end()

        # # # Render

        imgui.render()
        self.imgui.render(imgui.get_draw_data())
  
