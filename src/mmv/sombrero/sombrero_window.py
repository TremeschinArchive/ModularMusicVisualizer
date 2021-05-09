"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Window utilities, functions for SombreroMGL

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

sin = math.sin
cos = math.cos

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


class FrameTimesCounter:
    def __init__(self, fps = 60, plot_seconds = 2, history = 30):
        self.fps, self.plot_seconds, self.history = fps, plot_seconds, history
        self.last = time.time()
        self.counter = 0
        self.plot_fps = 60  # Otherwise too much info
        self.clear()
    
    # Create or reset the framtimes array
    def clear(self):
        self.frametimes = np.zeros((self.plot_fps * self.history), dtype = np.float32)
        self.last = time.time()
        self.first_time = True
    
    # Update counters
    def next(self):
        if not self.first_time:
            self.frametimes[self.counter % self.frametimes.shape[0]] = time.time() - self.last
        self.first_time = False
        self.last = time.time()
        self.counter += 1

    # Get dictionary with info
    def get_info(self):

        # Cut array in wrap mode, basically where we are minus the plot_seconds target
        plot_seconds_frametimes = self.frametimes.take(range(self.counter - (self.plot_seconds * self.plot_fps), self.counter), mode = "wrap")
        plot_seconds_frametimes_no_zeros = plot_seconds_frametimes[plot_seconds_frametimes != 0]

        # Simple average, doesn't tel much
        avg = np.mean(plot_seconds_frametimes_no_zeros)

        # Ignore zero entries, sort for getting 1% and .1%
        frametimes = self.frametimes[self.frametimes != 0]
        frametimes = list(reversed(list(sorted(frametimes))))
  
        return {
            "frametimes": plot_seconds_frametimes, "average": avg,
            "min": min(plot_seconds_frametimes_no_zeros, default = 1),
            "max": max(plot_seconds_frametimes_no_zeros, default = 1),
            "1%": np.mean(frametimes[0 : max(int(len(frametimes) * .01), 1)]),
            "0.1%": np.mean(frametimes[0 : max(int(len(frametimes) * .001), 1)]),
        }

def clamp(value, minimum, maximum): return max(minimum, min(value, maximum))

class SombreroWindow:
    LINUX_GNOME_PIXEL_SAVER_EXTENSION_WORKAROUND = False

    def __init__(self, sombrero):
        self.sombrero = sombrero
        print(self.sombrero.config["window"])
        self.ACTION_MESSAGE_TIMEOUT = self.sombrero.config["window"]["action_message_timeout"]
        
        # Mouse related controls
        self.target_drag = np.array([0.0, 0.0])
        self.target_intensity = 1
        self.target_uv_rotation = 0
        self.target_zoom = 1
        self.is_dragging_mode = False
        self.is_dragging = False

        # Multiplier on top of multiplier, configurable real time
        self.drag_momentum = np.array([0.0, 0.0])
        self.drag = np.array([0.0, 0.0])
        self.intensity = 1
        self.uv_rotation = 0
        self.zoom = 1

        # Keys
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.alt_pressed = False

        # Mouse
        self.mouse_buttons_pressed = []

        # Gui
        self.messages = OnScreenTextMessages()
        self.debug_mode = False

        # Actions
        self.playback_stopped = False
        self.target_time_factor = 1
        self.time_factor = 0
        self.keyboard_mode = 2

        # # 3D Stuff
        self.ThreeD_camera_pos = np.array([0, 0, 0], dtype = np.float32)
        self.ThreeD_target_camera_pos = np.array([0, 0, 0], dtype = np.float32)
        self.ThreeD_want_to_walk_unit_vector = np.array([0, 0, 0], dtype = np.float32)
        self.ThreeD_camera_pointing = np.array([0, 0, 0], dtype = np.float32)
        self.ThreeD_inclination = math.pi / 2
        self.ThreeD_target_inclination = math.pi / 2
        self.ThreeD_azimuth = 0
        self.ThreeD_target_azimuth = 0
        self.ThreeD_radius = 0
        self.ThreeD_target_radius = 0
        self.ThreeD_walk_speed = 1
        self.ThreeD_target_FOV = 1
        self.ThreeD_FOV = 1

    # Which "mode" to render, window loader class, msaa, ssaa, vsync, force res?
    def create(self, window_class = "glfw", msaa = 8, vsync = False, strict = False, icon = None):
        debug_prefix = "[SombreroWindow.create]"

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

        # Frame Rate
        self.framerate = FrameTimesCounter(fps = self.sombrero.fps)

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
            if not self.headless: self.imgui.resize(self.sombrero.width, self.sombrero.height)

            # Window viewport
            self.window.fbo.viewport = (0, 0, self.sombrero.width, self.sombrero.height)

    # Close the window
    def close(self, *args, **kwargs):
        logging.info(f"[SombreroWindow.close] Window should close")
        self.window_should_close = True

    # Swap the window buffers, be careful if vsync is False and you have a heavy
    # shader, it will consume all of your GPU computation and will most likely freeze
    # the video
    def update_window(self):
        self.window.swap_buffers()
        fix = self.sombrero._fix_ratio_due_fps
        cfg = self.sombrero.config["window"]

        # Interpolate stuff
        self.intensity += (self.target_intensity - self.intensity) * fix(cfg["intensity_responsiveness"]) 
        self.uv_rotation += (self.target_uv_rotation - self.uv_rotation) * fix(cfg["rotation_responsiveness"])
        self.zoom += (self.target_zoom - self.zoom) * fix(cfg["zoom_responsiveness"])
        self.drag += (self.target_drag - self.drag) * fix(cfg["drag_responsiveness"])
        self.drag_momentum *= cfg["drag_momentum"]

        self.time_factor += \
            ( (int(not self.playback_stopped) * int(not self.sombrero.freezed_pipeline) * self.target_time_factor) \
            - self.time_factor) * fix(cfg["time_responsiveness"]) 

        # 3D smooth interpolation
        self.ThreeD_azimuth += (self.ThreeD_target_azimuth - self.ThreeD_azimuth) * fix(cfg["3d"]["rotate_responsiveness"])
        self.ThreeD_inclination += (self.ThreeD_target_inclination - self.ThreeD_inclination) * fix(cfg["3d"]["rotate_responsiveness"])
        self.ThreeD_camera_pos += (self.ThreeD_target_camera_pos - self.ThreeD_camera_pos) * fix(cfg["3d"]["walk_responsiveness"])
        self.ThreeD_FOV += (self.ThreeD_target_FOV - self.ThreeD_FOV) * fix(cfg["3d"]["zoom_responsiveness"])
        self.walk_3d()

        # Drag momentum
        if not 1 in self.mouse_buttons_pressed: self.target_drag += self.drag_momentum

        # If we're still iterating towards target drag then we're dragging
        self.is_dragging = not np.allclose(self.target_drag, self.drag, rtol = 0.003)

    # # Interactive events

    # Walk in current pointing 3D directions
    def walk_3d(self):
        # Current spherical coordinates and (where) Want to Walk (WW)
        t, p, r = self.ThreeD_inclination, self.ThreeD_azimuth, self.ThreeD_radius
        ww = self.ThreeD_want_to_walk_unit_vector

        # Yes, Y and Z are swapped, think of Minecraft where the vertical is the Y axis
        # this is because screen's UV are already XY so the depth is Z, also called non surprisingly z-depth

        # Unit vectors on where we are, spherical coordinates
        rhat = ww[0] * np.array([sin(t)*cos(p), cos(t), sin(t)*sin(p)])
        phat = ww[1] * np.array([-sin(p), 0, cos(p)])
        that = ww[2] * np.array([cos(t)*cos(p), -sin(t), cos(t)*sin(p)])

        # Where camera want to go
        self.ThreeD_target_camera_pos += \
            (rhat + that + phat) * (self.ThreeD_walk_speed/20.0) \
            * (int(self.shift_pressed) + 1)
        self.ThreeD_camera_pointing = np.array([cos(p)*sin(t), cos(t), sin(p)*sin(t)])

    def key_event(self, key, action, modifiers):
        debug_prefix = "[SombreroWindow.key_event]"
        self.imgui.key_event(key, action, modifiers)
        logging.info(f"{debug_prefix} Key [{key}] Action [{action}] Modifier [{modifiers}]")

        # "tab" key pressed, toggle gui
        if (key == 258) and (action == 1):
            self.show_gui = not self.show_gui
            self.messages.add(f"(TAB) Toggle GUI [{self.show_gui}]", self.ACTION_MESSAGE_TIMEOUT)
            self.window.mouse_exclusivity = False
            self.framerate.clear()

        if self.imgui_io.want_capture_keyboard: return

        # Shift and control
        if key == 340: self.shift_pressed = bool(action)
        if key == 341: self.ctrl_pressed = bool(action)
        if key == 342: self.alt_pressed = bool(action)

        if (key == 50) and (action == 1):
            self.messages.add(f"{debug_prefix} (2) Set 2D (default) mode", self.ACTION_MESSAGE_TIMEOUT)
            self.window.mouse_exclusivity = False
            self.keyboard_mode = 2

        if (key == 51) and (action == 1):
            self.messages.add(f"{debug_prefix} (3) Set 3D mode", self.ACTION_MESSAGE_TIMEOUT)
            self.ThreeD_want_to_walk_unit_vector = np.array([0, 0, 0])
            self.window.mouse_exclusivity = True
            self.keyboard_mode = 3

        # # # # Specific

        # 2D mode
        if self.keyboard_mode == 2:

            # Target rotation to the nearest 360° multiple (current minus negative remainder if you think hard enough)
            if (key == 67) and (action == 1):
                self.messages.add(f"{debug_prefix} [2D] (c) Reset rotation to [0°]", self.ACTION_MESSAGE_TIMEOUT)
                self.target_uv_rotation = self.target_uv_rotation - (math.remainder(self.target_uv_rotation, 360))

            if (key == 90) and (action == 1):
                self.messages.add(f"{debug_prefix} [2D] (z) Reset zoom to [1x]", self.ACTION_MESSAGE_TIMEOUT)
                self.target_zoom = 1

            if (key == 88) and (action == 1):
                self.messages.add(f"{debug_prefix} [2D] (x) Reset drag to [0, 0]", self.ACTION_MESSAGE_TIMEOUT)
                self.target_drag = np.array([0.0, 0.0])
            
            if (key == 32) and (action == 1):
                self.playback_stopped = not self.playback_stopped
                self.messages.add(f"{debug_prefix} [2D] (space) Toggle playback [{self.playback_stopped}]", self.ACTION_MESSAGE_TIMEOUT)

        # 3D mode
        if self.keyboard_mode == 3:
            if action in [0, 1]:
                if (key == 87):  self.ThreeD_want_to_walk_unit_vector[0] =  action  # W
                if (key == 83):  self.ThreeD_want_to_walk_unit_vector[0] = -action  # A 
                if (key == 65):  self.ThreeD_want_to_walk_unit_vector[1] = -action  # S
                if (key == 68):  self.ThreeD_want_to_walk_unit_vector[1] =  action  # D
                if (key == 32):  self.ThreeD_want_to_walk_unit_vector[2] = -action  # Space
                if (key == 340): self.ThreeD_want_to_walk_unit_vector[2] =  action  # Shift
            
            if (key == 67) and (action == 1):
                self.messages.add(f"{debug_prefix} [3D] (c) Reset azimuth to [0°]", self.ACTION_MESSAGE_TIMEOUT)
                self.ThreeD_target_azimuth = self.ThreeD_target_azimuth - (math.remainder(self.ThreeD_target_azimuth, 360))

            if (key == 86) and (action == 1):
                self.messages.add(f"{debug_prefix} [3D] (v) Reset inclination to [90°]", self.ACTION_MESSAGE_TIMEOUT)
                self.ThreeD_target_inclination = self.ThreeD_target_inclination - (math.remainder(self.ThreeD_target_inclination, 180)) + math.pi/2

            if (key == 88) and (action == 1):
                self.messages.add(f"{debug_prefix} [3D] (x) Reset camera to (0, 0, 0)", self.ACTION_MESSAGE_TIMEOUT)
                self.ThreeD_target_camera_pos = np.array([0.0, 0.0, 0.0], dtype = np.float32)

            if (key == 90) and (action == 1):
                self.messages.add(f"{debug_prefix} [3D] (z) Reset FOV to [1x]", self.ACTION_MESSAGE_TIMEOUT)
                self.ThreeD_target_FOV = 1

                
        # # # # Generic
        
        # Escape
        if (key == 256) and (action == 1) and (self.keyboard_mode == 3):
            self.window_should_close = True

        # TODO change to i
        # if (key == 86) and (action == 1):
            # self.messages.add(f"{debug_prefix} (i) Reset intensity to [1]", self.ACTION_MESSAGE_TIMEOUT)
            # self.target_intensity = 1

        if (key == 44) and (action == 1):
            if self.shift_pressed:
                self.target_time_factor -= 0.01
                self.messages.add(f"{debug_prefix} (,) Playback speed [-0.1] [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)
            else:
                self.target_time_factor -= 0.1
                self.messages.add(f"{debug_prefix} (.) Playback speed [-0.1] [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)

        if (key == 46) and (action == 1):
            if self.shift_pressed:
                self.target_time_factor += 0.01
                self.messages.add(f"{debug_prefix} (,) Playback speed [+0.1] [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)
            else:
                self.target_time_factor += 0.1
                self.messages.add(f"{debug_prefix} (.) Playback speed [+0.1] [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)

        if (key == 47) and (action == 1):
                self.target_time_factor *= -1
                self.messages.add(f"{debug_prefix} (;) Reverse playback speed [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)
        
        if (key == 70) and (action == 1):
            self.window.fullscreen = not self.window.fullscreen
            self.messages.add(f"{debug_prefix} (f) Toggle fullscreen [{self.window.fullscreen}]", self.ACTION_MESSAGE_TIMEOUT)

        if (key == 72) and (action == 1):
            self.window.cursor = not self.window.cursor
            self.messages.add(f"{debug_prefix} (h) Toggle Hide Mouse [{self.window.cursor}]", self.ACTION_MESSAGE_TIMEOUT)
      
        if (key == 79) and (action == 1):
            self.sombrero.freezed_pipeline = not self.sombrero.freezed_pipeline
            self.messages.add(f"{debug_prefix} (o) Freeze pipeline [{self.sombrero.freezed_pipeline}]", self.ACTION_MESSAGE_TIMEOUT)
            self.time_factor = 0
            for index in self.sombrero.contents.keys():
                if self.sombrero.contents[index]["loader"] == "shader":
                    self.sombrero.contents[index]["shader_as_texture"].freezed_pipeline = self.sombrero.freezed_pipeline

        if (key == 82) and (action == 1):
            self.messages.add(f"{debug_prefix} (r) Reloading shaders..", self.ACTION_MESSAGE_TIMEOUT)
            self.sombrero._want_to_reload = True
  
        if (key == 84) and (action == 1):
            self.sombrero.pipeline["mFrame"] = 0
            self.sombrero.pipeline["mTime"] = 0
            self.messages.add(f"{debug_prefix} (t) Set time to [0s]", self.ACTION_MESSAGE_TIMEOUT)

        if (key == 89) and (action == 1):
            self.messages.add(f"{debug_prefix} (y) Toggle debug", self.ACTION_MESSAGE_TIMEOUT)
            self.debug_mode = not self.debug_mode

        # "p" key pressed, screenshot
        if (key == 80) and (action == 1):
            m = self.sombrero # Lazy

            # Where to save
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            saveto = m.mmv_interface.screenshots_dir / f"{now}.jpg"
            self.messages.add(f"{debug_prefix} (p) Screenshot save [{saveto}]", self.ACTION_MESSAGE_TIMEOUT * 4)

            old = self.show_gui  # Did we have GUI enabled previously?
            self.show_gui = False  # Disable for screenshot
            self.sombrero._render()  # Update screen so we actually remove the GUI
            self.show_gui = old  # Revert
      
            # Get data ib the scree's size viewport
            size = (m.width, m.height)
            data = self.window.fbo.read( viewport = (0, 0, size[0], size[1]) )
            logging.info(f"{debug_prefix} [Resolution: {size}] [WxHx3: {size[0] * size[1] * 3}] [len(data): {len(data)}]")

            # Multiprocessing save image to file so we don't lock
            def save_image_to_file(size, data, path):
                img = Image.frombytes('RGB', size, data, 'raw').transpose(Image.FLIP_TOP_BOTTOM)
                img.save(path, quality = 95)
            multiprocessing.Process(target = save_image_to_file, args = (size, data, saveto)).start()

    # Mouse position changed
    def mouse_position_event(self, x, y, dx, dy):
        self.sombrero.pipeline["mMouse"] = np.array([x, y])
        if self.imgui_io.want_capture_mouse: return

        # Drag if on mouse exclusivity
        if self.keyboard_mode == 3:
            cfg = self.sombrero.config["window"]["3d"]
            mouse_sensitivity = cfg["mouse_sensitivity"]
            self.ThreeD_target_azimuth += (mouse_sensitivity * dx * self.ThreeD_target_FOV) / 400
            self.ThreeD_target_inclination += (mouse_sensitivity * dy * self.ThreeD_target_FOV) / 400

    # Apply drag with the target rotation (because dx and dy are relative to the window itself not the rendered contents)
    def __apply_rotated_drag(self, dx, dy, howmuch = 1, inverse = False):

        # Inverse drag? Feels more natural when mouse exclusivity is on
        inverse = -1 if inverse else 1

        # Add to the mmv_drag pipeline item the dx and dy multiplied by the square of the current zoom
        square_current_zoom = (self.sombrero.pipeline["mZoom"] ** 2)

        # dx and dy on zoom and SSAA
        dx = (dx * square_current_zoom) * self.sombrero.ssaa
        dy = (dy * square_current_zoom) * self.sombrero.ssaa

        # Cosine and sine
        c = cos(self.uv_rotation)
        s = sin(self.uv_rotation)

        # mat2 rotation times the dx, dy vector
        drag_rotated = np.array([
            (dx * c) + (dy * -s),
            (dx * s) + (dy * c)
        ]) * howmuch * inverse

        # Normalize dx step due aspect ratio
        drag_rotated[0] *= self.sombrero.width / self.sombrero.height 

        # Add to target drag the dx, dy relative to current zoom and SSAA level
        self.target_drag += drag_rotated
        self.drag_momentum += drag_rotated
        
    # Mouse drag, add to pipeline drag
    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)
        if self.imgui_io.want_capture_mouse: return

        if not self.keyboard_mode == 3:
            if 1 in self.mouse_buttons_pressed:
                self.is_dragging_mode = True
                if self.shift_pressed: self.target_zoom += (dy / 1000) * self.target_zoom
                elif self.alt_pressed: self.target_uv_rotation += (dy / 80) / (2*math.pi)
                else: self.__apply_rotated_drag(dx = dx, dy = dy, inverse = True)

            if 2 in self.mouse_buttons_pressed:
                if self.shift_pressed: self.sombrero.pipeline["mFrame"] -= (dy * self.sombrero.fps) / 200
                elif self.alt_pressed: self.target_time_factor -= dy / 80
                else: self.sombrero.pipeline["mFrame"] -= (dy * self.sombrero.fps) / 800

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

        if self.keyboard_mode == 3:
            if self.shift_pressed:
                self.ThreeD_target_FOV -= (y_offset * 0.05) * self.ThreeD_target_FOV
            else:
                self.ThreeD_walk_speed += (y_offset * 0.05) * self.ThreeD_walk_speed
        
        else:
            if self.shift_pressed:
                self.target_intensity += y_offset / 10
                logging.info(f"{debug_prefix} Mouse scroll with shift Target Intensity: [{self.target_intensity}]")
            elif self.ctrl_pressed and (not self.is_dragging_mode):
                change_to = self.sombrero.ssaa + ((y_offset / 20) * self.sombrero.ssaa)
                logging.info(f"{debug_prefix} Mouse scroll with shift change SSAA to: [{change_to}]")
                self.change_ssaa(change_to)
            elif self.alt_pressed:
                self.target_uv_rotation -= y_offset * 5
                logging.info(f"{debug_prefix} Mouse scroll with alt change target rotation to: [{self.target_uv_rotation}]")
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
        if not self.keyboard_mode == 3: self.window.mouse_exclusivity = True

    def mouse_release_event(self, x, y, button):
        debug_prefix = "[SombreroWindow.mouse_release_event]"
        logging.info(f"{debug_prefix} Mouse release (x, y): [{x}, {y}] Button [{button}]")
        self.imgui.mouse_release_event(x, y, button)
        self.is_dragging_mode = False
        if self.imgui_io.want_capture_mouse: return
        if button in self.mouse_buttons_pressed: self.mouse_buttons_pressed.remove(button)
        if not self.keyboard_mode == 3: self.window.mouse_exclusivity = False

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)
    

    # # # # GUI, somewhat intensive and weird code that can't be really simplified


    # Render the user interface
    def render_ui(self):
        imgui.new_frame()
        dock_y = 0
        imgui.push_style_var(imgui.STYLE_WINDOW_BORDERSIZE, 0.0)
        imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0)
        section_color = (0, 1, 0)

        # # # Info window

        if 1:
            imgui.set_next_window_position(0, dock_y)
            imgui.set_next_window_bg_alpha(0.5)
            imgui.begin(f"Info Window", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE)

            # Render related
            imgui.text_colored("Render", *section_color)
            imgui.separator()
            imgui.text(f"SSAA:       [{self.sombrero.ssaa:.3f}]")
            imgui.text(f"Resolution: [{int(self.sombrero.width)}, {int(self.sombrero.height)}] => [{int(self.sombrero.width*self.sombrero.ssaa)}, {int(self.sombrero.height*self.sombrero.ssaa)}]")

            # Coordinates, attributes
            imgui.separator()
            imgui.text_colored("Coordinates, attributes", *section_color)
            imgui.text(f"(x, y):    [{self.drag[0]:.3f}, {self.drag[1]:.3f}] => [{self.target_drag[0]:.3f}, {self.target_drag[1]:.3f}]")
            imgui.text(f"Intensity: [{self.intensity:.2f}] => [{self.target_intensity:.2f}]")
            imgui.text(f"Zoom:      [{self.zoom:.5f}x] => [{self.target_zoom:.5f}x]")
            imgui.text(f"UV Rotation:  [{math.degrees(self.uv_rotation):.3f}°] => [{math.degrees(self.target_uv_rotation):.3f}°]")

            # 3D
            imgui.separator()
            imgui.text_colored("3D Related", *section_color)
            imgui.text(f"Camera Pointing:  [{self.ThreeD_camera_pointing[0]:.2f}, {self.ThreeD_camera_pointing[1]:.2f}, {self.ThreeD_camera_pointing[2]:.2f}]")
            imgui.text(f"Camera (x, y, z): [{self.ThreeD_camera_pos[0]:.2f}, {self.ThreeD_camera_pos[1]:.2f}, {self.ThreeD_camera_pos[2]:.2f}]")
            imgui.text(f"Inclination:      [{math.degrees(self.ThreeD_inclination):.2f}°] => [{math.degrees(self.ThreeD_target_inclination):.2f}°]")
            imgui.text(f"Azimuth:          [{math.degrees(self.ThreeD_azimuth):.2f}°] => [{math.degrees(self.ThreeD_target_azimuth):.2f}°]")
            imgui.text(f"FOV:              [{self.ThreeD_FOV:.2f}] => [{self.ThreeD_target_FOV:.2f}]")
            imgui.text(f"Walk speed:       [{self.ThreeD_walk_speed:.2f}]")
            
            dock_y += imgui.get_window_height()
            imgui.end()

        # # # Basic render, config settings

        if 1:
            imgui.set_next_window_position(0, dock_y)
            imgui.set_next_window_bg_alpha(0.5)
            imgui.begin("Config Window", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE)
            
            # # FPS
            changed, value = imgui.input_int("Target FPS", self.sombrero.fps)
            if changed: self.sombrero.change_fps(value)

            # List of common fps
            for fps in [24, 30, 60, 90, 120, 144, 240]:
                changed = imgui.button(f"{fps}Hz")
                if fps != 240: imgui.same_line() # Same line until last value
                if changed: self.sombrero.change_fps(fps)
            imgui.separator()

            # # Time
            t = f"{self.sombrero.pipeline['mTime']:.1f}s"
            if not self.sombrero.freezed_pipeline: imgui.text_colored(f"Time [PLAYING] [{t}]", *section_color)
            else: imgui.text_colored(f"Time [FROZEN] [{t}]", 1, 0, 0)

            changed, value = imgui.slider_float("Multiplier", self.target_time_factor, min_value = -3, max_value = 3, power = 1)
            if changed:
                self.target_time_factor = value
                self.previous_time_factor = self.target_time_factor

            # # Time
            imgui.separator()

            # Quick
            for ratio in [-2, -1, -0.5, 0, 0.1, 0.25, 0.5, 1, 2]:
                changed = imgui.button(f"{ratio}x")
                if ratio != 2: imgui.same_line() # Same line until last value
                if changed:
                    self.target_time_factor = ratio
                    self.previous_time_factor = self.target_time_factor
                    self.sombrero.freezed_pipeline = False

            imgui.separator()
            dock_y += imgui.get_window_height()
            imgui.end()

        # # # Performance Window

        if 1:
            # Update framerates, get info
            self.framerate.next()
            info = self.framerate.get_info()

            imgui.set_next_window_position(0, dock_y)
            imgui.set_next_window_bg_alpha(0.5)
            imgui.begin("Performance", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE)
            imgui.text_colored(f"Frametimes [last {self.framerate.history:.2f}s]", *section_color)
            imgui.separator()
            precision = 2
            imgui.plot_lines(
                (
                    f"Average: [{1/info['average']:.{precision}f}fps]\n"
                    f"     1%: [{1/info['1%']:.{precision}f}fps]\n"
                    f"   0.1%: [{1/info['0.1%']:.{precision}f}fps]\n"
                    f"    Min: [{1/info['max']:.{precision}f}fps]\n"
                    f"    Max: [{1/info['min']:.{precision}f}fps]\n"
                ), info["frametimes"],
                scale_min = 0,
                graph_size = (0, 70)
            )
            imgui.separator()
            dock_y += imgui.get_window_height()
            imgui.end()

        # # # Messages window

        if 1:
            # Do have at least some message?
            messages = [m for m in self.messages.get_contents()]
            if len(messages) > 0: imgui.set_next_window_bg_alpha(0.2)
            else: imgui.set_next_window_bg_alpha(0)
            imgui.set_next_window_position(0, dock_y)

            # Yes long line, but it's just setting stuff to no title bar, resize, moving
            imgui.begin("Messages", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_SAVED_SETTINGS | imgui.WINDOW_NO_INPUTS)

            # Add messages to the window
            for message in messages: imgui.text(message)
            imgui.end()

        # # # Render
        imgui.pop_style_var(2)

        imgui.render()
        self.imgui.render(imgui.get_draw_data())
  
