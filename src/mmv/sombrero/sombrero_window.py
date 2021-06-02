"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Window utilities, functions for SombreroMGL
Heavy calculations on 2D coordinates, interactive contents and also 3D.

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
from mmv.sombrero.utils.sombrero_window_utils import FrameTimesCounter, OnScreenTextMessages
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from mmv.sombrero.modules.controller.joystick import Joysticks
from mmv.sombrero.modules.camera.camera_2d import Camera2D
from mmv.sombrero.modules.camera.camera_3d import Camera3D
from mmv.sombrero.utils.keyboard_keys import KeyboardKey
from mmv.sombrero.sombrero_context import RealTimeModes
from moderngl_window.conf import settings
from moderngl_window import resources
from datetime import datetime
from enum import Enum, auto
from dotmap import DotMap
from pathlib import Path
import multiprocessing
import moderngl_window
from PIL import Image
import numpy as np
import quaternion
import moderngl
import logging
import imgui
import math
import uuid
import time
import gc
import os

sin = math.sin
cos = math.cos

class SombreroWindow:

    def __init__(self, sombrero_mgl):
        self.sombrero_mgl = sombrero_mgl
        self.mmv_interface = self.sombrero_mgl.mmv_interface
        self.context = self.sombrero_mgl.context
        self.ACTION_MESSAGE_TIMEOUT = self.context.config["window"]["action_message_timeout"]
        
        # Modules
        self.messages = OnScreenTextMessages()
        self.context.camera3d = Camera3D(self)
        self.context.camera2d = Camera2D(self)
        self.context.joysticks = Joysticks(self)
        self.context.framerate = FrameTimesCounter(fps = self.context.fps)
        self.window_should_close = False

        # TODO move to context
        self.target_time_factor = 1

    def create(self):
        debug_prefix = "[SombreroWindow.create]"

        # Headless we disable vsync because we're rendering only..?
        # And also force aspect ratio just in case (strict option)
        if self.context.window_headless: settings.WINDOW["aspect_ratio"] = self.context.width / self.context.height
        else: settings.WINDOW["aspect_ratio"] = None

        # Assign the function arguments
        settings.WINDOW["class"] = f"moderngl_window.context.{self.context.window_class}.Window"
        settings.WINDOW["vsync"] = self.context.window_vsync
        settings.WINDOW["title"] = "Sombrero Real Time"

        # Don't set target width, height otherwise this will always crash
        if (self.context.window_headless) or (not self.context.LINUX_GNOME_PIXEL_SAVER_EXTENSION_WORKAROUND):
            settings.WINDOW["size"] = (self.context.width, self.context.height)

        # Create the window
        self.window = moderngl_window.create_window_from_settings()
        self.context.gl_context = self.window.ctx

        # Make sure we render strictly into the resolution we asked
        if self.context.window_strict: self.window.fbo.viewport = (0, 0, self.context.width, self.context.height)

        # Functions of the window if not headless
        if not self.context.window_headless:
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

    # [NOT HEADLESS] Window was resized, update the width and height so we render with the new config
    def window_resize(self, width, height):
        if hasattr(self, "strict") and self.strict: return

        # We need to do some sort of change of basis between drag numbers when we change resolutions because
        # drag itself is absolute, not related 
        self.context.camera2d.drag.set_target(
            self.context.camera2d.drag.value * (np.array([width, height]) / np.array([self.context.width, self.context.height]))
        )
        self.context.camera2d.drag._target_is_current_value()

        # Set width and height
        self.context.width = int(width)
        self.context.height = int(height)

        # for child in self.sombrero_mgl.children_sombrero_mgl():
        #     child.texture.release()
        #     child.fbo.release()
        #     child._create_assing_texture_fbo_render_buffer()

        # for child in self.sombrero_mgl.children_sombrero_mgl():
        #     child.window.window_resize(width, height)
        self.context.mmv_main.reload_shaders()

        # Master shader has window and imgui
        if self.sombrero_mgl.master_shader:
            if not self.context.window_headless: self.imgui.resize(self.context.width, self.context.height)
            self.window.fbo.viewport = (0, 0, self.context.width, self.context.height)
            self.sombrero_mgl._create_assing_texture_fbo_render_buffer()

    # Close the window
    def close(self, *args, **kwargs):
        logging.info(f"[SombreroWindow.close] Window should close")
        self.window_should_close = True

    # Swap the window buffers, be careful if vsync is False and you have a heavy
    # shader, it will consume all of your GPU computation and will most likely freeze
    # the video
    def update_window(self):
        self.window.swap_buffers()
        cfg = self.sombrero_mgl.config["window"]

        if not self.context.mode == self.context.ExecutionMode.Render:
            self.context.joysticks.next()
        if self.context.live_mode == RealTimeModes.Mode2D: self.context.camera2d.next()
        if self.context.live_mode == RealTimeModes.Mode3D: self.context.camera3d.next()

        # TODO: move to context
        # self.context.intensity += (self.target_intensity - self.context.intensity) * cfg["intensity_responsiveness"]
        # self.time_factor += \
        #     ( (int(not self.playback_stopped) * int(not self.context.freezed_pipeline) * self.target_time_factor) \
        #     - self.time_factor) * self.sombrero_mgl._fix_ratio_due_fps(cfg["time_responsiveness"]) 

    def key_event(self, key, action, modifiers):
        debug_prefix = "[SombreroWindow.key_event]"
        self.imgui.key_event(key, action, modifiers)
        logging.info(f"{debug_prefix} Key [{key}] Action [{action}] Modifier [{modifiers}]")

        # Shift and control
        if key == 340: self.context.shift_pressed = bool(action)
        if key == 341: self.context.ctrl_pressed = bool(action)
        if key == 342: self.context.alt_pressed = bool(action)
        
        # "tab" key pressed, toggle gui
        if (key == 258) and (action == 1):
            if self.context.shift_pressed:
                self.context.show_gui = not self.context.show_gui
                self.messages.add(f"(Shift + TAB) Toggle All GUI [{self.context.show_gui}]", self.ACTION_MESSAGE_TIMEOUT)
                self.context.framerate.clear()
            else:
                self.context.window_show_menu = not self.context.window_show_menu
                self.messages.add(f"(TAB) Toggle menu GUI [{self.context.window_show_menu}]", self.ACTION_MESSAGE_TIMEOUT)
                if self.context.window_show_menu: self.window.mouse_exclusivity = False
                else:
                    if self.context.live_mode == RealTimeModes.Mode3D: self.window.mouse_exclusivity = True

        if self.imgui_io.want_capture_keyboard: return

        if self.context.shift_pressed: pass

        elif self.context.ctrl_pressed:
            if (key == 49) and (action == 1):
                self.playback_stopped = not self.playback_stopped
                self.messages.add(f"{debug_prefix} (Ctrl 1) Toggle playback [{self.playback_stopped}]", self.ACTION_MESSAGE_TIMEOUT)
        else:
            if (key == KeyboardKey) and (action == 1):
                self.messages.add(f"{debug_prefix} (2) Set 2D (default) mode", self.ACTION_MESSAGE_TIMEOUT)
                self.window.mouse_exclusivity = False
                self.context.live_mode = RealTimeModes.Mode2D
                self.context.window_show_menu = False

            if (key == 51) and (action == 1):
                self.messages.add(f"{debug_prefix} (3) Set 3D mode", self.ACTION_MESSAGE_TIMEOUT)
                self.ThreeD_want_to_walk_unit_vector = np.array([0, 0, 0])
                self.window.mouse_exclusivity = True
                self.context.live_mode = RealTimeModes.Mode3D
                self.context.window_show_menu = False

        # Mode
        if self.context.live_mode == RealTimeModes.Mode2D:
            self.context.camera2d.key_event(key = key, action = action, modifiers = modifiers)
        if self.context.live_mode == RealTimeModes.Mode3D:
            self.context.camera3d.key_event(key = key, action = action, modifiers = modifiers)
                
        # # # # Generic
        
        # Escape
        if (key == 256) and (action == 1) and (self.context.live_mode == RealTimeModes.Mode3D):
            self.window_should_close = True

        if (key == 44) and (action == 1):
            if self.context.shift_pressed:
                self.target_time_factor -= 0.01
                self.messages.add(f"{debug_prefix} (,) Playback speed [-0.1] [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)
            else:
                self.target_time_factor -= 0.1
                self.messages.add(f"{debug_prefix} (.) Playback speed [-0.1] [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)

        if (key == 46) and (action == 1):
            if self.context.shift_pressed:
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
            self.context.freezed_pipeline = not self.context.freezed_pipeline
            self.messages.add(f"{debug_prefix} (o) Freeze pipeline [{self.context.freezed_pipeline}]", self.ACTION_MESSAGE_TIMEOUT)
            self.time_factor = 0
            for index in self.sombrero_mgl.contents.keys():
                if self.sombrero_mgl.contents[index]["loader"] == "shader":
                    self.sombrero_mgl.contents[index]["shader_as_texture"].freezed_pipeline = self.context.freezed_pipeline

        if (key == 82) and (action == 1):
            self.messages.add(f"{debug_prefix} (r) Reloading shaders..", self.ACTION_MESSAGE_TIMEOUT)
            # TOOD remove want to reload
            self.context.mmv_main.reload_shaders()
            self.sombrero_mgl._want_to_reload = True
  
        if (key == 84) and (action == 1):
            self.sombrero_mgl.pipeline["mFrame"] = 0
            self.sombrero_mgl.pipeline["mTime"] = 0
            self.messages.add(f"{debug_prefix} (t) Set time to [0s]", self.ACTION_MESSAGE_TIMEOUT)

        if (key == 89) and (action == 1):
            self.messages.add(f"{debug_prefix} (y) Toggle debug", self.ACTION_MESSAGE_TIMEOUT)
            self.debug_mode = not self.debug_mode

        # "p" key pressed, screenshot
        if (key == 80) and (action == 1):

            # Where to save
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            saveto = self.mmv_interface.screenshots_dir / f"{now}.jpg"
            self.messages.add(f"{debug_prefix} (p) Screenshot save [{saveto}]", self.ACTION_MESSAGE_TIMEOUT * 4)

            old = self.context.show_gui  # Did we have GUI enabled previously?
            self.context.show_gui = False  # Disable for screenshot
            self.sombrero_mgl._render()  # Update screen so we actually remove the GUI
            self.context.show_gui = old  # Revert
      
            # Get data ib the scree's size viewport
            size = (self.context.width, self.context.height)
            data = self.window.fbo.read( viewport = (0, 0, size[0], size[1]) )
            logging.info(f"{debug_prefix} [Resolution: {size}] [WxHx3: {size[0] * size[1] * 3}] [len(data): {len(data)}]")

            # Multiprocessing save image to file so we don't lock
            def save_image_to_file(size, data, path):
                img = Image.frombytes('RGB', size, data, 'raw').transpose(Image.FLIP_TOP_BOTTOM)
                img.save(path, quality = 95)
            multiprocessing.Process(target = save_image_to_file, args = (size, data, saveto)).start()

    # Mouse position changed
    def mouse_position_event(self, x, y, dx, dy):
        self.sombrero_mgl.pipeline["mMouse"] = np.array([x, y])
        if self.imgui_io.want_capture_mouse: return
        if self.context.live_mode == RealTimeModes.Mode2D: self.context.camera2d.mouse_position_event(x, y, dx, dy)
        if self.context.live_mode == RealTimeModes.Mode3D: self.context.camera3d.mouse_position_event(x, y, dx, dy)
        
    # Mouse drag, add to pipeline drag
    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)
        if self.imgui_io.want_capture_mouse: return

        if 2 in self.context.mouse_buttons_pressed:
            if self.context.shift_pressed: self.sombrero_mgl.pipeline["mFrame"] -= (dy * self.context.fps) / 200
            elif self.context.alt_pressed: self.target_time_factor -= dy / 80
            else: self.sombrero_mgl.pipeline["mFrame"] -= (dy * self.context.fps) / 800
        else:
            if self.context.live_mode == RealTimeModes.Mode2D:
                self.context.camera2d.mouse_drag_event(x = x, y = y, dx = dx, dy = dy)
                self.window.mouse_exclusivity = True
            if self.context.live_mode == RealTimeModes.Mode3D:
                self.context.camera3d.mouse_drag_event(x = x, y = y, dx = dx, dy = dy)

    # Change SSAA
    def change_ssaa(self, value):
        debug_prefix = "[SombreroWindow.change_ssaa]"
        self.context.ssaa = value
        self.sombrero_mgl._read_shaders_from_paths_again()
        logging.info(f"{debug_prefix} Changed SSAA to [{value}]")

    # Zoom in or out (usually)
    def mouse_scroll_event(self, x_offset, y_offset):
        debug_prefix = "[SombreroWindow.mouse_scroll_event]"
        self.imgui.mouse_scroll_event(x_offset, y_offset)
        if self.imgui_io.want_capture_mouse: return
        if self.context.live_mode == RealTimeModes.Mode2D: self.context.camera2d.mouse_scroll_event(x_offset = x_offset, y_offset = y_offset)
        if self.context.live_mode == RealTimeModes.Mode3D: self.context.camera3d.mouse_scroll_event(x_offset = x_offset, y_offset = y_offset)

    def mouse_press_event(self, x, y, button):
        debug_prefix = "[SombreroWindow.mouse_press_event]"
        logging.info(f"{debug_prefix} Mouse press (x, y): [{x}, {y}] Button [{button}]")
        self.imgui.mouse_press_event(x, y, button)
        if self.imgui_io.want_capture_mouse: return
        if not button in self.context.mouse_buttons_pressed: self.context.mouse_buttons_pressed.append(button)
        if button == 2: self.window.mouse_exclusivity = True

    def mouse_release_event(self, x, y, button):
        debug_prefix = "[SombreroWindow.mouse_release_event]"
        logging.info(f"{debug_prefix} Mouse release (x, y): [{x}, {y}] Button [{button}]")
        self.imgui.mouse_release_event(x, y, button)
        if button in self.context.mouse_buttons_pressed: self.context.mouse_buttons_pressed.remove(button)
        if self.imgui_io.want_capture_mouse: return
        if not self.context.live_mode == RealTimeModes.Mode3D: self.window.mouse_exclusivity = False

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)


    # # # # GUI, somewhat intensive and weird code that can't be really simplified


    # Render the user interface
    def render_ui(self):
        section_color = (0, 1, 0)
        imgui.push_style_var(imgui.STYLE_WINDOW_BORDERSIZE, 0.0)
        imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0)
        imgui.new_frame()

        # Main menu
        if self.context.window_show_menu:
            W, H = self.context.width / 2, self.context.height / 2
            imgui.set_window_position(W, H)
            imgui.begin(f"Modular Music Visualizer", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE)
            imgui.text("-" * 30)
            imgui.separator()

            # Presets loading
            imgui.text_colored("Load Presets", *section_color)
            for item in os.listdir(self.sombrero_mgl.mmv_interface.shaders_dir / "presets"):
                if ".py" in item:
                    item = item.replace(".py", "")
                    changed = imgui.button(f"> {item}")
                    if changed:
                        self.sombrero_mgl.mmv_interface.main.load_preset(item)

            w, h = imgui.get_window_width(), imgui.get_window_height()
            imgui.set_window_position(W - (w/2), H - (h/2))
            imgui.end()

        # # # Info window, top left anchored

        dock_y = 0
        if 1:
            imgui.set_next_window_collapsed(True, imgui.FIRST_USE_EVER)
            imgui.set_next_window_position(0, dock_y)
            imgui.set_next_window_bg_alpha(0.5)
            imgui.begin(f"Info Window", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE)

            # Render related
            imgui.separator()
            imgui.text_colored("Render", *section_color)
            imgui.text(f"SSAA:       [{self.context.ssaa:.3f}]")
            imgui.text(f"Resolution: [{int(self.context.width)}, {int(self.context.height)}] => [{int(self.context.width*self.context.ssaa)}, {int(self.context.height*self.context.ssaa)}]")

            # Camera stats
            if self.context.live_mode == RealTimeModes.Mode2D: self.context.camera2d.gui()
            if self.context.live_mode == RealTimeModes.Mode3D: self.context.camera3d.gui()
            if self.context.piano_roll is not None: self.context.piano_roll.gui()
            if self.context.joysticks is not None: self.context.joysticks.gui()

            dock_y += imgui.get_window_height()
            imgui.end()

        # # # Basic render, config settings

        if 1:
            imgui.set_next_window_collapsed(True, imgui.FIRST_USE_EVER)
            imgui.set_next_window_position(0, dock_y)
            imgui.set_next_window_bg_alpha(0.5)
            imgui.begin("Config Window", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE)
            
            # # FPS
            changed, value = imgui.input_int("Target FPS", self.context.fps)
            if changed: self.sombrero_mgl.change_fps(value)

            # List of common fps
            for fps in [24, 30, 60, 90, 120, 144, 240]:
                changed = imgui.button(f"{fps}Hz")
                if fps != 240: imgui.same_line() # Same line until last value
                if changed: self.context.change_fps(fps)
            imgui.separator()

            # # Time
            t = f"{self.sombrero_mgl.pipeline['mTime']:.1f}s"
            if not self.context.freezed_pipeline: imgui.text_colored(f"Time [PLAYING] [{t}]", *section_color)
            else: imgui.text_colored(f"Time [FROZEN] [{t}]", 1, 0, 0)

            changed, value = imgui.slider_float("Multiplier", self.target_time_factor, min_value = -3, max_value = 3, power = 1)
            if changed:
                self.context.time_speed = value

            # # Time
            imgui.separator()

            # Quick
            for ratio in [-2, -1, -0.5, 0, 0.1, 0.25, 0.5, 1, 2]:
                changed = imgui.button(f"{ratio}x")
                if ratio != 2: imgui.same_line() # Same line until last value
                if changed:
                    self.context.time_speed = ratio
                    self.context.freezed_pipeline = False
            imgui.separator()

            imgui.text_colored("Render Config", *section_color)
            changed, value = imgui.slider_int("Quality", self.context.quality, min_value = 0, max_value = 20)
            if changed: self.context.quality = value; 

            if self.context.piano_roll is not None:
                self.context.piano_roll.gui()

            dock_y += imgui.get_window_height()
            imgui.end()

        # # # Performance Window

        if 1:
            # Update framerates, get info
            self.context.framerate.next()
            info = self.context.framerate.get_info()

            imgui.set_next_window_collapsed(True, imgui.FIRST_USE_EVER)
            imgui.set_next_window_position(0, dock_y)
            imgui.set_next_window_bg_alpha(0.5)
            imgui.begin("Performance", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE)
            imgui.text_colored(f"Frametimes [last {self.context.framerate.history:.2f}s]", *section_color)
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
  
