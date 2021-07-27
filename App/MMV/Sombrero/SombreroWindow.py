"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

===============================================================================

Purpose: Window utilities, functions for SombreroMain
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
import gc
import logging
import math
import multiprocessing
import os
import time
import uuid
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

import imgui
import moderngl
import moderngl_window
import numpy as np
import quaternion
from dotmap import DotMap
from MMV.Sombrero.Modules.Camera.Camera2D import Camera2D
from MMV.Sombrero.Modules.Camera.Camera3D import Camera3D
from MMV.Sombrero.Modules.Controller.Joystick import Joysticks
from MMV.Sombrero.SombreroContext import RealTimeModes
from MMV.Sombrero.Utils.GLFWKeyboardKeys import KeyboardKey
from MMV.Sombrero.Utils.SombreroWindowUtils import (FrameTimesCounter,
                                                    OnScreenTextMessages)
from moderngl_window import resources
from moderngl_window.conf import settings
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from PIL import Image

sin = math.sin
cos = math.cos

from MMV.Common.Polyglot import Polyglot

Speak = Polyglot.Speak

class SombreroWindow:

    def __init__(self, SombreroMain):
        self.SombreroMain = SombreroMain
        self.PackageInterface = self.SombreroMain.PackageInterface
        self.SombreroContext = self.SombreroMain.SombreroContext
        self.ACTION_MESSAGE_TIMEOUT = self.SombreroContext.LiveConfig["window"]["action_message_timeout"]
        
        # Modules
        self.messages = OnScreenTextMessages()
        self.SombreroContext.camera3d = Camera3D(self)
        self.SombreroContext.camera2d = Camera2D(self)
        self.SombreroContext.joysticks = Joysticks(self)
        self.SombreroContext.framerate = FrameTimesCounter(fps = self.SombreroContext.fps)
        self.ModernGLWindowShouldClose = False

        # TODO move to context
        self.target_time_factor = 1

    def CreateWindow(self):
        dpfx = "[SombreroWindow.CreateWindow]"

        # On Wayland one must use XWayland because ModernGL haven't implemented EGL yet
        if self.PackageInterface.os == "linux": os.environ["XDG_SESSION_TYPE"] = "x11"

        # Headless we disable vsync because we're rendering only..?
        # And also force aspect ratio just in case (strict option)
        if self.SombreroContext.window_headless: settings.WINDOW["aspect_ratio"] = self.SombreroContext.width / self.SombreroContext.height
        else: settings.WINDOW["aspect_ratio"] = None

        # Assign the function arguments
        settings.WINDOW["class"] = f"moderngl_window.context.{self.SombreroContext.window_class}.Window"
        settings.WINDOW["vsync"] = self.SombreroContext.window_vsync
        settings.WINDOW["title"] = Speak("Real Time Shaders")+" [Sombrero]"

        # Don't set target width, height otherwise this will always crash
        if (self.SombreroContext.window_headless) or (not self.SombreroContext.LINUX_GNOME_PIXEL_SAVER_EXTENSION_WORKAROUND):
            settings.WINDOW["size"] = (self.SombreroContext.width, self.SombreroContext.height)

        # Create the window
        self.window = moderngl_window.create_window_from_settings()
        self.SombreroContext.gl_context = self.window.ctx

        # Make sure we render strictly into the resolution we asked
        if self.SombreroContext.window_strict: self.window.fbo.viewport = (0, 0, self.SombreroContext.width, self.SombreroContext.height)

        # Functions of the window if not headless
        if not self.SombreroContext.window_headless:
            self.window.resize_func = self.WindowResized
            self.window.key_event_func = self.key_event
            self.window.mouse_position_event_func = self.mouse_position_event
            self.window.mouse_drag_event_func = self.mouse_drag_event
            self.window.mouse_scroll_event_func = self.mouse_scroll_event
            self.window.mouse_press_event_func = self.mouse_press_event
            self.window.mouse_release_event_func = self.mouse_release_event
            self.window.unicode_char_entered_func = self.unicode_char_entered
            self.window.close_func = self.CloseWindow
            imgui.create_context()
            self.imgui = ModernglWindowRenderer(self.window)
            self.imgui_io = imgui.get_io()
            self.imgui_io.ini_saving_rate = 1

    # [NOT HEADLESS] Window was resized, update the width and height so we render with the new config
    def WindowResized(self, width, height):
        if hasattr(self, "strict") and self.strict: return

        # We need to do some sort of change of basis between drag numbers when we change resolutions because
        # drag itself is absolute, not related 
        self.SombreroContext.camera2d.drag.set_target(
            self.SombreroContext.camera2d.drag.value * (np.array([width, height]) / np.array([self.SombreroContext.width, self.SombreroContext.height]))
        )
        self.SombreroContext.camera2d.drag._target_is_current_value()

        # Set width and height
        self.SombreroContext.width = int(width)
        self.SombreroContext.height = int(height)

        # for child in self.SombreroMain.children_SombreroMain():
        #     child.texture.release()
        #     child.fbo.release()
        #     child._create_assing_texture_fbo_render_buffer()

        # for child in self.SombreroMain.children_SombreroMain():
        #     child.window.WindowResized(width, height)
        # self.SombreroContext.mmv_main.reload_shaders()

        # Master shader has window and imgui
        if self.SombreroMain.MasterShader:
            if not self.SombreroContext.window_headless: self.imgui.resize(self.SombreroContext.width, self.SombreroContext.height)
            self.window.fbo.viewport = (0, 0, self.SombreroContext.width, self.SombreroContext.height)
            self.SombreroMain._create_assing_texture_fbo_render_buffer()

    # Close the window
    def CloseWindow(self, *args, **kwargs):
        logging.info(f"[SombreroWindow.CloseWindow] Window should close")
        self.ModernGLWindowShouldClose = True

    # Swap the window buffers, be careful if vsync is False and you have a heavy
    # shader, it will consume all of your GPU computation and will most likely freeze
    # the video
    def UpdateWindow(self):
        self.window.swap_buffers()

        # cfg = self.SombreroMain.config["window"]

        if not self.SombreroContext.mode == self.SombreroContext.ExecutionMode.Render:
            self.SombreroContext.joysticks.next()
        if self.SombreroContext.live_mode == RealTimeModes.Mode2D: self.SombreroContext.camera2d.next()
        if self.SombreroContext.live_mode == RealTimeModes.Mode3D: self.SombreroContext.camera3d.next()

        # TODO: move to context
        # self.SombreroContext.intensity += (self.target_intensity - self.SombreroContext.intensity) * cfg["intensity_responsiveness"]
        # self.time_factor += \
        #     ( (int(not self.playback_stopped) * int(not self.SombreroContext.freezed_GlobalPipeline) * self.target_time_factor) \
        #     - self.time_factor) * self.SombreroMain._fix_ratio_due_fps(cfg["time_responsiveness"]) 

    def key_event(self, key, action, modifiers):
        dpfx = "[SombreroWindow.key_event]"
        self.imgui.key_event(key, action, modifiers)
        logging.info(f"{dpfx} Key [{key}] Action [{action}] Modifier [{modifiers}]")

        # Shift and control
        if key == 340: self.SombreroContext.shift_pressed = bool(action)
        if key == 341: self.SombreroContext.ctrl_pressed = bool(action)
        if key == 342: self.SombreroContext.alt_pressed = bool(action)
        
        # "tab" key pressed, toggle gui
        if (key == 258) and (action == 1):
            if self.SombreroContext.shift_pressed:
                self.SombreroContext.show_gui = not self.SombreroContext.show_gui
                self.messages.add(f"(Shift + TAB) Toggle All GUI [{self.SombreroContext.show_gui}]", self.ACTION_MESSAGE_TIMEOUT)
                self.SombreroContext.framerate.clear()
            else:
                self.SombreroContext.window_show_menu = not self.SombreroContext.window_show_menu
                self.messages.add(f"(TAB) Toggle menu GUI [{self.SombreroContext.window_show_menu}]", self.ACTION_MESSAGE_TIMEOUT)
                if self.SombreroContext.window_show_menu: self.window.mouse_exclusivity = False
                else:
                    if self.SombreroContext.live_mode == RealTimeModes.Mode3D: self.window.mouse_exclusivity = True

        if self.imgui_io.want_capture_keyboard: return

        if self.SombreroContext.shift_pressed: pass

        elif self.SombreroContext.ctrl_pressed:
            if (key == 49) and (action == 1):
                self.playback_stopped = not self.playback_stopped
                self.messages.add(f"{dpfx} (Ctrl 1) Toggle playback [{self.playback_stopped}]", self.ACTION_MESSAGE_TIMEOUT)
        else:
            if (key == KeyboardKey) and (action == 1):
                self.messages.add(f"{dpfx} (2) Set 2D (default) mode", self.ACTION_MESSAGE_TIMEOUT)
                self.window.mouse_exclusivity = False
                self.SombreroContext.live_mode = RealTimeModes.Mode2D
                self.SombreroContext.window_show_menu = False

            if (key == 51) and (action == 1):
                self.messages.add(f"{dpfx} (3) Set 3D mode", self.ACTION_MESSAGE_TIMEOUT)
                self.ThreeD_want_to_walk_unit_vector = np.array([0, 0, 0])
                self.window.mouse_exclusivity = True
                self.SombreroContext.live_mode = RealTimeModes.Mode3D
                self.SombreroContext.window_show_menu = False

        # Mode
        if self.SombreroContext.live_mode == RealTimeModes.Mode2D:
            self.SombreroContext.camera2d.key_event(key = key, action = action, modifiers = modifiers)
        if self.SombreroContext.live_mode == RealTimeModes.Mode3D:
            self.SombreroContext.camera3d.key_event(key = key, action = action, modifiers = modifiers)
                
        # # # # Generic
        
        # Escape
        if (key == 256) and (action == 1) and (self.SombreroContext.live_mode == RealTimeModes.Mode3D):
            self.ModernGLWindowShouldClose = True

        if (key == 44) and (action == 1):
            if self.SombreroContext.shift_pressed:
                self.target_time_factor -= 0.01
                self.messages.add(f"{dpfx} (,) Playback speed [-0.1] [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)
            else:
                self.target_time_factor -= 0.1
                self.messages.add(f"{dpfx} (.) Playback speed [-0.1] [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)

        if (key == 46) and (action == 1):
            if self.SombreroContext.shift_pressed:
                self.target_time_factor += 0.01
                self.messages.add(f"{dpfx} (,) Playback speed [+0.1] [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)
            else:
                self.target_time_factor += 0.1
                self.messages.add(f"{dpfx} (.) Playback speed [+0.1] [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)

        if (key == 47) and (action == 1):
                self.target_time_factor *= -1
                self.messages.add(f"{dpfx} (;) Reverse playback speed [{self.target_time_factor:.3f}]", self.ACTION_MESSAGE_TIMEOUT)
        
        if (key == 70) and (action == 1):
            self.window.fullscreen = not self.window.fullscreen
            self.messages.add(f"{dpfx} (f) Toggle fullscreen [{self.window.fullscreen}]", self.ACTION_MESSAGE_TIMEOUT)

        if (key == 72) and (action == 1):
            self.window.cursor = not self.window.cursor
            self.messages.add(f"{dpfx} (h) Toggle Hide Mouse [{self.window.cursor}]", self.ACTION_MESSAGE_TIMEOUT)
      
        if (key == 79) and (action == 1):
            self.SombreroContext.freezed_GlobalPipeline = not self.SombreroContext.freezed_GlobalPipeline
            self.messages.add(f"{dpfx} (o) Freeze GlobalPipeline [{self.SombreroContext.freezed_GlobalPipeline}]", self.ACTION_MESSAGE_TIMEOUT)
            self.time_factor = 0
            for index in self.SombreroMain.contents.keys():
                if self.SombreroMain.contents[index]["loader"] == "shader":
                    self.SombreroMain.contents[index]["shader_as_texture"].freezed_GlobalPipeline = self.SombreroContext.freezed_GlobalPipeline

        if (key == 82) and (action == 1):
            self.messages.add(f"{dpfx} (r) Reloading shaders..", self.ACTION_MESSAGE_TIMEOUT)
            # TOOD remove want to reload
            self.SombreroContext.mmv_main.reload_shaders()
            self.SombreroMain._want_to_reload = True
  
        if (key == 84) and (action == 1):
            self.SombreroMain.GlobalPipeline["mFrame"] = 0
            self.SombreroMain.GlobalPipeline["mTime"] = 0
            self.messages.add(f"{dpfx} (t) Set time to [0s]", self.ACTION_MESSAGE_TIMEOUT)

        if (key == 89) and (action == 1):
            self.messages.add(f"{dpfx} (y) Toggle debug", self.ACTION_MESSAGE_TIMEOUT)
            self.debug_mode = not self.debug_mode

        # "p" key pressed, screenshot
        if (key == 80) and (action == 1):

            # Where to save
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            saveto = self.PackageInterface.screenshots_dir / f"{now}.jpg"
            self.messages.add(f"{dpfx} (p) Screenshot save [{saveto}]", self.ACTION_MESSAGE_TIMEOUT * 4)

            old = self.SombreroContext.show_gui  # Did we have GUI enabled previously?
            self.SombreroContext.show_gui = False  # Disable for screenshot
            self.SombreroMain._render()  # Update screen so we actually remove the GUI
            self.SombreroContext.show_gui = old  # Revert
      
            # Get data ib the scree's size viewport
            size = (self.SombreroContext.width, self.SombreroContext.height)
            data = self.window.fbo.read( viewport = (0, 0, size[0], size[1]) )
            logging.info(f"{dpfx} [Resolution: {size}] [WxHx3: {size[0] * size[1] * 3}] [len(data): {len(data)}]")

            # Multiprocessing save image to file so we don't lock
            def save_image_to_file(size, data, path):
                img = Image.frombytes('RGB', size, data, 'raw').transpose(Image.FLIP_TOP_BOTTOM)
                img.save(path, quality = 95)
            multiprocessing.Process(target = save_image_to_file, args = (size, data, saveto)).start()

    # Mouse position changed
    def mouse_position_event(self, x, y, dx, dy):
        self.SombreroMain.GlobalPipeline["mMouse"] = np.array([x, y])
        if self.imgui_io.want_capture_mouse: return
        if self.SombreroContext.live_mode == RealTimeModes.Mode2D: self.SombreroContext.camera2d.mouse_position_event(x, y, dx, dy)
        if self.SombreroContext.live_mode == RealTimeModes.Mode3D: self.SombreroContext.camera3d.mouse_position_event(x, y, dx, dy)
        
    # Mouse drag, add to GlobalPipeline drag
    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)
        if self.imgui_io.want_capture_mouse: return

        if 2 in self.SombreroContext.mouse_buttons_pressed:
            if self.SombreroContext.shift_pressed: self.SombreroMain.GlobalPipeline["mFrame"] -= (dy * self.SombreroContext.fps) / 200
            elif self.SombreroContext.alt_pressed: self.target_time_factor -= dy / 80
            else: self.SombreroMain.GlobalPipeline["mFrame"] -= (dy * self.SombreroContext.fps) / 800
        else:
            if self.SombreroContext.live_mode == RealTimeModes.Mode2D:
                self.SombreroContext.camera2d.mouse_drag_event(x = x, y = y, dx = dx, dy = dy)
                self.window.mouse_exclusivity = True
            if self.SombreroContext.live_mode == RealTimeModes.Mode3D:
                self.SombreroContext.camera3d.mouse_drag_event(x = x, y = y, dx = dx, dy = dy)

    # Change SSAA
    def change_ssaa(self, value):
        dpfx = "[SombreroWindow.change_ssaa]"
        self.SombreroContext.ssaa = value
        self.SombreroMain._read_shaders_from_paths_again()
        logging.info(f"{dpfx} Changed SSAA to [{value}]")

    # Zoom in or out (usually)
    def mouse_scroll_event(self, x_offset, y_offset):
        dpfx = "[SombreroWindow.mouse_scroll_event]"
        self.imgui.mouse_scroll_event(x_offset, y_offset)
        if self.imgui_io.want_capture_mouse: return
        if self.SombreroContext.live_mode == RealTimeModes.Mode2D: self.SombreroContext.camera2d.mouse_scroll_event(x_offset = x_offset, y_offset = y_offset)
        if self.SombreroContext.live_mode == RealTimeModes.Mode3D: self.SombreroContext.camera3d.mouse_scroll_event(x_offset = x_offset, y_offset = y_offset)

    def mouse_press_event(self, x, y, button):
        dpfx = "[SombreroWindow.mouse_press_event]"
        logging.info(f"{dpfx} Mouse press (x, y): [{x}, {y}] Button [{button}]")
        self.imgui.mouse_press_event(x, y, button)
        if self.imgui_io.want_capture_mouse: return
        if not button in self.SombreroContext.mouse_buttons_pressed: self.SombreroContext.mouse_buttons_pressed.append(button)
        if button == 2: self.window.mouse_exclusivity = True

    def mouse_release_event(self, x, y, button):
        dpfx = "[SombreroWindow.mouse_release_event]"
        logging.info(f"{dpfx} Mouse release (x, y): [{x}, {y}] Button [{button}]")
        self.imgui.mouse_release_event(x, y, button)
        if button in self.SombreroContext.mouse_buttons_pressed: self.SombreroContext.mouse_buttons_pressed.remove(button)
        if self.imgui_io.want_capture_mouse: return
        if not self.SombreroContext.live_mode == RealTimeModes.Mode3D: self.window.mouse_exclusivity = False

    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)


    # # # # GUI, somewhat intensive and weird code that can't be really simplified


    # Render the user interface
    def render_ui(self):
        section_color = (0, 1, 0)
        imgui.push_style_var(imgui.STYLE_WINDOW_BORDERSIZE, 0.0)
        imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0)
        imgui.new_frame()

        # # Main menu
        # if self.SombreroContext.window_show_menu:
        #     W, H = self.SombreroContext.width / 2, self.SombreroContext.height / 2
        #     imgui.set_window_position(W, H)
        #     imgui.begin(f"Modular Music Visualizer", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE)
        #     imgui.text("-" * 30)
        #     imgui.separator()

        #     # Presets loading
        #     imgui.text_colored("Load Presets", *section_color)
        #     for item in os.listdir(self.SombreroMain.PackageInterface.shaders_dir / "presets"):
        #         if ".py" in item:
        #             item = item.replace(".py", "")
        #             changed = imgui.button(f"> {item}")
        #             if changed:
        #                 self.SombreroMain.PackageInterface.main._load_preset(item)

        #     w, h = imgui.get_window_width(), imgui.get_window_height()
        #     imgui.set_window_position(W - (w/2), H - (h/2))
        #     imgui.end()

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
            imgui.text(f"SSAA:       [{self.SombreroContext.ssaa:.3f}]")
            imgui.text(f"Resolution: [{int(self.SombreroContext.width)}, {int(self.SombreroContext.height)}] => [{int(self.SombreroContext.width*self.SombreroContext.ssaa)}, {int(self.SombreroContext.height*self.SombreroContext.ssaa)}]")

            # Camera stats
            if self.SombreroContext.live_mode == RealTimeModes.Mode2D: self.SombreroContext.camera2d.gui()
            if self.SombreroContext.live_mode == RealTimeModes.Mode3D: self.SombreroContext.camera3d.gui()
            if self.SombreroContext.piano_roll is not None: self.SombreroContext.piano_roll.gui()
            if self.SombreroContext.joysticks is not None: self.SombreroContext.joysticks.gui()

            dock_y += imgui.get_window_height()
            imgui.end()

        # # # Basic render, config settings

        if 1:
            imgui.set_next_window_collapsed(True, imgui.FIRST_USE_EVER)
            imgui.set_next_window_position(0, dock_y)
            imgui.set_next_window_bg_alpha(0.5)
            imgui.begin("Config Window", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE)
            
            # # FPS
            changed, value = imgui.input_int("Target FPS", self.SombreroContext.fps)
            if changed: self.SombreroContext.change_fps(value)

            # List of common fps
            for fps in [24, 30, 60, 90, 120, 144, 240]:
                changed = imgui.button(f"{fps}Hz")
                if fps != 240: imgui.same_line() # Same line until last value
                if changed: self.SombreroContext.change_fps(fps)
            imgui.separator()

            # # Time
            t = f"{self.SombreroMain.GlobalPipeline['mTime']:.1f}s"
            if not self.SombreroContext.freezed_GlobalPipeline: imgui.text_colored(f"Time [PLAYING] [{t}]", *section_color)
            else: imgui.text_colored(f"Time [FROZEN] [{t}]", 1, 0, 0)

            changed, value = imgui.slider_float("Multiplier", self.target_time_factor, min_value = -3, max_value = 3, power = 1)
            if changed:
                self.SombreroContext.time_speed = value

            # # Time
            imgui.separator()

            # Quick
            for ratio in [-2, -1, -0.5, 0, 0.1, 0.25, 0.5, 1, 2]:
                changed = imgui.button(f"{ratio}x")
                if ratio != 2: imgui.same_line() # Same line until last value
                if changed:
                    self.SombreroContext.time_speed = ratio
                    self.SombreroContext.freezed_GlobalPipeline = False
            imgui.separator()

            imgui.text_colored("Render Config", *section_color)
            changed, value = imgui.slider_int("Quality", self.SombreroContext.quality, min_value = 0, max_value = 20)
            if changed: self.SombreroContext.quality = value; 

            if self.SombreroContext.piano_roll is not None:
                self.SombreroContext.piano_roll.gui()

            dock_y += imgui.get_window_height()
            imgui.end()

        # # # Performance Window

        if 1:
            # Update framerates, get info
            self.SombreroContext.framerate.next()
            info = self.SombreroContext.framerate.get_info()

            imgui.set_next_window_collapsed(True, imgui.FIRST_USE_EVER)
            imgui.set_next_window_position(0, dock_y)
            imgui.set_next_window_bg_alpha(0.5)
            imgui.begin("Performance", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_MOVE)
            imgui.text_colored(f"Frametimes [last {self.SombreroContext.framerate.history:.2f}s]", *section_color)
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
  
