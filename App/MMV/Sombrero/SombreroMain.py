"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Global controller and wrapper on mapping, rendering shaders.

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
import logging
import sys
from array import array
from contextlib import suppress
from enum import Enum, auto

import moderngl
import numpy as np
from MMV.Sombrero.SombreroConstructor import *
from MMV.Sombrero.SombreroContext import SombreroContext
from MMV.Sombrero.SombreroPianoRoll import PianoRoll
from MMV.Sombrero.SombreroShader import *
from MMV.Sombrero.SombreroWindow import SombreroWindow
from PIL import Image


# When we don't find some element / want to ignore something
# we .get(expected, DummyElement()) and continue
class DummyElement:
    value = None
    def write(self, *a, **k): pass


def pretty_lines_counter(data):
    for number, line in enumerate(data.split('\n')):
        yield f"[{number:05}] | {line}"


class SombreroMain:
    def __init__(self, PackageInterface, MasterShader=False, flip=False, ChildSombreroContext=None):
        # # Constructor
        self.PackageInterface = PackageInterface

        # Do flip coordinates vertically? OpenGL context ("shared" with main class)
        self.flip = flip

        # # Standard attributes
        self.MasterShader = MasterShader

        # Contents dictionary that holds instruction, other classes and all
        # Pipeline textures have name if mappend one 
        # Pending uniforms to be passed values after shader is loaded
        # Variables pipeline
        self.contents = {}
        self.writable_textures = {}
        self.pending_uniforms = []
        self.pipeline = {}

        # Modules
        if self.MasterShader: self.SombreroContext = SombreroContext(self)
        else: self.SombreroContext = ChildSombreroContext
        self.window = SombreroWindow(SombreroMain = self)
        self.macros = SombreroShaderMacros(self)
        self.shader = SombreroShader()
        self.constructor = None
        
        self._want_to_reload = False
        self.__ever_finished = False
    
    def create_piano_roll(self):
        self.piano_roll = PianoRoll(self)
        return self.piano_roll

    # Create and configure one child of this class with same target stuff
    def new_child(self):
        child = SombreroMain(PackageInterface = self.PackageInterface, MasterShader = False, context = self.SombreroContext)
        return child

    # # Shorthands

    def __mipmap_anisotropy_repeat_texture(self, texture, context):
        texture.anisotropy = context.get("anisotropy", 1)
        texture.repeat_x = context.get("repeat_x", True)
        texture.repeat_y = context.get("repeat_y", True)
        if context.get("mipmaps", False): texture.build_mipmaps()

    # Add a dictionary to the next available index of the contents attribute
    def assign_content(self, dictionary): self.contents[len(list(self.contents.keys()))] = dictionary

    # # Mappings

    # Map some other SombreroMain class as a shader of this one
    def map_shader(self, name, SombreroMain):
        uniforms = [Uniform("sampler2D", name, None)]
        self.pending_uniforms += uniforms
        self.assign_content(dict(
            loader = "child_SombreroMain", name = name, texture = SombreroMain.texture, SombreroMain = SombreroMain,
            dynamic = True
        ))
        return uniforms

    # Image mapping as texture
    def map_image(self, name, path, repeat_x = True, repeat_y = True, mipmap = True, anisotropy = 16):

        # Open image, mipmap, texture
        img = Image.open(path).convert("RGBA")
        texture = self.SombreroContext.gl_context.texture(img.size, 4, img.tobytes())
        self.__mipmap_anisotropy_repeat_texture(texture, locals())

        # Uniforms, assign content
        uniforms = [Uniform("sampler2D", name, None), Uniform("vec2", f"{name}_resolution", img.size)]
        self.pending_uniforms += uniforms
        self.assign_content(dict(
            loader = "image", name = name, texture = texture, resolution = img.size
        )); return uniforms

    # Map some other SombreroMain class as a shader of this one
    def map_pipeline_texture(self, name, width, height, depth):
        size = (width, height)
        uniforms = [Uniform("sampler2D", name, None), Uniform("vec2", f"{name}_resolution", size)]
        texture = self.SombreroContext.gl_context.texture(size, depth, dtype = "f4")
        texture.write(np.zeros((width, height, depth), dtype = np.float32))  # Start empty (GL context no guarantee to be clean)
        self.writable_textures[name] = texture
        self.pending_uniforms += uniforms
        self.assign_content(dict(
            loader = "pipeline_texture", name = name, texture = texture, size = size
        ))
        return uniforms

    # # GL objects

    # Create one texture attached to some FBO. Depth = 4 -> RGBA
    def create_texture_fbo(self, width, height, depth = 4) -> list:
        texture = self.SombreroContext.gl_context.texture((int(width), int(height)), depth)
        fbo = self.SombreroContext.gl_context.framebuffer(color_attachments = [texture])
        return [texture, fbo]

    # Get the uniform if exists, enforce tuple if isn't tuple or int and assign the value
    def set_uniform(self, name, value):
        if (not isinstance(value, float)) and (not isinstance(value, int)): value = tuple(value)
        self.program.get(name, DummyElement()).value = value
        return name
    
    # Write to some PipelineTexture that was mapped, recursively to every child
    def write_pipeline_texture(self, name, data):
        self.writable_textures.get(name, DummyElement()).write(np.array(data, dtype = np.float32).tobytes())
        for child in self.children_SombreroMain(): child.write_pipeline_texture(name, data)
    
    # Write uniform values on the list of pending uniforms
    def solve_pending_uniforms(self):
        for item in self.pending_uniforms:
            if item.value is not None: self.set_uniform(item.name, item.value)
        self.pending_uniforms = []

    # Pipe a global pipeline
    def pipe_pipeline(self, pipeline):
        for name, value in pipeline.items(): self.set_uniform(name, value)
    
    # # Load

    def _create_assing_texture_fbo_render_buffer(self):
        self.texture, self.fbo = self.create_texture_fbo(
            width  = self.SombreroContext.width  * self.SombreroContext.ssaa,
            height = self.SombreroContext.height * self.SombreroContext.ssaa)

    # Load shader from this class's SombreroConstructor
    def finish(self, _give_up_if_any_errors = False):
        dpfx = "[SombreroMain.finish]"
        self.__ever_finished = True

        # Default constructor is Fullscreen if not set
        if self.constructor is None: self.constructor = FullScreenConstructor(self)

        # Add IOs to the frag shader based on constructor specifications
        self.constructor.treat_fragment_shader(self.shader)
        frag = self.shader.build()

        # The FBO and texture so we can use on parent shaders, master shader doesn't require since it haves window fbo
        if not self.MasterShader:
            self._create_assing_texture_fbo_render_buffer()
            
        try:
            self.program = self.SombreroContext.gl_context.program(
                vertex_shader = self.constructor.vertex_shader,
                geometry_shader = self.constructor.geometry_shader,
                fragment_shader = frag,
            )
            self.solve_pending_uniforms()
            if self.MasterShader: self.SombreroContext.framerate.clear()

        except moderngl.error.Error as e:
            self.reset()
            for pretty in pretty_lines_counter(frag): print(pretty)
            logging.error(f"{dpfx} {e}")
            if _give_up_if_any_errors: sys.exit()
            self.constructor = FullScreenConstructor(self)
            self.shader = SombreroShader()
            self.macros.load(self.PackageInterface.sombrero_dir/"glsl"/"missing_texture.glsl")
            self.finish(_give_up_if_any_errors = True)

    # Get render instructions, do this every render because stuff like piano roll needs
    # their draw instructions to be updated
    def get_vao(self):
        if instructions := self.constructor.vao():
            self.vao = self.SombreroContext.gl_context.vertex_array(self.program, instructions, skip_errors = True)

    # # Render

    # Next iteration, also render
    def next(self, custom_pipeline = {}):
        if not self.__ever_finished: self.finish()
        if custom_pipeline is None: custom_pipeline = {}

        # # Update pipeline

        # Get current window "state"
        self.pipeline["mResolution"] = (self.SombreroContext.width * self.SombreroContext.ssaa, self.SombreroContext.height * self.SombreroContext.ssaa)
        self.pipeline["mFlip"] = -1 if self.flip else 1

        # Render related
        self.pipeline["quality"] = self.SombreroContext.quality

        # Time related
        self.pipeline["mFrame"] = self.pipeline.get("mFrame", 0) + self.SombreroContext.time_speed
        self.pipeline["mTime"] = self.pipeline["mFrame"] / self.SombreroContext.fps

        # GUI related
        self.pipeline["mIsGuiVisible"] = self.SombreroContext.show_gui
        self.pipeline["mIsDebugMode"] = self.SombreroContext.debug_mode

        # 2D
        self.pipeline["m2DIsDraggingMode"] = 1 in self.SombreroContext.mouse_buttons_pressed
        self.pipeline["m2DIsDragging"] = self.SombreroContext.camera2d.is_dragging
        self.pipeline["m2DRotation"] = self.SombreroContext.camera2d.rotation.value
        self.pipeline["m2DZoom"] = self.SombreroContext.camera2d.zoom.value
        self.pipeline["m2DDrag"] = self.SombreroContext.camera2d.drag.value

        # 3D
        self.pipeline["m3DCameraBase"] = self.SombreroContext.camera3d.standard_base.reshape(-1)
        self.pipeline["m3DCameraPointing"] = self.SombreroContext.camera3d.pointing
        self.pipeline["m3DCameraPos"] = self.SombreroContext.camera3d.position.value
        self.pipeline["m3DRoll"] = self.SombreroContext.camera3d.roll.value
        self.pipeline["m3DFOV"] = self.SombreroContext.camera3d.fov.value
        
        # Keys
        self.pipeline["mMouse1"] = 1 in self.SombreroContext.mouse_buttons_pressed
        self.pipeline["mMouse2"] = 2 in self.SombreroContext.mouse_buttons_pressed
        self.pipeline["mMouse3"] = 3 in self.SombreroContext.mouse_buttons_pressed
        self.pipeline["mKeyShift"] = self.SombreroContext.shift_pressed
        self.pipeline["mKeyCtrl"] = self.SombreroContext.ctrl_pressed
        self.pipeline["mKeyAlt"] = self.SombreroContext.alt_pressed

        # Merge the two dictionaries
        for key, value in custom_pipeline.values():
            self.pipeline[key] = value

        # Render, update window
        self._render()
        self.window.update_window()

    # Internal function for rendering (some stuff needs to be called like getting next image of video)
    def _render(self):

        # VAO, constructor
        self.constructor.next()
        self.get_vao()

        # Pipe to self
        self.pipe_pipeline(self.pipeline)

        # Pipe the pipeline to child shaders and render them
        for child in self.children_SombreroMain():
            child.pipe_pipeline(self.pipeline)
            child.pipeline = self.pipeline
            child._render()

        # Which FBO to use
        if self.MasterShader: self.window.window.use(); self.window.window.clear()
        else: self.fbo.use(); self.fbo.clear()

        # Use textures at specific indexes
        for index, item in self.contents.items():

            # Read next frame of video
            if item["loader"] == "video":
                raise NotImplementedError("Video TODO")
            
            # Where texture will be used
            try: item["texture"].use(location = index)
            except Exception as e: print(e)
            try: self.program[item["name"]] = index
            except KeyError: pass  # Texture was mapped but isn't used

        # Render the content
        # self.vao.render(mode = moderngl.TRIANGLE_STRIP)

        self.SombreroContext.gl_context.enable_only(moderngl.NOTHING)
        
        if isinstance(self.constructor, PianoRollConstructor):
            self.SombreroContext.gl_context.enable_only(moderngl.BLEND)

        if nvert := self.constructor.num_vertices:
            self.vao.render(mode = moderngl.POINTS, vertices = nvert)
        
        # Draw UI then reset composite mode to NOTHING because imgui changes that
        if self.MasterShader and (not self.SombreroContext.window_headless) and (self.SombreroContext.show_gui):
            self.window.render_ui()
            
        self.SombreroContext.gl_context.enable_only(moderngl.NOTHING)

    # Read contents from window FBO, chose one
    def read(self): return self.window.window.fbo.read()
    def stdout(self, target): target.write(self.read())

    @property # FBO size for screenshots
    def fbo_size(self): return self.window.window.fbo.size
    
    # Generator for iterating on child SombreroMain instances
    def children_SombreroMain(self):
        for index, item in self.contents.items():
            if item["loader"] == "child_SombreroMain":
                yield item["SombreroMain"]
    
    # Return list of used variables in program
    def get_used_variables(self) -> list:
        info = [k for k in self.program._members.keys()]

        # Call for every shader as texture loaders
        for child in self.children_SombreroMain():
            for key in child.get_used_variables(): info.append(key)

        # Remove duplicates
        return list(set(info))
    
    def time_zero(self): self.pipeline["mFrame"] = 0

    def reset(self):
        if self.SombreroContext.piano_roll is not None:
            self.SombreroContext.piano_roll.synth.reset()
            del self.SombreroContext.piano_roll; self.SombreroContext.piano_roll = None
        self.SombreroContext.camera2d.reset()
        self.SombreroContext.camera3d.reset()
        for child in self.children_SombreroMain(): child.reset(); del child
        with suppress(AttributeError): self.program.release()
        with suppress(AttributeError): self.texture.release()
        with suppress(AttributeError): self.fbo.release()
        with suppress(AttributeError): self.vao.release()
        if isinstance(self.constructor, FullScreenConstructor):
            self.constructor.once_returned_vao = False
        self.contents = {}
