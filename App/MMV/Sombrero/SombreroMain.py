"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

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
        self.SombreroDir = self.PackageInterface.SombreroDir

        # Do flip coordinates vertically? OpenGL context ("shared" with main class)
        self.flip = flip

        # # Standard attributes
        self.MasterShader = MasterShader

        # Contents dictionary that holds instruction, other classes and all
        # Pipeline textures have name if mappend one 
        # Pending uniforms to be passed values after shader is loaded
        # Variables GlobalPipeline
        self.contents = {}
        self.WritableTextures = {}
        self.PendingUniforms = []
        self.GlobalPipeline = {}

        # Modules
        if self.MasterShader: self.SombreroContext = SombreroContext(self)
        else: self.SombreroContext = ChildSombreroContext
        self.window = SombreroWindow(SombreroMain=self)
        self.ShaderMacros = SombreroShaderMacros(self)
        self.Shader = SombreroShader()
        self.constructor = None
        
        self._want_to_reload = False
        self.__ever_finished = False
    
    def create_piano_roll(self):
        self.piano_roll = PianoRoll(self)
        return self.piano_roll

    # Create and configure one child of this class with same target stuff
    def NewChild(self):
        child = SombreroMain(
            PackageInterface=self.PackageInterface,
            MasterShader=False,
            ChildSombreroContext=self.SombreroContext)
        return child

    # # Shorthands

    def __mipmap_anisotropy_repeat_texture(self, texture, context):
        texture.anisotropy = context.get("anisotropy", 1)
        texture.repeat_x = context.get("repeat_x", True)
        texture.repeat_y = context.get("repeat_y", True)
        if context.get("mipmaps", False): texture.build_mipmaps()

    # Add a dictionary to the next available index of the contents attribute
    def AssignContent(self, dictionary): self.contents[len(list(self.contents.keys()))] = dictionary

    # # Mappings

    # Map some other SombreroMain class as a shader of this one
    def MapShader(self, Name, SombreroMain):
        uniforms = [Uniform("sampler2D", Name, None)]
        self.PendingUniforms += uniforms
        self.AssignContent(dict(
            loader = "ChildSombreroMain", Name=Name, texture=SombreroMain.texture, SombreroMain=SombreroMain,
            dynamic = True
        ))
        return uniforms

    # Image mapping as texture
    def MapImage(self, Name, path, repeat_x=True, repeat_y=True, mipmap=True, anisotropy=16):

        # Open image, mipmap, texture
        img = Image.open(path).convert("RGBA")
        texture = self.SombreroContext.OpenGL_Context.texture(img.size, 4, img.tobytes())
        self.__mipmap_anisotropy_repeat_texture(texture, locals())

        # Uniforms, assign content
        uniforms = [Uniform("sampler2D", Name, None), Uniform("vec2", f"{Name}_resolution", img.size)]
        self.PendingUniforms += uniforms
        self.AssignContent(dict(
            loader = "image", Name = Name, texture = texture, resolution = img.size
        )); return uniforms

    # Map some other SombreroMain class as a shader of this one
    def MapPipelineTexture(self, Name, width, height, depth):
        size = (width, height)
        uniforms = [Uniform("sampler2D", Name, None), Uniform("vec2", f"{Name}_resolution", size)]
        texture = self.SombreroContext.OpenGL_Context.texture(size, depth, dtype = "f4")
        texture.write(np.zeros((width, height, depth), dtype = np.float32))  # Start empty (GL context no guarantee to be clean)
        self.WritableTextures[Name] = texture
        self.PendingUniforms += uniforms
        self.AssignContent(dict(
            loader = "GlobalPipeline_texture",
            Name=Name, texture=texture, size=size
        ))
        return uniforms

    # # GL objects

    # Create one texture attached to some FBO. Depth = 4 -> RGBA
    def CreateTextureFBO(self, width, height, depth = 4) -> list:
        texture = self.SombreroContext.OpenGL_Context.texture((int(width), int(height)), depth)
        fbo = self.SombreroContext.OpenGL_Context.framebuffer(color_attachments = [texture])
        return [texture, fbo]

    # Get the uniform if exists, enforce tuple if isn't tuple or int and assign the value
    def SetUniform(self, Name, value):
        if (not isinstance(value, float)) and (not isinstance(value, int)): value = tuple(value)
        self.program.get(Name, DummyElement()).value = value
        return Name
    
    # Write to some PipelineTexture that was mapped, recursively to every child
    def WritePipelineTexture(self, Name, data):
        self.WritableTextures.get(Name, DummyElement()).write(np.array(data, dtype = np.float32).tobytes())
        for child in self.ChildrenOfSombreroMain(): child.WritePipelineTexture(Name, data)
    
    # Write uniform values on the list of pending uniforms
    def SolvePendingUniforms(self):
        for item in self.PendingUniforms:
            if item.value is not None: self.SetUniform(item.Name, item.value)
        self.PendingUniforms = []

    # Pipe a global GlobalPipeline
    def PipePipeline(self, GlobalPipeline):
        for Name, value in GlobalPipeline.items(): self.SetUniform(Name, value)
    
    # # Load

    def _create_assing_texture_fbo_render_buffer(self):
        self.texture, self.fbo = self.CreateTextureFBO(
            width  = self.SombreroContext.width  * self.SombreroContext.ssaa,
            height = self.SombreroContext.height * self.SombreroContext.ssaa)

    # Load shader from this class's SombreroConstructor
    def Finish(self, _give_up_if_any_errors = False):
        dpfx = "[SombreroMain.Finish]"
        self.__ever_finished = True

        # Default constructor is Fullscreen if not set
        if self.constructor is None: self.constructor = FullScreenConstructor(self)

        # Add IOs to the frag shader based on constructor specifications
        self.constructor.TreatFragmentShader(self.Shader)
        FragmentShader = self.Shader.Build()

        # The FBO and texture so we can use on parent shaders, master shader doesn't require since it haves window fbo
        if not self.MasterShader:
            self._create_assing_texture_fbo_render_buffer()
            
        try:
            self.program = self.SombreroContext.OpenGL_Context.program(
                vertex_shader = self.constructor.VertexShader,
                geometry_shader = self.constructor.GeometryShader,
                fragment_shader = FragmentShader,
            )
            self.SolvePendingUniforms()
            if self.MasterShader: self.SombreroContext.framerate.clear()

        except moderngl.error.Error as e:
            self.Reset()
            for pretty in pretty_lines_counter(FragmentShader): print(pretty)
            logging.error(f"{dpfx} {e}")
            if _give_up_if_any_errors: sys.exit()
            self.constructor = FullScreenConstructor(self)
            self.Shader = SombreroShader()
            self.ShaderMacros.Load(self.PackageInterface.SombreroDir/"MissingTexture.glsl")
            self.Finish(_give_up_if_any_errors = True)

    # Get render instructions, do this every render because stuff like piano roll needs
    # their draw instructions to be updated
    def GetVAO(self):
        if instructions := self.constructor.vao():
            self.vao = self.SombreroContext.OpenGL_Context.vertex_array(self.program, instructions, skip_errors = True)

    # # Render

    # Next iteration, also render
    def Next(self, CustomGlobalPipeline = {}):
        if not self.__ever_finished: self.Finish()
        if CustomGlobalPipeline is None: CustomGlobalPipeline = {}

        # # Update GlobalPipeline

        # Get current window "state"
        self.GlobalPipeline["mResolution"] = (self.SombreroContext.width * self.SombreroContext.ssaa, self.SombreroContext.height * self.SombreroContext.ssaa)
        self.GlobalPipeline["mFlip"] = -1 if self.flip else 1

        # Render related
        self.GlobalPipeline["quality"] = self.SombreroContext.quality

        # Time related
        self.GlobalPipeline["mFrame"] = self.GlobalPipeline.get("mFrame", 0) + self.SombreroContext.time_speed
        self.GlobalPipeline["mTime"] = self.GlobalPipeline["mFrame"] / self.SombreroContext.fps

        # GUI related
        self.GlobalPipeline["mIsGuiVisible"] = self.SombreroContext.show_gui
        self.GlobalPipeline["mIsDebugMode"] = self.SombreroContext.debug_mode

        # 2D
        self.GlobalPipeline["m2DIsDraggingMode"] = 1 in self.SombreroContext.mouse_buttons_pressed
        self.GlobalPipeline["m2DIsDragging"] = self.SombreroContext.camera2d.is_dragging
        self.GlobalPipeline["m2DRotation"] = self.SombreroContext.camera2d.rotation.value
        self.GlobalPipeline["m2DZoom"] = self.SombreroContext.camera2d.zoom.value
        self.GlobalPipeline["m2DDrag"] = self.SombreroContext.camera2d.drag.value

        # 3D
        self.GlobalPipeline["m3DCameraBase"] = self.SombreroContext.camera3d.standard_base.reshape(-1)
        self.GlobalPipeline["m3DCameraPointing"] = self.SombreroContext.camera3d.pointing
        self.GlobalPipeline["m3DCameraPos"] = self.SombreroContext.camera3d.position.value
        self.GlobalPipeline["m3DRoll"] = self.SombreroContext.camera3d.roll.value
        self.GlobalPipeline["m3DFOV"] = self.SombreroContext.camera3d.fov.value
        
        # Keys
        self.GlobalPipeline["mMouse1"] = 1 in self.SombreroContext.mouse_buttons_pressed
        self.GlobalPipeline["mMouse2"] = 2 in self.SombreroContext.mouse_buttons_pressed
        self.GlobalPipeline["mMouse3"] = 3 in self.SombreroContext.mouse_buttons_pressed
        self.GlobalPipeline["mKeyShift"] = self.SombreroContext.shift_pressed
        self.GlobalPipeline["mKeyCtrl"] = self.SombreroContext.ctrl_pressed
        self.GlobalPipeline["mKeyAlt"] = self.SombreroContext.alt_pressed

        # Merge the two dictionaries
        for key, value in CustomGlobalPipeline.values():
            self.GlobalPipeline[key] = value

        # Render, update window
        self._render()
        self.window.UpdateWindow()

    # Internal function for rendering (some stuff needs to be called like getting next image of video)
    def _render(self):

        # VAO, constructor
        self.constructor.next()
        self.GetVAO()

        # Pipe to self
        self.PipePipeline(self.GlobalPipeline)

        # Pipe the GlobalPipeline to child shaders and render them
        for child in self.ChildrenOfSombreroMain():
            child.PipePipeline(self.GlobalPipeline)
            child.GlobalPipeline = self.GlobalPipeline
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
            try: self.program[item["Name"]] = index
            except KeyError: pass  # Texture was mapped but isn't used

        # Render the content
        # self.vao.render(mode = moderngl.TRIANGLE_STRIP)

        self.SombreroContext.OpenGL_Context.enable_only(moderngl.NOTHING)
        
        if isinstance(self.constructor, PianoRollConstructor):
            self.SombreroContext.OpenGL_Context.enable_only(moderngl.BLEND)

        if nvert := self.constructor.num_vertices:
            self.vao.render(mode = moderngl.POINTS, vertices = nvert)
        
        # Draw UI then reset composite mode to NOTHING because imgui changes that
        if self.MasterShader and (not self.SombreroContext.window_headless) and (self.SombreroContext.show_gui):
            self.window.render_ui()
            
        self.SombreroContext.OpenGL_Context.enable_only(moderngl.NOTHING)

    # Read contents from window FBO, chose one
    def read(self): return self.window.window.fbo.read()
    def stdout(self, target): target.write(self.read())

    @property # FBO size for screenshots
    def FBO_Size(self): return self.window.window.fbo.size
    
    # Generator for iterating on child SombreroMain instances
    def ChildrenOfSombreroMain(self):
        for index, item in self.contents.items():
            if item["loader"] == "ChildSombreroMain":
                yield item["SombreroMain"]
    
    # Return list of used variables in program
    def get_used_variables(self) -> list:
        info = [k for k in self.program._members.keys()]

        # Call for every shader as texture loaders
        for child in self.ChildrenOfSombreroMain():
            for key in child.get_used_variables(): info.append(key)

        # Remove duplicates
        return list(set(info))
    
    def ResetTimeZero(self): self.GlobalPipeline["mFrame"] = 0

    def Reset(self):
        if self.SombreroContext.piano_roll is not None:
            self.SombreroContext.piano_roll.synth.reset()
            del self.SombreroContext.piano_roll; self.SombreroContext.piano_roll = None
        self.SombreroContext.camera2d.reset()
        self.SombreroContext.camera3d.reset()
        for child in self.ChildrenOfSombreroMain(): child.Reset(); del child
        with suppress(AttributeError): self.program.release()
        with suppress(AttributeError): self.texture.release()
        with suppress(AttributeError): self.fbo.release()
        with suppress(AttributeError): self.vao.release()
        if isinstance(self.constructor, FullScreenConstructor):
            self.constructor.once_returned_vao = False
        self.contents = {}
